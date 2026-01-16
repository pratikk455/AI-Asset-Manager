"""
Shrestha Capital - Celery Configuration

Celery app for scheduled and background tasks.
"""

from celery import Celery
from celery.schedules import crontab
import os

# Create Celery app
app = Celery(
    'shrestha_capital',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=[
        'scheduler.jobs.daily',
        'scheduler.jobs.weekly',
    ]
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/New_York',  # Market timezone
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Daily tasks - run at 9 AM ET (market open)
    'daily-position-monitor': {
        'task': 'scheduler.jobs.daily.monitor_all_positions',
        'schedule': crontab(hour=9, minute=0, day_of_week='mon-fri'),
    },
    'daily-price-update': {
        'task': 'scheduler.jobs.daily.update_all_prices',
        'schedule': crontab(hour=16, minute=30, day_of_week='mon-fri'),  # After market close
    },

    # Weekly tasks - run Monday 8 AM ET
    'weekly-risk-report': {
        'task': 'scheduler.jobs.weekly.generate_risk_reports',
        'schedule': crontab(hour=8, minute=0, day_of_week='mon'),
    },
    'weekly-rebalance-check': {
        'task': 'scheduler.jobs.weekly.check_rebalancing',
        'schedule': crontab(hour=8, minute=30, day_of_week='mon'),
    },
    'weekly-performance-update': {
        'task': 'scheduler.jobs.weekly.update_performance',
        'schedule': crontab(hour=9, minute=0, day_of_week='mon'),
    },
}
