from moderation import moderation
from moderation.moderator import GenericModerator

from .models import Season, Match


class NoNotifyModerator(GenericModerator):
    notify_moderator = False
    notify_user = False


class SeasonModerator(NoNotifyModerator):
    pass


class MatchModerator(NoNotifyModerator):
    pass


moderation.register(Season, SeasonModerator)
moderation.register(Match, MatchModerator)
