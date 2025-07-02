from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from pets.models import ScheduledTask
import requests
import logging
from decouple import config
from django.urls import reverse

logger = logging.getLogger(__name__)

def run_scheduled_tasks():
    now = timezone.localtime(timezone.now())
    logger.info(f"Checking scheduled tasks at {now}")
    
    day_translation = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábados',
        'Sunday': 'Domingos',
    }
    today = day_translation[now.strftime('%A')]

    tasks = ScheduledTask.objects.filter(
        hour=now.hour,
        minute=now.minute
    )

    for task in tasks:
        if task.schedule_type == 'Una vez':
            if task.date != now.date():
                continue
        elif task.schedule_type == 'Semanal':
            if task.day_of_week != today:
                continue
        elif task.schedule_type == 'Diario':
            if task.last_executed_at and task.last_executed_at.date() == now.date():
                continue

        logger.info(f"Executing task: {task.name}")

        try:
            response = requests.get(config('APPLICATION_URL', default = "") + reverse("api.pets.dispense") + f"?id={task.machine.id}", None)
            if response.status_code == 200:
                task.last_executed_at = now
                machine = task.machine
                task.save()
                machine.update_next_refill()
                logger.info(f"Task executed for machine {task.machine.id}")
                
            else:
                logger.error(f"Dispense error: {response.text}")
        except Exception as e:
            logger.error(f"Error calling dispense: {str(e)}")

def start():
    scheduler = BackgroundScheduler(
        timezone='America/Bogota',
        daemon=True
    )
    scheduler.add_job(run_scheduled_tasks, 'interval', minutes=1, next_run_time = timezone.now())
    scheduler.start()
    logger.info("Scheduler iniciado correctamente")