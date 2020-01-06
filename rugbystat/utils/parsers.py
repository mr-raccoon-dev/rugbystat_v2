import copy
import datetime
import functools as ft
import itertools as it
import logging
import operator
import re
from collections import namedtuple
from difflib import SequenceMatcher as SM

from django.contrib.messages import success
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Q, Value
from django.db.models.functions import Concat
from fuzzywuzzy import fuzz

from matches.models import Group, Season, Tournament
from teams.models import City, Person, PersonSeason, Team, TeamName, TeamSeason, GroupSeason

logger = logging.getLogger("django.request")
POSITIONS = {
    "15": PersonSeason.FB,
    "14-11": PersonSeason.BACK,
    "10": PersonSeason.FH,
    "9": PersonSeason.SH,
    "6-8": PersonSeason.BACKROW,
    "4-5": PersonSeason.LOCK,
    "1-3": PersonSeason.FIRST_ROW,
    "14": PersonSeason.WINGER,
    "13": PersonSeason.CENTER,
    "12": PersonSeason.CENTER,
    "12-13": PersonSeason.CENTER,
    "11": PersonSeason.WINGER,
    "9-10": PersonSeason.HALF,
    "8": PersonSeason.BACKROW,
    "7": PersonSeason.BACKROW,
    "6": PersonSeason.BACKROW,
    "5": PersonSeason.LOCK,
    "4": PersonSeason.LOCK,
    "4/5": PersonSeason.LOCK,
    "3": PersonSeason.PROP,
    "2": PersonSeason.HOOKER,
    "1": PersonSeason.PROP,
    "1/3": PersonSeason.PROP,
    "1-8": PersonSeason.FORWARD,
    "15-9": PersonSeason.BACK,
}
MONTHS_MAP = {
    "январ": "01",
    "феврал": "02",
    "март": "03",
    "апрел": "04",
    "мая": "05",
    "мае": "05",
    "июн": "06",
    "июл": "07",
    "август": "08",
    "сентябр": "09",
    "октябр": "10",
    "ноябр": "11",
    "декабр": "12",
}

TEAM_NAME = re.compile("[а-я]+\s+", re.I)


def parse_rosters(request, data):
    input_ = data["input"].replace("\r\n", " ").replace(" / ", ";")
    positions = input_.strip().split(";")
    for position in positions:
        # split number from names
        esc = r"(\d{1,2}-*\d{0,2}).(.*)"
        try:
            print("Checking {}".format(position))
            number, players = re.findall(esc, position)[0]
        except ValueError:
            msg = "Couldn't import data: {}".format(position)
            print(msg)
            logger.warning(msg)
        else:
            role = POSITIONS.get(number, PersonSeason.PLAYER)
            for player in players.split(","):
                # find person
                try:
                    first_name, name = player.split()
                except ValueError:
                    msg = "Couldn't split: {}".format(player)
                    print(msg)
                    logger.warning(msg)

                    name = player

                persons = Person.objects.filter(name=name)
                # what if there're multiple?
                print("Finding best match from {}".format(persons))

                person = find_best_match(persons, name, first_name)
                print("Found {}".format(person))

                # get_or_create PersonSeason for number
                obj, created = PersonSeason.objects.get_or_create(
                    role=role,
                    person=person,
                    season_id=data["season"],
                    team_id=data["team"],
                    year=data["year"],
                )
                if created:
                    success(request, "Created {}".format(obj))
                else:
                    success(request, "Found {}".format(obj))


def parse_alphabet(request, data):
    importer = LineImporter()
    importer.run(data["input"].split('\r\n'))


