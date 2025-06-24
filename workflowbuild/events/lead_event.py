import frappe
from workflowbuild.schedule.execute_action import check_trigger_event
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("workflow_lead_event", allow_site=True, file_count=50)

def after_save_all(doc, method):
    try:
        current_state = doc.workflow_state
        status_changed = doc.has_value_changed("workflow_state")
        logger.info(f"\n\nCurrent status: {current_state}\nStatus changed: {status_changed}\n\n")

        print("Current status:", current_state)
        print("Status changed:", status_changed)

        if status_changed:
            # DB-level filter to only get relevant Workflow Configuration
            workflow_data_list = frappe.get_all(
                'Workflow Configuration',
                filters={
                    'trigger_event': current_state
                },
                fields=['name']
            )

            if workflow_data_list:
                workflow_data = frappe.get_doc('Workflow Configuration', workflow_data_list[0].name)
                workflow_actions = workflow_data.workflow_action or []

                workflow_actions_data = [
                    frappe.get_doc('Workflow Actions', action.name).as_dict()
                    for action in workflow_actions
                ]

                doc_dict = doc.as_dict()

                try:
                    res = check_trigger_event(workflow_actions_data, doc_dict)
                    if res:
                        logger.info(f"Trigger Event API Response: {res}")
                    else:
                        logger.info("No response from Trigger Event API")
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(), "Trigger Event API Error: " + str(e))
            else:
                logger.info("No matching Workflow Configuration found for current status.")
                print("No matching Workflow Configuration found for current status.\n\n")
        else:
            logger.info("Workflow name or status change not detected.")
            print("Workflow name or status change not detected.\n\n")

    except Exception as main_e:
        frappe.log_error(frappe.get_traceback(), "Error: " + str(main_e))
