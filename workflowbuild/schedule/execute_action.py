import frappe
from datetime import timedelta
from rq import Queue
from redis import Redis
import redis
from .logs import create_scheduled_job
import os
import json
from .logs import create_scheduled_job
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())  # Optional: only for dev or Docker logs


def check_trigger_event(workflow_actions, doc):
    print("start path",os.getcwd())
    logger.info("Started check_trigger_event in path: %s", os.getcwd())
    try:
        """Cron job to check if any workflow event is triggered and act on the configured actions"""
        print("Current Path",os.getcwd())
        
        redis_url = os.environ.get("REDIS_QUEUE")
        logger.info(f"{redis_url=}")

        if not redis_url:
            logger.error("REDIS_QUEUE environment variable not set")
            return False

        redis_conn = redis.from_url(redis_url)
        logger.info("Connected to Redis at: %s", redis_url)

        for action in workflow_actions:

            action_type = action.get('action_type')  # Email, SMS, ToDo
            execution_days = int(action.get('execution_time') or 0)
            logger.info("Processing action: %s", action_type)

            if action_type == "Email":
                logger.info("Action Email Start")
                # queue_email = Queue(name='home-frappe-frappe-bench:email', connection=redis_conn)
                queue_email = Queue(name='email', connection=redis_conn)
                email_template = frappe.get_doc("Email Template", action.get("email_template"))

                email_detail = {
                    "email_temp": email_template,
                    "email_id": doc.email_id,
                    "doc":doc
                }

                job = queue_email.enqueue_in(
                    timedelta(seconds=int(execution_days)),
                    "workflowbuild.schedule.utils.send_email",
                    args=[email_detail]
                )
                job_args_serializable = []

                for arg in job.args:
                    try:
                        job_args_serializable.append(json.loads(json.dumps(arg, default=str)))
                    except Exception as e:
                        job_args_serializable.append(str(arg))

                job_data = {
                    "job_id": job.id,
                    "job_name": job.func_name,  # Use job.func_name instead of private _func_name
                    "timeout": job.timeout,
                    "schedule_at": job.enqueued_at or None,
                    "job_created": job.created_at,
                    "arguments": json.dumps(job_args_serializable, indent=2),
                    "status": job.get_status()
                }
                job_resp = create_scheduled_job(job_data)
                print("Email Job Scheduled:", job_resp)
                logger.info("Action Email Ended")

            elif action_type == "SMS":
                logger.info("Action SMS Start")
                # queue_sms = Queue(name='home-frappe-frappe-bench:sms', connection=redis_conn)
                queue_sms = Queue(name='sms', connection=redis_conn)
                job = queue_sms.enqueue_in(
                    timedelta(seconds=int(execution_days)),
                    "workflowbuild.schedule.utils.sends_sms",
                    args=[action,doc]
                )

                job_args_serializable = []
                for arg in job.args:
                    try:
                        job_args_serializable.append(json.loads(json.dumps(arg, default=str)))
                    except Exception as e:
                        job_args_serializable.append(str(arg))

                job_data = {
                    "job_id": job.id,
                    "job_name": job.func_name,
                    "timeout": job.timeout,
                    "schedule_at": job.enqueued_at or None,
                    "job_created": job.created_at,
                    "arguments": json.dumps(job_args_serializable, indent=2),
                    "status": job.get_status()
                }
                job_resp = create_scheduled_job(job_data)
                logger.info("Action SMS Ended")

                print("SMS Job Scheduled:", job_resp)


            elif action_type == "ToDO":
                logger.info("Action ToDo Start")
                # queue_todo = Queue(name='home-frappe-frappe-bench:todo', connection=redis_conn)
                queue_todo = Queue(name='todo', connection=redis_conn)
                job = queue_todo.enqueue_in(
                    timedelta(seconds=int(execution_days)),
                    "workflowbuild.schedule.utils.assign_task",
                    args=[action, doc]
                )
                job_args_serializable = []

                for arg in job.args:
                    try:
                        job_args_serializable.append(json.loads(json.dumps(arg, default=str)))
                    except Exception as e:
                        job_args_serializable.append(str(arg))

                job_data = {
                    "job_id": job.id,
                    "job_name": job.func_name,
                    "timeout": job.timeout,
                    "schedule_at": job.enqueued_at or None,
                    "job_created": job.created_at,
                    "arguments": json.dumps(job_args_serializable, indent=2),
                    "status": job.get_status()
                }
                job_resp = create_scheduled_job(job_data)
                print("ToDo Job Scheduled:", job_resp)
                logger.info("Action ToDo Ended")
                
        logger.info("Completed check_trigger_event")

        return True

    except Exception as error:
        logger.error(f"Error in check_trigger_event: {str(error)}", exc_info=True)
        return False