class LineImporter:
    pattern = re.compile(r"(?P<name>(?:[А-Я][а-я.]*\s*){1,3})(?P<year>\(\d+\) )?— (?P<teams>(([A-Яа-я ]+) (?P<seasons>\((\d+,*\s*)+\)),*\s*)+)(.*)")
    teams_re = re.compile("(\S+ \S+) (?P<seasons>\((\d+,*\s*)+\)),*\s*")

    def __init__(self, *args, **kwargs):
        self.p = Person()
        self.m2m = []
        self.seasons = {
            "1933": Season.objects.get(name="Товарищеские матчи 1933"),
            "1934": Season.objects.get(name="Товарищеские матчи 1934"),
            "1935": Season.objects.get(name="Чемпионат Москвы 1935 (о)"),
            "1936": Season.objects.get(name="Кубок СССР 1936"),
            "1937": Season.objects.get(name="Матч городов 1937"),
            "1938": Season.objects.get(name="Чемпионат СССР 1938"),
            "1939": Season.objects.get(name="Чемпионат СССР 1939"),
            "1940": Season.objects.get(name="Чемпионат Москвы 1940"),
            "1946": Season.objects.get(name="Чемпионат Москвы 1946"),
            "1947": Season.objects.get(name="Матч городов 1947"),
            "1949": Season.objects.get(name="Матч городов 1949"),
        }

    def restart(self):
        self.p = Person()
        self.m2m = []
    
    def run(self, inpt):
        for line in inpt:
            self.process_line(line)
            PersonSeason.objects.bulk_create(self.m2m)
            self.restart()
    
    def process_line(self, line):
        matches = self.pattern.findall(line)
        name, year, teams, last, last_name, seasons, last_season, occupation = matches[0]
        self.create_person(name.strip(), year, occupation)
        self.parse_seasons(teams, last, last_name, seasons, last_season)

    def create_person(self, name, year, occupation):
        if " " in name:
            name = name.replace('.', ' ').strip().split(' ')
            self.p.name = name[0]
            self.p.first_name = name[1]
            if len(name) > 2:
                self.p.middle_name = name[2]
        else:
            self.p.name = name

        if year:
            self.p.year_birth = year[1:5]
        
        if occupation:
            self.p.story = occupation
        
        self.p.save()

    def parse_seasons(self, teams, last, last_name, last_seasons, last_season):
        if last == teams:
            self.create_seasons(last_name, last_seasons)
        else:
            for team, seasons, _ in self.parse_teams(teams):
                self.create_seasons(team, seasons)

    def parse_teams(self, teams):
        return self.teams_re.findall(teams)

    def create_seasons(self, team, seasons):
        # '(1936)'
        # '(1937, 1938)'
        team_instance = self.get_team_instance(team)
        if not team_instance:
            logger.warning(f"No team found for {team}")
        for season in seasons[1:-1].split(','):
            self.m2m.append(
                PersonSeason(
                    person=self.p,
                    season_id=self.seasons[season.strip()].pk,
                    team_id=team_instance.id,
                    year=season.strip(),
                )
            )

    def get_team_instance(self, name):
        qs = Team.objects.filter(year__lt=1950)
        for element in name.split():
            qs = reduce_qs(qs, element.strip())
        return qs.first()


def reduce_qs(qs, search_term): 
    queries = [
        Q(**{lookup: search_term})
        for lookup in (
            'name__icontains',
            'short_name__icontains',
            'names__name__icontains',
            'city__name__istartswith',
        )
    ]
    return qs.filter(ft.reduce(operator.or_, queries))


def find_best_match(queryset, name, first_name, all=False):
    """
    Find the most suitable instance by SequenceMatcher from queryset.

    If None found, try to look for all objects.
    If again None found - create one.
    """
    ratios = [
        SM(None, str(obj), "{} {}".format(first_name, name)).ratio() for obj in queryset
    ]

    if ratios and max(ratios) > 0.6:
        found = queryset[ratios.index(max(ratios))]
    elif all:
        found = Person.objects.create(name=name, first_name=first_name)
    else:
        queryset = Person.objects.all()
        found = find_best_match(queryset, name, first_name, all=True)
    return found


def parse_teams(data):
    previous_team = None
    for line in data.split("\n"):
        if len(line) < 4:
            previous_team.save()
            break
        if line[:4] == "<li>":
            if not previous_team:
                previous_team = init_team(line)
            else:
                previous_team.save()
                previous_team = init_team(line)
        else:
            if previous_team:
                previous_team.story += line


def init_date(prefix_year):
    try:
        year = int(prefix_year.strip().split(" ")[-1])
        prefix = prefix_year[: prefix_year.find(str(year))]
    except Exception:
        prefix = prefix_year
        year = None
    return prefix, year


