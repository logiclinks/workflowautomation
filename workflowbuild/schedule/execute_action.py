import frappe
from frappe.model.document import Document 
from frappe.utils import now_datetime
from datetime import timedelta, datetime
from rq import Queue
from redis import Redis
import redis
from .logs import create_scheduled_job
import os
import json
from .logs import create_scheduled_job
import logging
from .delayed_tasks import backgroundScheduler, enqueue_email_job, enqueue_sms_job, enqueue_todo_job, FrappeJobEncoder
from .utils import send_email

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.StreamHandler())  # Optional: only for dev or Docker logs
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("execute_actions", allow_site=True, file_count=50)

def get_job_name_and_func(job_name):
    if 'email_job' in job_name:
        return 'Email', 'workflowbuild.schedule.utils.send_email'
    elif 'sms_job' in job_name:
        return 'SMS', 'workflowbuild.schedule.utils.sends_sms_here'
    elif 'todo_job' in job_name:
        return 'ToDo', 'workflowbuild.schedule.utils.assign_task'
    return None

def check_trigger_event(workflow_actions, doc):
    # print("\nStart path",os.getcwd())
    logger.info("\n\nStarted check_trigger_event in path: %s", os.getcwd())
    
    try:
        """Cron job to check if any workflow event is triggered and act on the configured actions"""
        # logger.info(f"Current Path: {os.getcwd()=}")
        
        redis_url = os.environ.get("REDIS_QUEUE", "redis://redis-queue:6379")
        
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

            _job_name = f"Send_{action_type} {doc.name}"
            _job_enq_id = "".join(str(datetime.now().timestamp()).split("."))

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
                    args=[job_creation_time, schedule_time, email_detail, _job_name, _job_enq_id],
                    id=_job_name,
                    misfire_grace_time=60,
                    jobstore='persistent'
                )
                set_future_scheduled_job(email_detail, action_type, email_job, _job_enq_id, job_start=job_creation_time, job_scheduled=schedule_time)
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
                    args=[job_creation_time, schedule_time, sms_detail, _job_name, _job_enq_id],
                    id=_job_name,
                    misfire_grace_time=60,
                    jobstore='persistent'
                )
                set_future_scheduled_job(sms_detail, action_type, sms_job, _job_enq_id, job_start=job_creation_time, job_scheduled=schedule_time)
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
                    args=[job_creation_time, schedule_time, todo_detail, _job_name, _job_enq_id],
                    id=_job_name,
                    misfire_grace_time=60,
                    jobstore='persistent'
                )
                set_future_scheduled_job(todo_detail, action_type, todo_job, _job_enq_id, job_start=job_creation_time, job_scheduled=schedule_time)
                # -----------------------------------------------

        logger.info(f"=== All Actions Scheduled ===\n\n")
        return True

    except Exception as error:
        logger.error(f"Error in check_trigger_event: {str(error)}", exc_info=True)
        return 


def set_future_scheduled_job(data, action_type, _job, _job_enq_id, **kwargs):

    try:
        job_creation_time = kwargs.get("job_start")
        scheduled_time = kwargs.get("job_scheduled")

        #  serialize data
        job_kwargs_serializable = {}
        try:
            # Use the custom encoder for a robust serialization of kwargs
            job_kwargs_serializable = json.loads(json.dumps(data, cls=FrappeJobEncoder))
        except Exception as e:
            logger.error(f"Error serializing job.kwargs: {e}")
            # Fallback or simplified serialization if the above fails
            job_kwargs_serializable = str(data)


        # Create new entry for `Future Scheduled Job`
        logger.info(f"{action_type} Job Scheduled with APScheduler: {_job.id},\nwill run at {scheduled_time}\n")
        # logger.info(f"{data=}")
        # logger.info(f'{_job=}')

        job_name, job_func = get_job_name_and_func(_job.name)
        
        doc = frappe.get_doc({
            "doctype": "Future Scheduled Job",
            "name": _job_enq_id,
            "job_id": _job.id,
            "job_name": job_name,
            "job_function": job_func,
            "job_created_at": job_creation_time or now_datetime(),
            "job_scheduled_at": scheduled_time or None,
            "lead_id": data['doc']['name'],
            "arguments": json.dumps(job_kwargs_serializable),
            "status": "Scheduled"
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        logger.error(f"{str(e)}", exc_info=True)

    return

