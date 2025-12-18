from __future__ import annotations

from .base import BaseRepository


class SystemConfigRepo(BaseRepository):
    collection_name = "system_config"


class KeywordConfigRepo(BaseRepository):
    collection_name = "keyword_config"


class GeoFiltersRepo(BaseRepository):
    collection_name = "geo_filters"


class SchedulerConfigRepo(BaseRepository):
    collection_name = "scheduler_config"


class ClientRulesRepo(BaseRepository):
    collection_name = "client_rules"


class JobRulesRepo(BaseRepository):
    collection_name = "job_rules"


class RiskRulesRepo(BaseRepository):
    collection_name = "risk_rules"


class JobsRawRepo(BaseRepository):
    collection_name = "jobs_raw"


class JobsFilteredRepo(BaseRepository):
    collection_name = "jobs_filtered"


class JobScoresRepo(BaseRepository):
    collection_name = "job_scores"


class PortfoliosRepo(BaseRepository):
    collection_name = "portfolios"


class PromptTemplatesRepo(BaseRepository):
    collection_name = "prompt_templates"


class AISettingsRepo(BaseRepository):
    collection_name = "ai_settings"


class ProposalsRepo(BaseRepository):
    collection_name = "proposals"


class NotificationsRepo(BaseRepository):
    collection_name = "notifications"


class AuditLogsRepo(BaseRepository):
    collection_name = "audit_logs"


class FeedStatusRepo(BaseRepository):
    collection_name = "feed_status"