def init_team(line):
    expr = "<li>(.+) \(([^-]*)-*([^-]*)\)(.*)"
    team_and_city, year_create, year_disband, story = re.findall(expr, line)[0]
    city = team_and_city.split(" ")[-1]
    name = team_and_city[: team_and_city.find(city)].strip().strip("<b>")

    city_instance, _ = City.objects.get_or_create(name=city)

    prefix_create, create = init_date(year_create)
    prefix_disband, disband = init_date(year_disband)

    team = Team(
        name=name,
        story=story,
        city=city_instance,
        year=create or None,
        year_prefix=prefix_create,
        disband_year=disband or None,
        disband_year_prefix=prefix_disband,
    )
    return team


def parse_season(data, request):
    YEAR = re.compile(
        r"""(^\D*)    # all but digits - tournament name
                      ([\d/-]{4,9}) # '1975' or '1975/77' or '1999/2001'
                      *$            # 0 or once""",
        re.X,
    )

    season = Season()
    first, *rest = data.split("\n")
    # first line denotes title
    title, year = re.match(YEAR, first.strip()).group(1, 2)
    season.name = title.strip()
    season.year = int(year)
    tourns = Tournament.objects.filter(name__icontains=season.name)

    if tourns.count() == 1:
        season.tourn = tourns.first()
    else:
        if not tourns:
            msg = "No tournaments found"
        else:
            ratios = [SM(None, tourn.name, title).ratio() for tourn in tourns]
            max_tourn = tourns[ratios.index(max(ratios))]
            season.tourn = max_tourn
            msg = "Multiple tournaments found for this title. "
            msg = msg + "We suggest: {}".format(max_tourn.name)
        messages.add_message(request, messages.INFO, msg)

    for line in rest:
        if line.strip():
            date_start, date_end = find_dates(line, year)
            if date_start and date_end:
                season.date_start = date_start
                season.date_end = date_end
                break
        else:
            season.date_start = datetime.date(season.year, 1, 1)
            season.date_end = datetime.date(season.year, 12, 31)

    season.story = "\n".join(rest)
    return season


def find_dates(txt, year):
    """
    Parse "с 5 февраля по 10 мая" to datetime objects
    """
    months = r"({})".format("|".join(MONTHS_MAP.keys()))
    esc1 = r" (\d+(?= {}))".format(months)  # (с ... по ...)
    esc2 = r"(\d+-\d+(?= {}))".format(months)  # (1-10 ...)
    esc3 = r"[в|в конце|в начале] {}".format(months)  # в октябре...

    patterns = [esc1, esc2, esc3]
    dates = [re.findall(pattern, txt) for pattern in patterns]
    if tuple(filter(bool, dates)):
        # try the first found pattern
        try:
            date_start, date_end = dates[0]
            day, month = date_start
            date_start = datetime.datetime.strptime(
                "{}/{}/{}".format(day, MONTHS_MAP[month], year), "%d/%m/%Y"
            )
            day, month = date_end
            date_end = datetime.datetime.strptime(
                "{}/{}/{}".format(day, MONTHS_MAP[month], year), "%d/%m/%Y"
            )
        except (IndexError, ValueError):
            # either ('12-15', 'мая') or 'октябр'
            try:
                days, month = dates[1][0]
                day_start, day_end = days.split("-")
                date_start = datetime.datetime.strptime(
                    "{}/{}/{}".format(day_start, MONTHS_MAP[month], year), "%d/%m/%Y"
                )
                date_end = datetime.datetime.strptime(
                    "{}/{}/{}".format(day_end, MONTHS_MAP[month], year), "%d/%m/%Y"
                )
            except (IndexError, ValueError):
                # 'октябр'
                month = dates[2][0]
                date_start = datetime.datetime.strptime(
                    "{}/{}/{}".format("05", MONTHS_MAP[month], year), "%d/%m/%Y"
                )
                date_end = datetime.datetime.strptime(
                    "{}/{}/{}".format("25", MONTHS_MAP[month], year), "%d/%m/%Y"
                )
        return date_start, date_end
    else:
        return None, None


def parse_table(data, season, group):
    team_seasons, matches = {}, {}

    parser = SimpleTable.build(data).find_columns().find_teams(season.date_start.year)
    print(vars(parser))
    team_seasons = parser.build_teams(season.pk, group.pk)
    return team_seasons, matches


