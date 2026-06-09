"""
Report Generation Package

Autonomous report generator with scheduling and distribution capabilities.
Supports multiple output formats and distribution channels.
"""

from .report_generator import (
    ReportGenerator,
    ExecutiveReport,
    ReportType,
    ReportFrequency,
    ReportStatus,
    ReportMetadata,
    ReportSection,
)

from .report_formatter import (
    ReportFormatter,
    OutputFormat,
)

from .report_scheduler import (
    ReportScheduler,
    ScheduleConfig,
    ScheduleFrequency,
    ScheduledReport,
)

from .report_distributor import (
    ReportDistributor,
    DistributionChannel,
    DistributionRecord,
    EmailDistributor,
    WebhookDistributor,
    FileStorageDistributor,
    SlackDistributor,
    TeamsDistributor,
    DashboardDistributor,
)

__all__ = [
    # Generator
    'ReportGenerator',
    'ExecutiveReport',
    'ReportType',
    'ReportFrequency',
    'ReportStatus',
    'ReportMetadata',
    'ReportSection',
    # Formatter
    'ReportFormatter',
    'OutputFormat',
    # Scheduler
    'ReportScheduler',
    'ScheduleConfig',
    'ScheduleFrequency',
    'ScheduledReport',
    # Distributor
    'ReportDistributor',
    'DistributionChannel',
    'DistributionRecord',
    'EmailDistributor',
    'WebhookDistributor',
    'FileStorageDistributor',
    'SlackDistributor',
    'TeamsDistributor',
    'DashboardDistributor',
]
