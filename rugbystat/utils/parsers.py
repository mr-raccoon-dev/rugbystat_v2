import datetime
import functools as ft
import itertools as it
import logging
import operator
import re
from difflib import SequenceMatcher as SM

from django.contrib.messages import success
from django.contrib import messages
from django.db import connection
from django.db.models import Q
from fuzzywuzzy import fuzz

from matches.models import Season, Tournament, Match as MatchModel
from teams.models import City, Person, PersonSeason, Team, TeamSeason, GroupSeason

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
    teams_re = re.compile(r"(\S+ \S+) (?P<seasons>\((\d+,*\s*)+\)),*\s*")

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
    expr = r"<li>(.+) \(([^-]*)-*([^-]*)\)(.*)"
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
    parser = SimpleTable.build(data).find_teams(season).find_matches()
    print(vars(parser))
    team_seasons = parser.build_teams(season.pk, group.pk)
    return team_seasons, parser.matches


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
        """Return Django model instance."""
        if season:
            cls = TeamSeason
            kwargs = {'season_id': season}
        if group:
            cls = GroupSeason
            kwargs = {'group_id': group}
        return cls(**vars(self), **kwargs)


class Match:

    model = MatchModel

    def __init__(self, *args, **kwargs):
        self.home_id = kwargs.get('home_id')
        self.away_id = kwargs.get('away_id')
        self.home_score = kwargs.get('home_score')
        self.away_score = kwargs.get('away_score')
        self.tourn_season_id = kwargs.get('tourn_season_id')

    def __repr__(self):
        return (
            f"Match(home_id={self.home_id}, "
            + f"away_id={self.away_id}, "
            + f"home_score={self.home_score}, "
            + f"away_score={self.away_score}, "
            + f"tourn_season_id={self.tourn_season_id})"
        )

    def __str__(self):
        return f"{self.away_id} v {self.away_id} - {self.home_score}:{self.away_score}"

    def __eq__(self, other):
        return (
            self.home_id == other.away_id
            and self.away_id == other.home_id
            and self.home_score == other.away_score
            and self.away_score == other.home_score
        )

    @classmethod
    def from_string(cls, home, away, string):
        home_score, away_score = None, None
        if ':' in string:
            home_score, away_score = string.split(':')
        if string in {'поб', 'побед', 'выиг'}:
            home_score, away_score = 1, 0
        if string in {'пор', 'пораж', 'проиг'}:
            home_score, away_score = 0, 1
        if string in {'нич', 'ничья'}:
            home_score, away_score = 1, 1
        return cls(
            home_id=home.team_id,
            away_id=away.team_id,
            home_score=home_score,
            away_score=away_score,
        )

    def save(self):
        if self.tourn_season_id:
            instance = self.model(**{
                key: getattr(self, key)
                for key in ("home_id", "away_id", "home_score", "away_score", "tourn_season_id")
            })
            return instance.save()


EDGE = "xxxxx"
EDGE_RU = "ххххх"


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

    def __init__(self, lines, legs=1):
        self._lines = lines
        self._teams = []
        self._matches = {}
        self._column_marks = []
        self._column_parts = []
        self._season_id = None
        self.legs = legs

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

    def find_teams(self, season=None):
        year = season.date_start.year if season else None
        self._season_id = season.id
        for line, marks in zip(self._lines, self._column_marks):
            if marks:
                line = line[:marks[0]]
            place, team = line.split(".", 1)
            team = team.strip().replace('"', '')
            team_id = find_team_name_match(team.strip(), year)
            row = TableRow(place=place.strip(), name=team, team_id=team_id)
            self._teams.append(row)
        return self

    def find_matches(self):
        total = len(self._teams)
        for team_idx in range(0, total):
            start_idx = 0
            parts = self._column_parts[team_idx]
            if parts[team_idx] in {EDGE, EDGE_RU}:
                self._parse_matches(total, parts, team_idx)
                start_idx = total
            # parse games part: ['12 1 1', 'xxx-xx', '25']
            self._parse_standings(parts, start_idx, team_idx)
        return self

    def _parse_matches(self, num_teams, match_parts, team_idx):
        # TODO: parse two_legged tables
        for match_idx in range(team_idx, num_teams):
            match_str = match_parts[match_idx]
            if match_str and match_str not in {EDGE, EDGE_RU}:
                match = Match.from_string(
                    self._teams[team_idx],
                    self._teams[match_idx],
                    match_str,
                )
                match.tourn_season_id = self._season_id
                self._matches[(team_idx, match_idx)] = match

    def _parse_standings(self, match_parts, start_idx, team_idx):
        first = match_parts[start_idx]
        to_parse = match_parts[start_idx+1:]
        team = self._teams[team_idx]
        if ' ' in first:
            w_d_l = first.split()
            w_d_l.extend(to_parse)
            to_parse = w_d_l
        else:
            to_parse.insert(0, first)

        if len(to_parse) >= 3:
            team.wins = to_parse[0]
            team.draws = to_parse[1]
            team.losses = to_parse[2]
            to_parse = to_parse[3:]

        if len(to_parse) == 2:
            team.score = to_parse[0]
            team.points = to_parse[1]
        if len(to_parse) == 1:
            team.points = to_parse[0]

    def build_teams(self, season=None, group=None):
        return [t.build(season, group) for t in self._teams]

    @property
    def matches(self):
        # two_legged = True
        # to_return = []
        # for (i, j), match in self._matches.items():
        #     if j > i:
        #         if match == self._matches.get((j, i)):
        #             two_legged = False
        #         to_return.append(match)
        #     if two_legged:
        #         if i > j:
        #             to_return.append(match)
        return self._matches.values()


def find_team_name_match(search_name, year=None):
    """
    Find the most suitable instance by base name and given names.
    """
    condition = ""
    if year:
        condition += f" AND year <= {year} AND disband_year >= {year}"

    base_name = """SELECT tt.tagobject_ptr_id as team_id, t.name as team_name, c.name as city, tt.year, tt.disband_year
  FROM teams_team tt
 INNER JOIN teams_tagobject t ON t.id=tt.tagobject_ptr_id
  LEFT OUTER JOIN teams_city c on c.id=tt.city_id
 WHERE t.name LIKE '{name}%'{condition}"""

    with connection.cursor() as cursor:
        sqlite_ver = "strftime('%Y', from_day) as year, strftime('%Y', to_day) as disband_year"
        extract_years = "extract(year from from_day) as year, extract(year from to_day) as disband_year"
        if cursor.db.client_class.executable_name == 'sqlite3':
            extract_years = sqlite_ver

        given_names = (
            f"SELECT team_id, teams_teamname.name as team_name, c.name as city, {extract_years}" + """
  FROM teams_teamname
 INNER JOIN teams_team tt ON tt.tagobject_ptr_id=teams_teamname.team_id
 INNER JOIN teams_city c ON c.id = tt.city_id
 WHERE teams_teamname.name LIKE '{name}%'{condition}""")

        sql = f"""SELECT * FROM (
 {base_name}
  UNION ALL
 {given_names}
) as u;"""
        sql = sql.format(name=search_name[:3], condition=condition)
        cursor.execute(sql)
        res = cursor.fetchall()

    ratios = [
        fuzz.token_set_ratio(search_name, f"{obj[1]} {obj[2]}")
        for obj in res
    ]

    if ratios and max(ratios) > 60:
        found = res[ratios.index(max(ratios))][0]
    else:
        found = None
    return found
