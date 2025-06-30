import os
import frappe
from frappe.utils import now_datetime
from rq import get_current_job
from frappe.utils import now_datetime
from rq.job import Job
from redis import Redis
from .logs import  update_scheduled_job,  update_future_jobs
from dotenv import load_dotenv
from datetime import timedelta
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import redis

from twilio_settings.actions.utils import _send_sms_twilio

redis_url = os.environ.get("REDIS_QUEUE", "redis://redis-queue:6379")
redis_conn = redis.from_url(redis_url)

def send_email(email_detail):
    """Send Email using provided email_template and log job status"""

    started_at = now_datetime()
    job_id = get_current_job().id if get_current_job() else None
    _job_id = str(job_id).split("::")[1]

    try: 
        doc = email_detail.get("doc")
        if not doc:
            raise ValueError("Document not provided")

        email_temp = email_detail.get("email_temp")
        if not email_temp or not doc.get('email_id'):
            raise ValueError("Missing email template or recipient email ID")

        # Render subject and message using Jinja and doc context
        subject = frappe.render_template(email_temp.subject, doc)
        message = frappe.render_template(email_temp.response, doc)

        frappe.sendmail(
            recipients=[doc.email_id],
            subject=subject or "Notification",
            message=message,
            delayed=False
        )
        frappe.log(f"Email sent to: {doc.email_id}, JOB-ID: {_job_id}")

        if _job_id:

            job = Job.fetch(job_id, connection=redis_conn)
            status = job.get_status()
            update_future_jobs(_job_id, "Started")
            update_scheduled_job(job_id, 'finished', started_at)

    except Exception as error:
        frappe.log_error(frappe.get_traceback(), f"Error in Email Sending: {str(error)}" )
        if job_id:
            update_future_jobs(_job_id, "Failed", error_msg=str(error))
            update_scheduled_job(job_id, "failed", started_at, str(error))

    finally:
        frappe.destroy()

def sends_sms_here(sms_detail):
    """Send SMS using provided sms_template and log job status"""
    
    started_at = now_datetime()
    job_id = get_current_job().id if get_current_job() else None
    _job_id = str(job_id).split("::")[1]

    try:
        doc = sms_detail.get("doc")
        sms_temp = sms_detail.get("sms_temp")

        if not sms_temp or not doc.get('mobile_no'):
            raise ValueError("Missing mobile number or SMS template")

        recipient = str(doc.get('mobile_no'))

        # Render the SMS message template
        message_template = frappe.db.get_value("SMS Template", sms_temp, "template_text")
        if not message_template:
            raise ValueError("SMS template not found")

        message = frappe.render_template(message_template, doc)

        res = _send_sms_twilio(recipient, message, doc)
        frappe.log(f"\n{res=}")
        # send_sms([recipient], message, sender_name="LogicLinks.io")
        frappe.log(f"\n\nSMS SENT on {doc.get('mobile_no')}")

        # Fetch job status and log it
        if _job_id:
            job = Job.fetch(job_id, connection=redis_conn)
            status = job.get_status()
            update_future_jobs(_job_id, "Started")
            update_scheduled_job(job_id, 'finished', started_at)

    except Exception as error:
        print("Error in SMS Sending:", error)
        if job_id:
            update_future_jobs(_job_id, "Failed", error_msg=str(error))
            update_scheduled_job(job_id, "failed", started_at, str(error))

    finally:
        frappe.destroy()

def assign_task(todo_detail):
    
    started_at = now_datetime()
    job_id = get_current_job().id if get_current_job() else None
    _job_id = str(job_id).split("::")[1]

    try:
        action = todo_detail['action']
        assigned_user = action['assigned_user']
        if not assigned_user:
            raise ValueError("Assigned user not found in action or document")

        todo_temp = todo_detail['todo_temp']
        if not todo_temp:
            raise ValueError("ToDo Template not found")

        description = todo_temp.get("description")
        due_in_seconds = todo_temp.get("due_date") or 0
        due_date = now_datetime() + timedelta(seconds=due_in_seconds)


        doc = todo_detail['doc']
        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": description,
            "owner": doc.get('lead_owner'),
            "reference_type": "Lead",
            "reference_name": doc.get('name'),
            "allocated_to": assigned_user,
            "date": due_date,
            "assigned_by": doc.get('lead_owner')
        }).insert(ignore_permissions=True)

        frappe.db.commit()
        print("ToDo created with name:", todo.name)

        if _job_id:
            # redis_conn = Redis()
            job = Job.fetch(job_id, connection=redis_conn)
            status = job.get_status()
            update_future_jobs(_job_id, "Started")
            update_scheduled_job(job_id, 'finished', started_at)


    except Exception as error:
        print("Error in ToDo Assignment:", error)
        if job_id:
            update_future_jobs(_job_id, "Failed", error_msg=str(error))
            update_scheduled_job(job_id, "failed", started_at, str(error))

    finally:
        frappe.destroy()



   