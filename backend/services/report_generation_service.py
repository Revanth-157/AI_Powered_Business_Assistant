"""
Autonomous Report Generation Service

Orchestrates report generation, formatting, scheduling, and distribution.
Main service layer for Prompt 8 autonomous report generation system.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from report_generation import (
    ReportGenerator,
    ReportFormatter,
    ReportScheduler,
    ReportDistributor,
    ReportType,
    OutputFormat,
    ScheduleFrequency,
    DistributionChannel,
)


class ReportGenerationService:
    """Main service for autonomous report generation and management."""
    
    def __init__(self):
        """Initialize report generation service."""
        self.generator = ReportGenerator()
        self.formatter = ReportFormatter()
        self.scheduler = ReportScheduler()
        self.distributor = ReportDistributor()
        
        # Create default schedules
        self.scheduler.create_default_schedules()
    
    def generate_executive_report(
        self,
        insights_data: Dict[str, Any],
        period_days: int = 7,
        include_forecast: bool = True
    ) -> Dict[str, Any]:
        """Generate executive summary report."""
        report = self.generator.generate_executive_summary_report(
            insights_data,
            period_days=period_days,
            include_forecast=include_forecast
        )
        
        return {
            'report_id': report.metadata.report_id,
            'title': report.title,
            'status': report.metadata.status.value,
            'key_metrics': report.key_metrics,
            'section_count': len(report.sections),
            'recommendation_count': len(report.recommendations),
            'data': report.to_dict(),
        }
    
    def generate_detailed_report(
        self,
        insights_data: Dict[str, Any],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate detailed analysis report."""
        report = self.generator.generate_detailed_analysis_report(
            insights_data,
            focus_areas=focus_areas
        )
        
        return {
            'report_id': report.metadata.report_id,
            'title': report.title,
            'status': report.metadata.status.value,
            'key_metrics': report.key_metrics,
            'data': report.to_dict(),
        }
    
    def generate_opportunity_report(
        self,
        opportunities: List[Dict[str, Any]],
        insights_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate opportunities review report."""
        report = self.generator.generate_opportunity_review_report(
            opportunities,
            insights_data=insights_data
        )
        
        return {
            'report_id': report.metadata.report_id,
            'title': report.title,
            'status': report.metadata.status.value,
            'key_metrics': report.key_metrics,
            'data': report.to_dict(),
        }
    
    def generate_kpi_report(
        self,
        kpi_data: Dict[str, Any],
        include_targets: bool = True
    ) -> Dict[str, Any]:
        """Generate KPI scorecard report."""
        report = self.generator.generate_kpi_scorecard_report(
            kpi_data,
            include_targets=include_targets
        )
        
        return {
            'report_id': report.metadata.report_id,
            'title': report.title,
            'status': report.metadata.status.value,
            'key_metrics': report.key_metrics,
            'data': report.to_dict(),
        }
    
    def format_report(
        self,
        report_id: str,
        output_format: str
    ) -> Optional[str]:
        """Format a generated report to specified output format."""
        report = self.generator.get_report_by_id(report_id)
        if not report:
            return None
        
        try:
            output_fmt = OutputFormat(output_format)
            return self.formatter.format(report, output_fmt)
        except ValueError:
            return None
    
    def get_visualization_specs(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get visualization specifications for a report."""
        report = self.generator.get_report_by_id(report_id)
        if not report:
            return None
        
        return self.formatter.generate_visualization_specs(report)
    
    def create_report_schedule(
        self,
        report_type: str,
        frequency: str,
        recipients: List[str],
        output_formats: Optional[List[str]] = None,
        enabled: bool = True,
        run_time: str = "08:00"
    ) -> Dict[str, Any]:
        """Create a new report schedule."""
        try:
            freq = ScheduleFrequency(frequency)
        except ValueError:
            freq = ScheduleFrequency.DAILY
        
        schedule = self.scheduler.create_schedule(
            report_type=report_type,
            frequency=freq,
            recipients=recipients,
            output_formats=output_formats,
            enabled=enabled,
            run_time=run_time
        )
        
        return {
            'schedule_id': schedule.schedule_id,
            'report_type': schedule.report_type,
            'frequency': schedule.frequency.value,
            'enabled': schedule.enabled,
            'next_run': schedule.next_run.isoformat(),
            'recipients': schedule.recipients,
        }
    
    def get_all_schedules(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get all report schedules."""
        schedules = self.scheduler.get_all_schedules(enabled_only=enabled_only)
        
        return [
            {
                'schedule_id': s.schedule_id,
                'report_type': s.report_type,
                'frequency': s.frequency.value,
                'enabled': s.enabled,
                'next_run': s.next_run.isoformat(),
                'last_run': s.last_run.isoformat() if s.last_run else None,
                'recipients': s.recipients,
            }
            for s in schedules
        ]
    
    def get_due_schedules(self) -> List[Dict[str, Any]]:
        """Get schedules that are due to run."""
        schedules = self.scheduler.get_due_schedules()
        
        return [
            {
                'schedule_id': s.schedule_id,
                'report_type': s.report_type,
                'frequency': s.frequency.value,
                'next_run': s.next_run.isoformat(),
                'recipients': s.recipients,
            }
            for s in schedules
        ]
    
    def execute_schedule(
        self,
        schedule_id: str,
        insights_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Execute a scheduled report."""
        schedule = self.scheduler.get_schedule(schedule_id)
        if not schedule:
            return None
        
        try:
            # Generate report based on type
            if schedule.report_type == 'executive_summary':
                report = self.generator.generate_executive_summary_report(insights_data)
            elif schedule.report_type == 'detailed_analysis':
                report = self.generator.generate_detailed_analysis_report(insights_data)
            elif schedule.report_type == 'kpi_scorecard':
                report = self.generator.generate_kpi_scorecard_report(insights_data.get('kpi_dashboard', {}))
            else:
                report = self.generator.generate_executive_summary_report(insights_data)
            
            # Distribute report
            channels = [DistributionChannel.EMAIL, DistributionChannel.FILE_STORAGE]
            recipients = {
                'email': schedule.recipients
            }
            
            distribution_records = self.distributor.distribute_report(
                report.metadata.report_id,
                report.title,
                report.to_dict(),
                channels,
                recipients=recipients,
                formats=schedule.output_formats
            )
            
            # Record execution
            execution = self.scheduler.record_execution(
                schedule_id,
                status='completed',
                report_id=report.metadata.report_id,
                output_files=[d.distribution_id for d in distribution_records]
            )
            
            return {
                'execution_id': execution.execution_id,
                'report_id': report.metadata.report_id,
                'status': execution.status,
                'distributions': len(distribution_records),
                'executed_at': execution.executed_at.isoformat(),
            }
        
        except Exception as e:
            execution = self.scheduler.record_execution(
                schedule_id,
                status='failed',
                error_message=str(e)
            )
            return {
                'execution_id': execution.execution_id,
                'status': 'failed',
                'error': str(e),
            }
    
    def distribute_report(
        self,
        report_id: str,
        report_data: Dict[str, Any],
        channels: List[str],
        recipients: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """Distribute a report to specified channels."""
        try:
            channel_list = [DistributionChannel(c) for c in channels]
        except ValueError:
            return []
        
        distribution_records = self.distributor.distribute_report(
            report_id,
            report_data.get('title', 'Report'),
            report_data,
            channels=channel_list,
            recipients=recipients or {}
        )
        
        return [
            {
                'distribution_id': d.distribution_id,
                'channel': d.channel.value,
                'status': d.status,
                'sent_at': d.sent_at.isoformat(),
                'recipients': d.recipients,
            }
            for d in distribution_records
        ]
    
    def get_distribution_history(
        self,
        report_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get report distribution history."""
        records = self.distributor.get_distribution_history(
            report_id=report_id,
            limit=limit
        )
        
        return [
            {
                'distribution_id': d.distribution_id,
                'report_id': d.report_id,
                'channel': d.channel.value,
                'status': d.status,
                'sent_at': d.sent_at.isoformat(),
                'recipients': d.recipients,
            }
            for d in records
        ]
    
    def get_report_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get report generation history."""
        reports = self.generator.get_report_history(limit=limit)
        
        return [
            {
                'report_id': r.metadata.report_id,
                'title': r.title,
                'type': r.metadata.report_type.value,
                'generated_at': r.metadata.generated_at.isoformat(),
                'status': r.metadata.status.value,
                'key_metrics': r.key_metrics,
            }
            for r in reports
        ]
    
    def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        schedules = self.scheduler.get_all_schedules()
        executions = self.scheduler.execution_history
        
        return {
            'total_schedules': len(schedules),
            'enabled_schedules': len([s for s in schedules if s.enabled]),
            'total_executions': len(executions),
            'successful_executions': len([e for e in executions if e.status == 'completed']),
            'failed_executions': len([e for e in executions if e.status == 'failed']),
            'schedules': self.get_all_schedules(),
        }
    
    def get_distribution_statistics(self) -> Dict[str, Any]:
        """Get distribution statistics."""
        return self.distributor.get_distribution_statistics()
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export all service configuration."""
        return {
            'export_date': datetime.now().isoformat(),
            'schedules': self.scheduler.export_schedule_config(),
            'distribution_channels': {
                'webhooks': self.distributor.webhook_distributor.get_registered_webhooks(),
            },
            'statistics': {
                'scheduler': self.get_scheduler_statistics(),
                'distributor': self.get_distribution_statistics(),
            }
        }
