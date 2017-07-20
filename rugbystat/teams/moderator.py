from moderation import moderation
from moderation.moderator import GenericModerator

from .models import Team, Person, PersonSeason


class NoNotifyModerator(GenericModerator):
    notify_moderator = False
    notify_user = False


class TeamModerator(NoNotifyModerator):
    pass


class PersonModerator(NoNotifyModerator):
    pass


class PersonSeasonModerator(NoNotifyModerator):
    pass


moderation.register(Team, TeamModerator)
moderation.register(Person, PersonModerator)
moderation.register(PersonSeason, PersonSeasonModerator)
