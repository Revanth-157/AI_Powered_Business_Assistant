"""
Report Scheduler Module

Manages scheduled report generation with cron-like scheduling capabilities.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class ScheduleFrequency(str, Enum):
    """Report scheduling frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


@dataclass
class ScheduleConfig:
    """Configuration for scheduled report generation."""
    schedule_id: str
    report_type: str
    frequency: ScheduleFrequency
    enabled: bool = True
    next_run: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    run_time: str = "08:00"  # HH:MM format
    recipients: List[str] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=lambda: ["json", "html"])
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledReport:
    """Record of a scheduled report execution."""
    execution_id: str
    schedule_id: str
    report_type: str
    executed_at: datetime
    status: str  # "pending", "in_progress", "completed", "failed"
    duration_seconds: float = 0.0
    report_id: Optional[str] = None
    error_message: Optional[str] = None
    output_files: List[str] = field(default_factory=list)


class ReportScheduler:
    """Manages report scheduling and execution."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.execution_history: List[ScheduledReport] = []
        self.execution_counter = 0
    
    def create_schedule(
        self,
        report_type: str,
        frequency: ScheduleFrequency,
        recipients: List[str],
        output_formats: Optional[List[str]] = None,
        enabled: bool = True,
        run_time: str = "08:00"
    ) -> ScheduleConfig:
        """Create a new report schedule."""
        schedule_id = f"SCH-{datetime.now().strftime('%Y%m%d')}-{len(self.schedules)+1:04d}"
        
        schedule = ScheduleConfig(
            schedule_id=schedule_id,
            report_type=report_type,
            frequency=frequency,
            enabled=enabled,
            next_run=self._calculate_next_run(frequency, run_time),
            run_time=run_time,
            recipients=recipients,
            output_formats=output_formats or ["json", "html"],
        )
        
        self.schedules[schedule_id] = schedule
        return schedule
    
    def update_schedule(
        self,
        schedule_id: str,
        **kwargs
    ) -> Optional[ScheduleConfig]:
        """Update an existing schedule."""
        if schedule_id not in self.schedules:
            return None
        
        schedule = self.schedules[schedule_id]
        
        for key, value in kwargs.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        return schedule
    
    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = True
            return True
        return False
    
    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule."""
        if schedule_id in self.schedules:
            self.schedules[schedule_id].enabled = False
            return True
        return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            return True
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleConfig]:
        """Get a schedule by ID."""
        return self.schedules.get(schedule_id)
    
    def get_all_schedules(self, enabled_only: bool = False) -> List[ScheduleConfig]:
        """Get all schedules."""
        schedules = list(self.schedules.values())
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        return sorted(schedules, key=lambda s: s.next_run)
    
    def get_due_schedules(self) -> List[ScheduleConfig]:
        """Get schedules that are due to run."""
        now = datetime.now()
        due_schedules = []
        
        for schedule in self.schedules.values():
            if schedule.enabled and schedule.next_run <= now:
                due_schedules.append(schedule)
        
        return sorted(due_schedules, key=lambda s: s.next_run)
    
    def record_execution(
        self,
        schedule_id: str,
        status: str = "completed",
        report_id: Optional[str] = None,
        error_message: Optional[str] = None,
        output_files: Optional[List[str]] = None
    ) -> ScheduledReport:
        """Record report execution."""
        self.execution_counter += 1
        execution_id = f"EXE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.execution_counter:04d}"
        
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        execution = ScheduledReport(
            execution_id=execution_id,
            schedule_id=schedule_id,
            report_type=schedule.report_type,
            executed_at=datetime.now(),
            status=status,
            report_id=report_id,
            error_message=error_message,
            output_files=output_files or []
        )
        
        self.execution_history.append(execution)
        
        # Update schedule's last_run and next_run
        schedule.last_run = execution.executed_at
        schedule.next_run = self._calculate_next_run(
            schedule.frequency,
            schedule.run_time,
            from_date=execution.executed_at
        )
        
        return execution
    
    def get_execution_history(
        self,
        schedule_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ScheduledReport]:
        """Get execution history."""
        history = self.execution_history
        
        if schedule_id:
            history = [e for e in history if e.schedule_id == schedule_id]
        
        return sorted(history, key=lambda e: e.executed_at, reverse=True)[:limit]
    
    def get_schedule_statistics(self, schedule_id: str) -> Dict[str, Any]:
        """Get statistics for a schedule."""
        executions = [e for e in self.execution_history if e.schedule_id == schedule_id]
        
        if not executions:
            return {
                'total_executions': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0,
                'average_duration': 0.0,
                'last_execution': None,
            }
        
        successful = [e for e in executions if e.status == 'completed']
        failed = [e for e in executions if e.status == 'failed']
        avg_duration = sum(e.duration_seconds for e in executions) / len(executions) if executions else 0
        
        return {
            'total_executions': len(executions),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(executions) if executions else 0.0,
            'average_duration': avg_duration,
            'last_execution': executions[0].executed_at if executions else None,
            'last_status': executions[0].status if executions else None,
        }
    
    def create_default_schedules(self) -> List[ScheduleConfig]:
        """Create default report schedules."""
        default_schedules = [
            {
                'report_type': 'executive_summary',
                'frequency': ScheduleFrequency.DAILY,
                'recipients': ['executive@company.com'],
                'run_time': '08:00',
            },
            {
                'report_type': 'detailed_analysis',
                'frequency': ScheduleFrequency.WEEKLY,
                'recipients': ['analysis-team@company.com'],
                'run_time': '09:00',
            },
            {
                'report_type': 'opportunity_review',
                'frequency': ScheduleFrequency.WEEKLY,
                'recipients': ['strategy@company.com'],
                'run_time': '10:00',
            },
            {
                'report_type': 'kpi_scorecard',
                'frequency': ScheduleFrequency.DAILY,
                'recipients': ['operations@company.com'],
                'run_time': '18:00',
            },
        ]
        
        created_schedules = []
        for config in default_schedules:
            schedule = self.create_schedule(
                report_type=config['report_type'],
                frequency=config['frequency'],
                recipients=config['recipients'],
                run_time=config['run_time'],
            )
            created_schedules.append(schedule)
        
        return created_schedules
    
    def export_schedule_config(self) -> Dict[str, Any]:
        """Export all schedule configurations."""
        return {
            'export_date': datetime.now().isoformat(),
            'total_schedules': len(self.schedules),
            'schedules': [
                {
                    'schedule_id': s.schedule_id,
                    'report_type': s.report_type,
                    'frequency': s.frequency.value,
                    'enabled': s.enabled,
                    'run_time': s.run_time,
                    'recipients': s.recipients,
                    'output_formats': s.output_formats,
                    'next_run': s.next_run.isoformat(),
                    'last_run': s.last_run.isoformat() if s.last_run else None,
                }
                for s in self.schedules.values()
            ]
        }
    
    def import_schedule_config(self, config: Dict[str, Any]) -> int:
        """Import schedule configurations."""
        imported_count = 0
        
        for schedule_data in config.get('schedules', []):
            try:
                schedule = ScheduleConfig(
                    schedule_id=schedule_data['schedule_id'],
                    report_type=schedule_data['report_type'],
                    frequency=ScheduleFrequency(schedule_data['frequency']),
                    enabled=schedule_data.get('enabled', True),
                    run_time=schedule_data.get('run_time', '08:00'),
                    recipients=schedule_data.get('recipients', []),
                    output_formats=schedule_data.get('output_formats', ['json', 'html']),
                )
                self.schedules[schedule.schedule_id] = schedule
                imported_count += 1
            except Exception as e:
                print(f"Error importing schedule: {e}")
        
        return imported_count
    
    @staticmethod
    def _calculate_next_run(
        frequency: ScheduleFrequency,
        run_time: str,
        from_date: Optional[datetime] = None
    ) -> datetime:
        """Calculate next run time based on frequency."""
        if from_date is None:
            from_date = datetime.now()
        
        hour, minute = map(int, run_time.split(':'))
        
        if frequency == ScheduleFrequency.DAILY:
            next_run = from_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= from_date:
                next_run += timedelta(days=1)
            return next_run
        
        elif frequency == ScheduleFrequency.WEEKLY:
            next_run = from_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= from_date:
                next_run += timedelta(days=1)
            # Move to next Monday if not already
            days_to_monday = (7 - next_run.weekday()) % 7
            if days_to_monday == 0 and next_run <= from_date:
                days_to_monday = 7
            next_run += timedelta(days=days_to_monday)
            return next_run
        
        elif frequency == ScheduleFrequency.MONTHLY:
            next_run = from_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run.day == from_date.day and next_run <= from_date:
                # Move to next month, same day
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=next_run.month + 1)
            return next_run
        
        elif frequency == ScheduleFrequency.QUARTERLY:
            next_run = from_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Move to next quarter (every 3 months)
            months_to_add = 3 - ((next_run.month - 1) % 3)
            if months_to_add == 0:
                months_to_add = 3
            next_month = next_run.month + months_to_add
            next_year = next_run.year
            while next_month > 12:
                next_month -= 12
                next_year += 1
            next_run = next_run.replace(year=next_year, month=next_month)
            return next_run
        
        else:  # CUSTOM
            return from_date + timedelta(days=1)
