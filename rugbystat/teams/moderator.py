from moderation import moderation
from moderation.moderator import GenericModerator
from moderation.admin import ModerationAdmin

from .models import Team, TeamSeason, Person, PersonSeason


class NoModerationAdmin(ModerationAdmin):
    admin_integration_enabled = False


class NoNotifyModerator(GenericModerator):
    notify_moderator = False
    notify_user = False


class TeamModerator(NoNotifyModerator):
    pass


class TeamSeasonModerator(NoNotifyModerator):
    pass


class PersonModerator(NoNotifyModerator):
    pass


class PersonSeasonModerator(NoNotifyModerator):
    pass


moderation.register(Team, TeamModerator)
moderation.register(TeamSeason, TeamSeasonModerator)
moderation.register(Person, PersonModerator)
moderation.register(PersonSeason, PersonSeasonModerator)
