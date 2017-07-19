from moderation import moderation
from moderation.db import ModeratedModel

from .models import Season, Match


class NoNotifyModerator(ModeratedModel):
    notify_moderator = False
    notify_user = False


class SeasonModerator(NoNotifyModerator):
    pass


class MatchModerator(NoNotifyModerator):
    pass


moderation.register(Season, SeasonModerator)
moderation.register(Match, MatchModerator)
