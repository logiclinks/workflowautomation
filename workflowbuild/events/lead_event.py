import frappe
from workflowbuild.schedule.execute_action import check_trigger_event

def after_save_all(doc, method):
    try:
        current_state = doc.status
        status_changed = doc.has_value_changed("status")
        # workflow_state

        frappe.logger().info(f"Current status: {current_state}, Status changed: {status_changed}")

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
                        frappe.logger().info(f"Trigger Event API Response: {res}")
                    else:
                        frappe.logger().warning("No response from Trigger Event API")
                except Exception as e:
                    frappe.log_error("Trigger Event API Error", str(e))
            else:
                frappe.logger().info("No matching Workflow Configuration found for current status.")
                print("No matching Workflow Configuration found for current status.")
        else:
            frappe.logger().info("Workflow name or status change not detected.")
            print("Workflow name or status change not detected.")

    except Exception as main_e:
        frappe.log_error("after_save_all Error", str(main_e))
