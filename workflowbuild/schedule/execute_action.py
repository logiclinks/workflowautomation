import frappe
from frappe.model.document import Document 

from datetime import timedelta, datetime
from rq import Queue
from redis import Redis
import redis
from .logs import create_scheduled_job
import os
import json
from .logs import create_scheduled_job
import logging
from .delayed_tasks import backgroundScheduler, enqueue_email_job, enqueue_sms_job, enqueue_todo_job
from .utils import send_email

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())  # Optional: only for dev or Docker logs


def check_trigger_event(workflow_actions, doc):
    print("\nStart path",os.getcwd())
    logger.info("Started check_trigger_event in path: %s", os.getcwd())
    
    try:
        """Cron job to check if any workflow event is triggered and act on the configured actions"""
        logger.info(f"Current Path: {os.getcwd()=}")
        
        # change this in production
        # redis_url = os.environ.get("REDIS_QUEUE", "redis://127.0.0.1:11000")
        redis_url = os.environ.get("REDIS_QUEUE", "redis://redis-queue:6379")
        logger.info(f"{redis_url=}")

        if not redis_url:
            logger.error("REDIS_QUEUE environment variable not set")
            return False

        redis_conn = redis.from_url(redis_url)
        logger.info("Connected to Redis at: %s", redis_url)

        for action in workflow_actions:

            action_type = action.get('action_type')  # Email, SMS, ToDo
            execution_days = int(action.get('execution_time') or 0)

            job_creation_time = datetime.now()
            time_delay = timedelta(seconds=execution_days)
            schedule_time = job_creation_time + time_delay # Calculate the exact future time

            logger.info(f"Processing Action {action_type} Start")

            if action_type == "Email":
                email_template = frappe.get_doc("Email Template", action.get("email_template"))
                email_detail = {
                    "email_temp": email_template,
                    "email_id": doc.email_id,
                    "doc": doc
                }
                email_job = backgroundScheduler.add_job(
                    enqueue_email_job,
                    'date',
                    run_date=schedule_time,
                    args=[job_creation_time, schedule_time, email_detail],
                    id=f"Send-Email_{doc.name}_{datetime.now().timestamp()}",
                    misfire_grace_time=60
                )
                # create_scheduled_job(job_data) # Log this APScheduler job
                logger.info(f"Email Job Scheduled with APScheduler: {email_job.id}, will run at {schedule_time}")
                logger.info("Action Email Ended (APScheduler)\n\n")
                # -----------------------------------------------

            elif action_type == "SMS":
                sms_template = frappe.get_doc("SMS Template", action.get("sms_template"))
                sms_detail = {
                    "sms_temp": sms_template,
                    "mobile_no": doc.mobile_no,
                    "doc": doc
                }
                sms_job = backgroundScheduler.add_job(
                    enqueue_sms_job,
                    'date',
                    run_date=schedule_time,
                    args=[job_creation_time, schedule_time, sms_detail],
                    id=f"Send-SMS_{doc.name}_{datetime.now().timestamp()}",
                    misfire_grace_time=60
                )
                # create_scheduled_job(job_data) # Log this APScheduler job
                logger.info(f"SMS Job Scheduled with APScheduler: {sms_job.id}, will run at {schedule_time}")
                logger.info("Action SMS Ended (APScheduler)\n\n")
                # -----------------------------------------------

            elif action_type == "ToDO":
                
                todo_template = frappe.get_doc("ToDo Template", action.get("todo_template"))
                todo_detail = {
                    "todo_temp": todo_template,
                    "action": action,
                    "doc": doc
                }
                todo_job = backgroundScheduler.add_job(
                    enqueue_todo_job,
                    'date',
                    run_date=schedule_time,
                    args=[job_creation_time, schedule_time, todo_detail],
                    id=f"Send-ToDo_{doc.name}_{datetime.now().timestamp()}",
                    misfire_grace_time=60
                )
                # create_scheduled_job(job_data) # Log this APScheduler job
                logger.info(f"TODO Job Scheduled with APScheduler: {todo_job.id}, will run at {schedule_time}")
                logger.info("Action TODO Ended (APScheduler)\n\n")
                # -----------------------------------------------

        logger.info("Completed check_trigger_event")

        return True

    except Exception as error:
        logger.error(f"Error in check_trigger_event: {str(error)}", exc_info=True)
        return False