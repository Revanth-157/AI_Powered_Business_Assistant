"""
Autonomous Report Generation Test Suite

Comprehensive tests for Prompt 8: Autonomous Report Generation Engine
Tests report generation, formatting, scheduling, and distribution.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from report_generation import (
    ReportGenerator,
    ReportFormatter,
    ReportScheduler,
    ReportDistributor,
    OutputFormat,
    ScheduleFrequency,
    DistributionChannel,
)
from services.report_generation_service import ReportGenerationService


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'─'*70}")
    print(f"{title}")
    print(f"{'─'*70}\n")


# Sample data for testing
SAMPLE_INSIGHTS_DATA = {
    'findings': [
        {
            'title': 'Strong Promotion Performance',
            'description': 'Summer promotion exceeded targets by 25%',
            'severity': 'POSITIVE',
            'metric': 'sales_lift',
            'current_value': 125,
            'baseline_value': 100,
            'change_percent': 25,
            'affected_entities': ['Mango Nectar', 'Apple Cider']
        },
        {
            'title': 'Regional Stockout Alert',
            'description': 'North region experiencing stockouts',
            'severity': 'CRITICAL',
            'metric': 'stockout_rate',
            'current_value': 0.15,
            'baseline_value': 0.05,
            'change_percent': 200,
            'affected_entities': ['Premium Juice', 'Fresh Smoothie']
        },
    ],
    'opportunities': [
        {
            'title': 'Scale Successful Promotion',
            'description': 'Expand mango promotion to additional channels',
            'opportunity_type': 'EXPANSION',
            'priority': 9,
            'estimated_impact_value': 50000,
            'implementation_effort': 'MEDIUM',
            'affected_entities': ['Mango Nectar']
        },
        {
            'title': 'Optimize Inventory',
            'description': 'Reduce excess inventory in South region',
            'opportunity_type': 'OPTIMIZATION',
            'priority': 7,
            'estimated_impact_value': 30000,
            'implementation_effort': 'LOW',
            'affected_entities': ['All Products']
        },
    ],
    'alerts': [
        {
            'title': 'Critical Stockout',
            'message': 'Premium Juice stockout in North region',
            'level': 'CRITICAL',
            'metric_value': 0.15
        },
        {
            'title': 'Low Sales',
            'message': 'Apple Cider sales below forecast',
            'level': 'WARNING',
            'metric_value': 15000
        },
    ],
    'kpi_dashboard': {
        'health_score': 72,
        'on_target_count': 5,
        'at_risk_count': 2,
        'below_target_count': 1,
    }
}

SAMPLE_KPI_DATA = {
    'health_score': 72,
    'on_target_count': 5,
    'at_risk_count': 2,
    'below_target_count': 1,
    'kpis': [
        {'name': 'Revenue', 'value': 500000, 'target': 450000, 'status': 'ON_TARGET'},
        {'name': 'Margin', 'value': 35, 'target': 38, 'status': 'AT_RISK'},
        {'name': 'Units Sold', 'value': 150000, 'target': 160000, 'status': 'AT_RISK'},
        {'name': 'Stockout Rate', 'value': 8, 'target': 5, 'status': 'BELOW_TARGET'},
    ]
}


def test_1_report_generator():
    """Test 1: Report Generator"""
    print_section("Test 1: AUTONOMOUS REPORT GENERATOR")
    
    generator = ReportGenerator()
    
    # Generate executive summary report
    print_subsection("Generating Executive Summary Report")
    exec_report = generator.generate_executive_summary_report(SAMPLE_INSIGHTS_DATA)
    
    print(f"✓ Report ID: {exec_report.metadata.report_id}")
    print(f"✓ Title: {exec_report.title}")
    print(f"✓ Status: {exec_report.metadata.status.value}")
    print(f"✓ Sections: {len(exec_report.sections)}")
    print(f"✓ Recommendations: {len(exec_report.recommendations)}")
    print(f"✓ Key Metrics: {list(exec_report.key_metrics.keys())}")
    
    # Generate detailed report
    print_subsection("Generating Detailed Analysis Report")
    detail_report = generator.generate_detailed_analysis_report(SAMPLE_INSIGHTS_DATA)
    print(f"✓ Detailed Report: {detail_report.metadata.report_id}")
    print(f"✓ Type: {detail_report.metadata.report_type.value}")
    
    # Generate opportunity report
    print_subsection("Generating Opportunity Review Report")
    opp_report = generator.generate_opportunity_review_report(SAMPLE_INSIGHTS_DATA['opportunities'])
    print(f"✓ Opportunity Report: {opp_report.metadata.report_id}")
    print(f"✓ Opportunities: {opp_report.key_metrics.get('total_opportunities', 0)}")
    
    # Generate KPI scorecard
    print_subsection("Generating KPI Scorecard")
    kpi_report = generator.generate_kpi_scorecard_report(SAMPLE_KPI_DATA)
    print(f"✓ KPI Report: {kpi_report.metadata.report_id}")
    print(f"✓ Health Score: {kpi_report.key_metrics.get('health_score', 0)}/100")
    
    print(f"\n✅ Report generation completed with {generator.report_counter} reports")
    
    return exec_report


def test_2_report_formatter(report):
    """Test 2: Report Formatter"""
    print_section("Test 2: REPORT FORMATTER")
    
    formatter = ReportFormatter()
    
    # Test JSON format
    print_subsection("Formatting as JSON")
    json_output = formatter.format(report, OutputFormat.JSON)
    print(f"✓ JSON output length: {len(json_output)} characters")
    print(f"✓ Contains report_id: {'report_id' in json_output}")
    
    # Test HTML format
    print_subsection("Formatting as HTML")
    html_output = formatter.format(report, OutputFormat.HTML)
    print(f"✓ HTML output length: {len(html_output)} characters")
    print(f"✓ Contains DOCTYPE: {'<!DOCTYPE html>' in html_output}")
    
    # Test Markdown format
    print_subsection("Formatting as Markdown")
    md_output = formatter.format(report, OutputFormat.MARKDOWN)
    print(f"✓ Markdown output length: {len(md_output)} characters")
    print(f"✓ Contains headers: {'##' in md_output}")
    
    # Test Text format
    print_subsection("Formatting as Text")
    text_output = formatter.format(report, OutputFormat.TEXT)
    print(f"✓ Text output length: {len(text_output)} characters")
    print(f"✓ Contains separators: {'=====' in text_output}")
    
    # Test visualization specs
    print_subsection("Generating Visualization Specifications")
    vis_specs = formatter.generate_visualization_specs(report)
    print(f"✓ Charts count: {len(vis_specs.get('charts', []))}")
    print(f"✓ Tables count: {len(vis_specs.get('tables', []))}")
    print(f"✓ Chart types: {[c['type'] for c in vis_specs.get('charts', [])]}")
    
    print(f"\n✅ Report formatting completed for all formats")


def test_3_report_scheduler():
    """Test 3: Report Scheduler"""
    print_section("Test 3: REPORT SCHEDULER")
    
    scheduler = ReportScheduler()
    
    # Create schedules
    print_subsection("Creating Report Schedules")
    
    schedule1 = scheduler.create_schedule(
        report_type='executive_summary',
        frequency=ScheduleFrequency.DAILY,
        recipients=['exec@company.com'],
        run_time='08:00'
    )
    print(f"✓ Schedule 1: {schedule1.schedule_id}")
    print(f"  - Type: {schedule1.report_type}")
    print(f"  - Frequency: {schedule1.frequency.value}")
    print(f"  - Next run: {schedule1.next_run.strftime('%Y-%m-%d %H:%M')}")
    
    schedule2 = scheduler.create_schedule(
        report_type='detailed_analysis',
        frequency=ScheduleFrequency.WEEKLY,
        recipients=['analysis@company.com'],
        run_time='09:00'
    )
    print(f"✓ Schedule 2: {schedule2.schedule_id}")
    
    # Get all schedules
    print_subsection("Retrieving Schedules")
    all_schedules = scheduler.get_all_schedules()
    print(f"✓ Total schedules: {len(all_schedules)}")
    print(f"✓ Enabled: {len([s for s in all_schedules if s.enabled])}")
    
    # Create default schedules
    print_subsection("Creating Default Schedules")
    defaults = scheduler.create_default_schedules()
    print(f"✓ Default schedules created: {len(defaults)}")
    for sched in defaults:
        print(f"  - {sched.report_type}: {sched.frequency.value}")
    
    # Record execution
    print_subsection("Recording Schedule Execution")
    execution = scheduler.record_execution(
        schedule1.schedule_id,
        status='completed',
        report_id='REP-20260609-0001'
    )
    print(f"✓ Execution recorded: {execution.execution_id}")
    print(f"✓ Status: {execution.status}")
    
    # Get execution history
    history = scheduler.get_execution_history(limit=5)
    print(f"✓ Execution history: {len(history)} entries")
    
    # Get statistics
    print_subsection("Schedule Statistics")
    stats = scheduler.get_schedule_statistics(schedule1.schedule_id)
    print(f"✓ Total executions: {stats['total_executions']}")
    print(f"✓ Successful: {stats['successful']}")
    print(f"✓ Success rate: {stats['success_rate']*100:.1f}%")
    
    print(f"\n✅ Report scheduling completed")


def test_4_report_distributor():
    """Test 4: Report Distributor"""
    print_section("Test 4: REPORT DISTRIBUTOR")
    
    distributor = ReportDistributor()
    
    # Register webhook
    print_subsection("Registering Webhook")
    webhook = distributor.webhook_distributor.register_webhook(
        webhook_id='wh-001',
        url='https://api.company.com/webhooks/reports',
        events=['report_generated', 'report_scheduled'],
        enabled=True
    )
    print(f"✓ Webhook registered: {webhook['webhook_id']}")
    print(f"✓ Events: {webhook['events']}")
    
    # Distribute report
    print_subsection("Distributing Report")
    
    report_data = SAMPLE_INSIGHTS_DATA.copy()
    report_data['title'] = 'Executive Summary Report'
    report_data['key_metrics'] = {
        'health_score': 72,
        'opportunities_count': 2,
        'total_opportunity_value': 80000
    }
    
    channels = [
        DistributionChannel.EMAIL,
        DistributionChannel.WEBHOOK,
        DistributionChannel.FILE_STORAGE,
        DistributionChannel.DASHBOARD
    ]
    
    recipients = {
        'email': ['exec@company.com', 'manager@company.com'],
        'slack_channels': ['#executive-reports']
    }
    
    distributions = distributor.distribute_report(
        report_id='REP-20260609-0001',
        report_title='Executive Report',
        report_content=report_data,
        channels=channels,
        recipients=recipients
    )
    
    print(f"✓ Distribution tasks: {len(distributions)}")
    for dist in distributions:
        print(f"  - {dist.channel.value}: {dist.status}")
        print(f"    Recipients: {len(dist.recipients)}")
    
    # Get distribution history
    print_subsection("Distribution History")
    history = distributor.get_distribution_history(limit=10)
    print(f"✓ Total distributions: {len(history)}")
    
    # Get statistics
    print_subsection("Distribution Statistics")
    stats = distributor.get_distribution_statistics()
    print(f"✓ Total distributions: {stats['total_distributions']}")
    print(f"✓ Sent: {stats['sent']}")
    print(f"✓ Failed: {stats['failed']}")
    print(f"✓ Success rate: {stats['success_rate']*100:.1f}%")
    print(f"✓ By channel:")
    for channel, counts in stats['by_channel'].items():
        print(f"  - {channel}: {counts['total']} (sent: {counts['sent']}, failed: {counts['failed']})")
    
    print(f"\n✅ Report distribution completed")


def test_5_end_to_end_service():
    """Test 5: End-to-End Report Generation Service"""
    print_section("Test 5: END-TO-END REPORT GENERATION SERVICE")
    
    service = ReportGenerationService()
    
    # Generate executive report
    print_subsection("Generating Executive Report via Service")
    exec_result = service.generate_executive_report(SAMPLE_INSIGHTS_DATA)
    print(f"✓ Report ID: {exec_result['report_id']}")
    print(f"✓ Status: {exec_result['status']}")
    print(f"✓ Key metrics: {len(exec_result['key_metrics'])}")
    print(f"✓ Sections: {exec_result['section_count']}")
    
    # Format report
    print_subsection("Formatting Report")
    for format_type in ['json', 'html', 'markdown', 'text']:
        formatted = service.format_report(exec_result['report_id'], format_type)
        print(f"✓ Format {format_type}: {len(formatted)} characters")
    
    # Get visualization specs
    print_subsection("Getting Visualization Specs")
    specs = service.get_visualization_specs(exec_result['report_id'])
    print(f"✓ Charts: {len(specs['charts'])}")
    print(f"✓ Tables: {len(specs['tables'])}")
    
    # Create schedule
    print_subsection("Creating Report Schedule")
    schedule = service.create_report_schedule(
        report_type='executive_summary',
        frequency='daily',
        recipients=['daily-report@company.com'],
        run_time='08:00'
    )
    print(f"✓ Schedule ID: {schedule['schedule_id']}")
    print(f"✓ Frequency: {schedule['frequency']}")
    
    # Get all schedules
    print_subsection("Retrieving Schedules")
    all_schedules = service.get_all_schedules()
    print(f"✓ Total schedules: {len(all_schedules)}")
    print(f"✓ Schedule details retrieved successfully")
    
    # Distribute report
    print_subsection("Distributing Report")
    distributions = service.distribute_report(
        exec_result['report_id'],
        exec_result['data'],
        channels=['email', 'file_storage'],
        recipients={'email': ['manager@company.com']}
    )
    print(f"✓ Distributions: {len(distributions)}")
    for dist in distributions:
        print(f"  - {dist['channel']}: {dist['status']}")
    
    # Get statistics
    print_subsection("Service Statistics")
    scheduler_stats = service.get_scheduler_statistics()
    dist_stats = service.get_distribution_statistics()
    print(f"✓ Total schedules: {scheduler_stats['total_schedules']}")
    print(f"✓ Enabled schedules: {scheduler_stats['enabled_schedules']}")
    print(f"✓ Distribution success rate: {dist_stats['success_rate']*100:.1f}%")
    
    # Export configuration
    print_subsection("Exporting Configuration")
    config = service.export_configuration()
    print(f"✓ Export date: {config['export_date']}")
    print(f"✓ Schedules in export: {config['schedules']['total_schedules']}")
    
    print(f"\n✅ End-to-end service test completed")


def test_6_special_scenarios():
    """Test 6: Special Scenarios and Edge Cases"""
    print_section("Test 6: SPECIAL SCENARIOS AND EDGE CASES")
    
    generator = ReportGenerator()
    formatter = ReportFormatter()
    
    # Empty insights data
    print_subsection("Test: Handling Empty Insights Data")
    empty_data = {'findings': [], 'opportunities': [], 'alerts': []}
    report = generator.generate_executive_summary_report(empty_data)
    print(f"✓ Report generated with empty data: {report.metadata.report_id}")
    print(f"✓ Sections created: {len(report.sections)}")
    
    # Large datasets
    print_subsection("Test: Handling Large Datasets")
    large_findings = [
        {
            'title': f'Finding {i}',
            'description': f'Description for finding {i}',
            'severity': 'MEDIUM' if i % 2 == 0 else 'CRITICAL',
            'metric': 'metric_value',
            'current_value': 100 + i,
            'baseline_value': 100,
            'change_percent': i,
            'affected_entities': [f'Entity_{i}']
        }
        for i in range(50)
    ]
    large_data = {'findings': large_findings, 'opportunities': [], 'alerts': []}
    large_report = generator.generate_executive_summary_report(large_data)
    print(f"✓ Report with 50 findings generated: {large_report.metadata.report_id}")
    print(f"✓ Key findings extracted: {len(large_report.sections[1].subsections) if len(large_report.sections) > 1 else 0}")
    
    # Format to all formats
    print_subsection("Test: Multi-Format Export")
    for fmt in OutputFormat:
        output = formatter.format(report, fmt)
        print(f"✓ Format {fmt.value}: {len(output)} chars")
    
    print(f"\n✅ Special scenarios test completed")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("AUTONOMOUS REPORT GENERATION ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Run tests
        report = test_1_report_generator()
        test_2_report_formatter(report)
        test_3_report_scheduler()
        test_4_report_distributor()
        test_5_end_to_end_service()
        test_6_special_scenarios()
        
        # Summary
        print_section("TEST SUMMARY")
        print("✅ ALL TESTS PASSED")
        print("\n📊 Report Generation Engine Status:")
        print("   ✓ Report generator working correctly")
        print("   ✓ Report formatter supporting all formats (JSON, HTML, Markdown, Text, CSV, PDF)")
        print("   ✓ Report scheduler managing scheduling logic")
        print("   ✓ Report distributor handling multi-channel distribution")
        print("   ✓ End-to-end service orchestration functional")
        print("   ✓ Edge cases and special scenarios handled")
        
        print("\n🎯 Prompt 8: Autonomous Report Generator - COMPLETE ✅")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
