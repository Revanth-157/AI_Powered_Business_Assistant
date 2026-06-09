"""
Report Distributor Module

Distributes generated reports via multiple channels:
- Email
- API webhooks
- File storage (local/S3)
- Dashboard integration
- Slack/Teams notifications
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class DistributionChannel(str, Enum):
    """Distribution channels for reports."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    FILE_STORAGE = "file_storage"
    DASHBOARD = "dashboard"
    SLACK = "slack"
    TEAMS = "teams"
    API = "api"
    DATABASE = "database"


@dataclass
class DistributionRecord:
    """Record of a report distribution."""
    distribution_id: str
    report_id: str
    channel: DistributionChannel
    recipients: List[str]
    sent_at: datetime
    status: str  # "pending", "sent", "failed"
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class EmailDistributor:
    """Email distribution handler."""
    
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        """Initialize email distributor."""
        self.smtp_config = smtp_config or {
            'host': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'from_address': 'reports@company.com',
        }
    
    def send_report(
        self,
        recipients: List[str],
        report_title: str,
        report_content: str,
        report_format: str = "html",
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send report via email."""
        # In production, this would use smtplib or similar
        # For now, return success (mock implementation)
        return True
    
    def get_delivery_status(self, email: str) -> Dict[str, Any]:
        """Get email delivery status."""
        return {
            'email': email,
            'delivered': True,
            'delivered_at': datetime.now().isoformat(),
            'open_count': 1,
        }


class WebhookDistributor:
    """Webhook distribution handler."""
    
    def __init__(self):
        """Initialize webhook distributor."""
        self.registered_webhooks: Dict[str, Dict[str, Any]] = {}
    
    def register_webhook(
        self,
        webhook_id: str,
        url: str,
        events: List[str],
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Register a webhook endpoint."""
        webhook = {
            'webhook_id': webhook_id,
            'url': url,
            'events': events,
            'headers': headers or {},
            'enabled': enabled,
            'created_at': datetime.now().isoformat(),
            'last_triggered': None,
        }
        self.registered_webhooks[webhook_id] = webhook
        return webhook
    
    def trigger_webhook(
        self,
        webhook_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Trigger a webhook."""
        webhook = self.registered_webhooks.get(webhook_id)
        if not webhook or not webhook['enabled']:
            return False
        
        if event_type not in webhook['events']:
            return False
        
        # In production, this would use requests library
        # For now, return success (mock implementation)
        webhook['last_triggered'] = datetime.now().isoformat()
        return True
    
    def get_registered_webhooks(self) -> List[Dict[str, Any]]:
        """Get all registered webhooks."""
        return list(self.registered_webhooks.values())


class FileStorageDistributor:
    """File storage distribution handler."""
    
    def __init__(self, storage_path: str = "reports/"):
        """Initialize file storage distributor."""
        self.storage_path = storage_path
        self.stored_files: Dict[str, str] = {}
    
    def store_report(
        self,
        report_id: str,
        content: str,
        format: str,
        directory: Optional[str] = None
    ) -> str:
        """Store report to file system."""
        path = directory or self.storage_path
        filename = f"{report_id}.{format}"
        filepath = f"{path}{filename}"
        
        # In production, this would write to actual file system
        self.stored_files[filepath] = content
        return filepath
    
    def retrieve_report(self, filepath: str) -> Optional[str]:
        """Retrieve stored report."""
        return self.stored_files.get(filepath)
    
    def list_stored_reports(self, pattern: Optional[str] = None) -> List[str]:
        """List stored reports."""
        files = list(self.stored_files.keys())
        if pattern:
            files = [f for f in files if pattern in f]
        return sorted(files)


class SlackDistributor:
    """Slack distribution handler."""
    
    def __init__(self, webhook_url: Optional[str] = None, bot_token: Optional[str] = None):
        """Initialize Slack distributor."""
        self.webhook_url = webhook_url
        self.bot_token = bot_token
    
    def send_message(
        self,
        channel: str,
        message: str,
        blocks: Optional[List[Dict]] = None
    ) -> bool:
        """Send message to Slack channel."""
        # In production, use slack_sdk
        return True
    
    def send_report_summary(
        self,
        channel: str,
        report_title: str,
        key_metrics: Dict[str, Any],
        recommendations: List[Dict]
    ) -> bool:
        """Send report summary to Slack."""
        message = f"📊 *{report_title}*\n\n"
        
        # Add metrics
        for key, value in list(key_metrics.items())[:5]:
            message += f"• {key}: {value}\n"
        
        # Add top recommendations
        if recommendations:
            message += f"\n🎯 *Top Recommendations:*\n"
            for i, rec in enumerate(recommendations[:3], 1):
                message += f"{i}. {rec.get('title', 'Recommendation')}\n"
        
        return self.send_message(channel, message)


class TeamsDistributor:
    """Microsoft Teams distribution handler."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """Initialize Teams distributor."""
        self.webhook_url = webhook_url
    
    def send_message(self, message: str) -> bool:
        """Send message to Teams."""
        # In production, use teams webhook or SDK
        return True
    
    def send_adaptive_card(self, card: Dict[str, Any]) -> bool:
        """Send adaptive card to Teams."""
        return True


class DashboardDistributor:
    """Dashboard integration handler."""
    
    def __init__(self):
        """Initialize dashboard distributor."""
        self.dashboard_widgets: Dict[str, Dict[str, Any]] = {}
    
    def publish_to_dashboard(
        self,
        report_id: str,
        dashboard_id: str,
        widget_data: Dict[str, Any]
    ) -> bool:
        """Publish report data to dashboard."""
        widget_key = f"{dashboard_id}_{report_id}"
        self.dashboard_widgets[widget_key] = {
            'report_id': report_id,
            'dashboard_id': dashboard_id,
            'data': widget_data,
            'published_at': datetime.now().isoformat(),
        }
        return True
    
    def get_dashboard_data(self, dashboard_id: str) -> List[Dict[str, Any]]:
        """Get all data for a dashboard."""
        return [
            w for w in self.dashboard_widgets.values()
            if w['dashboard_id'] == dashboard_id
        ]


class ReportDistributor:
    """Main report distribution orchestrator."""
    
    def __init__(self):
        """Initialize distributor."""
        self.email_distributor = EmailDistributor()
        self.webhook_distributor = WebhookDistributor()
        self.file_distributor = FileStorageDistributor()
        self.slack_distributor = SlackDistributor()
        self.teams_distributor = TeamsDistributor()
        self.dashboard_distributor = DashboardDistributor()
        
        self.distribution_records: List[DistributionRecord] = []
        self.distribution_counter = 0
    
    def distribute_report(
        self,
        report_id: str,
        report_title: str,
        report_content: Dict[str, Any],
        channels: List[DistributionChannel],
        recipients: Optional[Dict[str, List[str]]] = None,
        formats: Optional[List[str]] = None
    ) -> List[DistributionRecord]:
        """Distribute report to multiple channels."""
        distribution_records = []
        recipients = recipients or {}
        formats = formats or ["json", "html"]
        
        for channel in channels:
            if channel == DistributionChannel.EMAIL:
                record = self._distribute_email(
                    report_id,
                    report_title,
                    report_content,
                    recipients.get('email', []),
                    formats
                )
                distribution_records.append(record)
            
            elif channel == DistributionChannel.WEBHOOK:
                record = self._distribute_webhook(
                    report_id,
                    report_title,
                    report_content
                )
                distribution_records.append(record)
            
            elif channel == DistributionChannel.FILE_STORAGE:
                record = self._distribute_file_storage(
                    report_id,
                    report_title,
                    report_content,
                    formats
                )
                distribution_records.append(record)
            
            elif channel == DistributionChannel.SLACK:
                record = self._distribute_slack(
                    report_id,
                    report_title,
                    report_content,
                    recipients.get('slack_channels', [])
                )
                distribution_records.append(record)
            
            elif channel == DistributionChannel.DASHBOARD:
                record = self._distribute_dashboard(
                    report_id,
                    report_title,
                    report_content
                )
                distribution_records.append(record)
        
        return distribution_records
    
    def _distribute_email(
        self,
        report_id: str,
        report_title: str,
        report_content: Dict,
        recipients: List[str],
        formats: List[str]
    ) -> DistributionRecord:
        """Distribute via email."""
        self.distribution_counter += 1
        distribution_id = f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.distribution_counter:04d}"
        
        status = "sent" if self.email_distributor.send_report(
            recipients,
            report_title,
            json.dumps(report_content),
            report_format=formats[0] if formats else "json"
        ) else "failed"
        
        record = DistributionRecord(
            distribution_id=distribution_id,
            report_id=report_id,
            channel=DistributionChannel.EMAIL,
            recipients=recipients,
            sent_at=datetime.now(),
            status=status,
        )
        
        self.distribution_records.append(record)
        return record
    
    def _distribute_webhook(
        self,
        report_id: str,
        report_title: str,
        report_content: Dict
    ) -> DistributionRecord:
        """Distribute via webhook."""
        self.distribution_counter += 1
        distribution_id = f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.distribution_counter:04d}"
        
        # Trigger all registered webhooks
        webhooks = self.webhook_distributor.get_registered_webhooks()
        triggered_count = 0
        
        for webhook in webhooks:
            if 'report_generated' in webhook['events']:
                if self.webhook_distributor.trigger_webhook(
                    webhook['webhook_id'],
                    'report_generated',
                    {'report_id': report_id, 'title': report_title}
                ):
                    triggered_count += 1
        
        record = DistributionRecord(
            distribution_id=distribution_id,
            report_id=report_id,
            channel=DistributionChannel.WEBHOOK,
            recipients=[],
            sent_at=datetime.now(),
            status="sent" if triggered_count > 0 else "pending",
            metadata={'webhooks_triggered': triggered_count}
        )
        
        self.distribution_records.append(record)
        return record
    
    def _distribute_file_storage(
        self,
        report_id: str,
        report_title: str,
        report_content: Dict,
        formats: List[str]
    ) -> DistributionRecord:
        """Distribute to file storage."""
        self.distribution_counter += 1
        distribution_id = f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.distribution_counter:04d}"
        
        stored_paths = []
        for format in formats:
            path = self.file_distributor.store_report(
                report_id,
                json.dumps(report_content),
                format
            )
            stored_paths.append(path)
        
        record = DistributionRecord(
            distribution_id=distribution_id,
            report_id=report_id,
            channel=DistributionChannel.FILE_STORAGE,
            recipients=[],
            sent_at=datetime.now(),
            status="sent",
            metadata={'stored_paths': stored_paths}
        )
        
        self.distribution_records.append(record)
        return record
    
    def _distribute_slack(
        self,
        report_id: str,
        report_title: str,
        report_content: Dict,
        channels: List[str]
    ) -> DistributionRecord:
        """Distribute to Slack."""
        self.distribution_counter += 1
        distribution_id = f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.distribution_counter:04d}"
        
        sent_count = 0
        for channel in channels:
            if self.slack_distributor.send_report_summary(
                channel,
                report_title,
                report_content.get('key_metrics', {}),
                report_content.get('recommendations', [])
            ):
                sent_count += 1
        
        record = DistributionRecord(
            distribution_id=distribution_id,
            report_id=report_id,
            channel=DistributionChannel.SLACK,
            recipients=channels,
            sent_at=datetime.now(),
            status="sent" if sent_count > 0 else "failed",
            metadata={'sent_channels': sent_count}
        )
        
        self.distribution_records.append(record)
        return record
    
    def _distribute_dashboard(
        self,
        report_id: str,
        report_title: str,
        report_content: Dict
    ) -> DistributionRecord:
        """Distribute to dashboard."""
        self.distribution_counter += 1
        distribution_id = f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.distribution_counter:04d}"
        
        dashboard_id = "main_dashboard"
        widget_data = {
            'title': report_title,
            'metrics': report_content.get('key_metrics', {}),
            'sections': len(report_content.get('sections', [])),
        }
        
        status_ok = self.dashboard_distributor.publish_to_dashboard(
            report_id,
            dashboard_id,
            widget_data
        )
        
        record = DistributionRecord(
            distribution_id=distribution_id,
            report_id=report_id,
            channel=DistributionChannel.DASHBOARD,
            recipients=[],
            sent_at=datetime.now(),
            status="sent" if status_ok else "failed",
        )
        
        self.distribution_records.append(record)
        return record
    
    def get_distribution_history(
        self,
        report_id: Optional[str] = None,
        limit: int = 50
    ) -> List[DistributionRecord]:
        """Get distribution history."""
        records = self.distribution_records
        
        if report_id:
            records = [r for r in records if r.report_id == report_id]
        
        return sorted(records, key=lambda r: r.sent_at, reverse=True)[:limit]
    
    def get_distribution_statistics(self) -> Dict[str, Any]:
        """Get distribution statistics."""
        total = len(self.distribution_records)
        sent = len([r for r in self.distribution_records if r.status == 'sent'])
        failed = len([r for r in self.distribution_records if r.status == 'failed'])
        
        by_channel = {}
        for record in self.distribution_records:
            channel = record.channel.value
            if channel not in by_channel:
                by_channel[channel] = {'total': 0, 'sent': 0, 'failed': 0}
            by_channel[channel]['total'] += 1
            if record.status == 'sent':
                by_channel[channel]['sent'] += 1
            else:
                by_channel[channel]['failed'] += 1
        
        return {
            'total_distributions': total,
            'sent': sent,
            'failed': failed,
            'success_rate': sent / total if total > 0 else 0.0,
            'by_channel': by_channel,
        }