class TableRow:
    def __init__(self, **kwargs):
        self.place = kwargs.get('place', '')
        self.name = kwargs.get('name')
        self.wins = kwargs.get('w')
        self.draws = kwargs.get('d')
        self.losses = kwargs.get('l')
        self.score = kwargs.get('score', '')
        self.points = kwargs.get('points')
        self.team_id = kwargs.get('team_id')

    def __repr__(self):
        return f"TableRow(place={self.place}, name={self.name}, team_id={self.team_id})"
    
    def __str__(self):
        return f"{self.place}. {self.name} ({self.team_id})"

    def build(self, season=None, group=None):
        if season:
            cls = TeamSeason
            kwargs = {'season_id': season}
        if group:
            cls = GroupSeason
            kwargs = {'group_id': group}
        return cls(**vars(self), **kwargs)


class SimpleTable:
    """
    line may be any representation in table:

    1. Динамо                     xxxxx  22:6    поб   13:3   20:0    поб
    5. "Спартак" Ленинград      6:18   0:6    0:3    0:8   xxxxx  20:8   1 0 4  26-43  2    
    1. "СТАКЛЕС" Каунас            6  0  2  164:72   12 *
    1. Крылья Советов Москва
    . Скра
    2. Политехник Киев
    3. МАИ Москва (?)
    .. РАФ Елгава

    """

    def __init__(self, lines):
        self._lines = lines
        self._teams = []
        self._column_marks = []
        self._column_parts = []

    @classmethod
    def build(cls, txt):
        _list = []
        for line in txt.split("\n"):
            if line.startswith("-") or not line.strip():
                continue
            _list.append(line.strip())
        return cls(_list).find_columns()

    def find_columns(self):
        """Every line must be approx the same width, we need to define columns."""
        lens = []
        for line in self._lines:
            marks = self._mark_columns(line)
            self._column_marks.append(marks)
            lens.append(len(marks))

        longest_marks = self._column_marks[lens.index(max(lens))]
        for line in self._lines:
            self._column_parts.append(self._split_line(line, longest_marks))
        return self

    @staticmethod
    def _mark_columns(line):
        previous_idx = -100
        bounds = []
        for idx, letter in enumerate(line):
            if letter == ' ':
                if previous_idx + 1 == idx:
                    # consecutive whitespace found
                    if bounds and bounds[-1] == previous_idx:
                        bounds[-1] += 1
                    else:
                        bounds.append(idx)
                previous_idx = idx
        return bounds

    @staticmethod
    def _split_line(line, marks):
        if marks:
            start, end = it.tee(marks)
            next(end)
            return [line[i:j].strip() for i, j in it.zip_longest(start, end)]

    def find_teams(self, year=None):
        for line, marks in zip(self._lines, self._column_marks):
            if marks:
                line = line[:marks[0]]
            place, team = line.split(".", 1)
            team = team.strip().replace('"', '')
            team_id = find_team_name_match(team.strip(), year)
            row = TableRow(place=place.strip(), name=team, team_id=team_id)
            self._teams.append(row)
        return self

    def build_teams(self, season=None, group=None):
        return [t.build(season, group) for t in self._teams]


def find_team_name_match(search_name, year=None):
    """
    Find the most suitable instance by base name and given names.
    """
    sql = """
SELECT tt.tagobject_ptr_id as team_id, t.name as base_name, tn.name as given, c.name as city
  FROM teams_team tt
 INNER JOIN teams_tagobject t ON t.id=tt.tagobject_ptr_id
  LEFT OUTER JOIN teams_teamname tn ON tt.tagobject_ptr_id=tn.team_id
  LEFT OUTER JOIN teams_city c on c.id=tt.city_id
 WHERE (base_name LIKE '{lookup}%' OR given LIKE '{lookup}%');"""
    
    if year:
        condition = f" AND tt.year <= {year} AND tt.disband_year >= {year};"
        sql = sql[:-1] + condition

    with connection.cursor() as cursor:
        cursor.execute(sql.format(lookup=search_name[:3]))
        res = cursor.fetchall()
        print(res)

    ratios = [
        fuzz.token_set_ratio(search_name, f"{obj[2] or obj[1]} {obj[3]}")
        for obj in res
    ]

    if ratios and max(ratios) > 60:
        found = res[ratios.index(max(ratios))][0]
    else:
        found = None
    return found
