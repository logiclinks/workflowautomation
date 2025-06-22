import frappe
import os
from datetime import datetime
from frappe.utils import now_datetime
from redis import Redis
from rq.job import Job
from datetime import timedelta
import redis

def create_scheduled_job(job_data):
    
    print("Current Path",os.getcwd())
    try:
        doc = frappe.get_doc({
            "doctype": "Scheduled  Job",
            "job_id": job_data.get("job_id"),
            "job_name": job_data.get("job_name"),
            "timeout": job_data.get("timeout"),
            "schedule_at": job_data.get("schedule_at"),
            "job_created": job_data.get("job_created") or now_datetime(),
            "arguments": job_data.get("arguments"),
            "status": job_data.get("status"),
            "time_taken": job_data.get("time_taken"),
            "started_at": job_data.get("started_at"),
            "ended_at": job_data.get("ended_at"),
            "exc_info": job_data.get("exc_info")
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc.name
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Scheduled Job Creation Error")
        print("Error creating Scheduled Job:", e)
        return None

def update_scheduled_job(job_id, status=None, started_at=None, error_msg=None):
    
    try:
        job_doc = frappe.get_doc("Scheduled  Job", job_id)

        if status is not None:
            job_doc.status = status
        if started_at is not None:
            job_doc.started_at = started_at
        if error_msg is not None:
            job_doc.exc_info = error_msg
        

        job_doc.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"Scheduled Job '{job_id}' updated successfully.")
    except frappe.DoesNotExistError:
        print(f"Scheduled Job with ID '{job_id}' does not exist.")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Scheduled Job Update Error")
        print(f"Error updating Scheduled Job '{job_id}':", e)


# @frappe.whitelist(allow_guest=True)
def refresh_job():
    try:
        print("Refresh Active")
        frappe.logger().info("Scheduled task ran.")
        scheduled_jobs = frappe.get_all(
            "Scheduled  Job",
            fields=["name", "job_id", "status"],
            filters={"status": ["not in", ["finished", "failed", "canceled"]]}
        )

        # change this in production
        # redis_url = "redis://redis-queue:6379"
        # redis_url = os.environ.get("REDIS_QUEUE", "redis://127.0.0.1:11000")
        redis_url = os.environ.get("REDIS_QUEUE", "redis://redis-queue:6379")
        
        if not redis_url:
            print("REDIS_QUEUE environment variable not set")
            return False

        redis_conn = redis.from_url(redis_url)

        for job_meta in scheduled_jobs:
            job_id = job_meta.job_id
            status = job_meta.status

            try:
                job = Job.fetch(job_id, connection=redis_conn)
                status = job.get_status()
                started_at = job.started_at
                ended_at = job.ended_at

                if not job.ended_at:
                    job.ended_at = job.started_at

                    duration = int(round((job.ended_at - job.started_at).total_seconds()))
                    
                    # Now assign to the Duration field
                    job_doc.time_taken = duration
                    
                    job_doc.save(ignore_permissions=True)
                    frappe.db.commit()


                if job_meta.status != status:

                    job_doc = frappe.get_doc("Scheduled  Job", job_meta.name)
                    job_doc.status = status

                    if started_at:
                        job_doc.started_at = started_at
                    if ended_at:
                        job_doc.ended_at = ended_at

                    if started_at and ended_at:
                        duration = round((ended_at - started_at).total_seconds())
                        if 1 < duration > 0:
                            duration = 1
                        duration = int(round((ended_at - started_at).total_seconds()))
                        # Now assign to the Duration field
                        job_doc.time_taken = duration

                    job_doc.save(ignore_permissions=True)
                    frappe.db.commit()

            except Exception as job_error:
                print(f"Error fetching job {job_id}: {job_error}")

    except Exception as e:
        print("Error in refresh_job:", e)