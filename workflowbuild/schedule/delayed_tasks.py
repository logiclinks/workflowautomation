# apps/workflowbuild/workflowbuild/schedule/delayed_tasks.py
import frappe
from frappe.model.document import Document 

import json, os, logging
from datetime import timedelta, datetime

from .logs import create_scheduled_job

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Define job stores
jobstores = {
    'default': MemoryJobStore(),  # In-memory store (no persistence)
    'persistent': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')  # SQLite-based persistent store
}
# Create scheduler with job stores configuration
backgroundScheduler = BackgroundScheduler(jobstores=jobstores)
backgroundScheduler.start()



# --- Initialize Logger ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Define a custom JSON encoder for non-standard types
class FrappeJobEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            # Convert timedelta to total seconds
            return obj.total_seconds()
        elif isinstance(obj, Document):
            # For Frappe Document objects, serialize relevant fields or convert to a dict
            # You might want to be more selective here, e.g., only pass name, doctype, etc.
            return obj.as_dict() # This is a good way to get a serializable dictionary representation
        elif isinstance(obj, datetime):
            # Convert datetime objects to ISO format strings
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def enqueue_email_job(job_creation_time, schedule_time, email_detail, _job_name, _job_enq_id):
    # SITE_NAME=os.environ.get("SITES", "logic.localhost")
    SITE_NAME=os.environ.get("SITES", "logiclinks.io")

    try:
        frappe.init(site=SITE_NAME)
        frappe.local.site = SITE_NAME # Manually set the site on frappe.local
        frappe.connect()
        frappe.set_user("Administrator") # Set a user context, essential for many Frappe operations
        logger.info(f"Frappe context initialized in APScheduler job: Site={frappe.local.site}, User={frappe.session.user}")
    except Exception as e:
        logger.error(f"Failed to initialize Frappe context in APScheduler job: {e}", exc_info=True)
        # If context fails, we cannot proceed with Frappe.enqueue
        return

    # / IMP --------- 
    job = frappe.enqueue(
        'workflowbuild.schedule.utils.send_email',
        queue="email",
        is_async=True,
        job_id=_job_enq_id,
        job_name=_job_name,
        email_detail=email_detail
    )
    
    job_kwargs_serializable = {}
    try:
        # Use the custom encoder for a robust serialization of kwargs
        job_kwargs_serializable = json.loads(json.dumps(job.kwargs, cls=FrappeJobEncoder))
    except Exception as e:
        logger.error(f"Error serializing job.kwargs: {e}")
        # Fallback or simplified serialization if the above fails
        job_kwargs_serializable = str(job.kwargs)

    job_data = {
        "job_id": _job_enq_id,
        "job_name": job.func_name, # This will be 'workflowbuild.schedule.utils.send_email'
        "timeout": job.timeout,
        "job_created": job_creation_time, # Ensure datetime is serialized
        "schedule_at": schedule_time,
        "arguments": json.dumps(job_kwargs_serializable, indent=2), # 'arguments' will now hold your serialized kwargs
        "status": job.get_status()
    }
    job_resp = create_scheduled_job(job_data)

    return

def enqueue_sms_job(job_creation_time, schedule_time, sms_detail, _job_name, _job_enq_id):
    SITE_NAME=os.environ.get("SITES", "logic.localhost")
    # SITE_NAME=os.environ.get("SITES", "logiclinks.io")

    try:
        frappe.init(site=SITE_NAME)
        frappe.local.site = SITE_NAME # Manually set the site on frappe.local
        frappe.connect()
        frappe.set_user("Administrator") # Set a user context, essential for many Frappe operations
        logger.info(f"Frappe context initialized in APScheduler job: Site={frappe.local.site}, User={frappe.session.user}")
    except Exception as e:
        logger.error(f"Failed to initialize Frappe context in APScheduler job: {e}", exc_info=True)
        # If context fails, we cannot proceed with Frappe.enqueue
        return

    # / IMP --------- 
    job = frappe.enqueue(
        'workflowbuild.schedule.utils.sends_sms_here',
        queue="sms",
        is_async=True,
        job_id=_job_enq_id,
        job_name=_job_name,
        sms_detail=sms_detail
    )
    
    job_kwargs_serializable = {}
    try:
        # Use the custom encoder for a robust serialization of kwargs
        job_kwargs_serializable = json.loads(json.dumps(job.kwargs, cls=FrappeJobEncoder))
    except Exception as e:
        logger.error(f"Error serializing job.kwargs: {e}")
        # Fallback or simplified serialization if the above fails
        job_kwargs_serializable = str(job.kwargs)

    job_data = {
        "job_id": _job_enq_id,
        "job_name": job.func_name, # This will be 'workflowbuild.schedule.utils.send_email'
        "timeout": job.timeout,
        "job_created": job_creation_time, # Ensure datetime is serialized
        "schedule_at": schedule_time,
        "arguments": json.dumps(job_kwargs_serializable, indent=2), # 'arguments' will now hold your serialized kwargs
        "status": job.get_status()
    }
    job_resp = create_scheduled_job(job_data)

    return

def enqueue_todo_job(job_creation_time, schedule_time, todo_detail, _job_name, _job_enq_id):
    # SITE_NAME=os.environ.get("SITES", "logic.localhost")
    SITE_NAME=os.environ.get("SITES", "logiclinks.io")

    try:
        frappe.init(site=SITE_NAME)
        frappe.local.site = SITE_NAME # Manually set the site on frappe.local
        frappe.connect()
        frappe.set_user("Administrator") # Set a user context, essential for many Frappe operations
        logger.info(f"Frappe context initialized in APScheduler job: Site={frappe.local.site}, User={frappe.session.user}")
    
    except Exception as e:
        logger.error(f"Failed to initialize Frappe context in APScheduler job: {e}", exc_info=True)
        # If context fails, we cannot proceed with Frappe.enqueue
        return

    # / IMP --------- 
    job = frappe.enqueue(
        'workflowbuild.schedule.utils.assign_task',
        queue="todo",
        is_async=True,
        job_id=_job_enq_id,
        job_name=_job_name,
        todo_detail=todo_detail
    )
    
    job_kwargs_serializable = {}
    try:
        # Use the custom encoder for a robust serialization of kwargs
        job_kwargs_serializable = json.loads(json.dumps(job.kwargs, cls=FrappeJobEncoder))
    except Exception as e:
        logger.error(f"Error serializing job.kwargs: {e}")
        # Fallback or simplified serialization if the above fails
        job_kwargs_serializable = str(job.kwargs)

    job_data = {
        "job_id": _job_enq_id,
        "job_name": job.func_name, # This will be 'workflowbuild.schedule.utils.send_email'
        "timeout": job.timeout,
        "job_created": job_creation_time, # Ensure datetime is serialized
        "schedule_at": schedule_time,
        "arguments": json.dumps(job_kwargs_serializable, indent=2), # 'arguments' will now hold your serialized kwargs
        "status": job.get_status()
    }
    job_resp = create_scheduled_job(job_data)

    return