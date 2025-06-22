app_name = "workflowbuild"
app_title = "Workflowbuild"
app_publisher = "Mradul Mishra, Shubhamm Mohitte"
app_description = "WorkFlow Builder"
app_email = "mishramradul29@gmail.com, mohite.shubhu61@gmail.com"
app_license = "mit"

# Apps
# ------------------


scheduler_events = {
    "cron": {
        "0/1 * * * *": [  # every 1 minute
          "workflowbuild.schedule.logs.refresh_job"  # function to execute
        ]
    }
}

override_whitelisted_methods = {
	"workflowbuild.schedule.logs.refresh_job": "workflowbuild.schedule.logs.refresh_job"
}

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "workflowbuild",
# 		"logo": "/assets/workflowbuild/logo.png",
# 		"title": "Workflowbuild",
# 		"route": "/workflowbuild",
# 		"has_permission": "workflowbuild.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/workflowbuild/css/workflowbuild.css"
# app_include_js = "/assets/workflowbuild/js/workflowbuild.js"

# include js, css files in header of web template
# web_include_css = "/assets/workflowbuild/css/workflowbuild.css"
# web_include_js = "/assets/workflowbuild/js/workflowbuild.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "workflowbuild/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "workflowbuild/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "workflowbuild.utils.jinja_methods",
# 	"filters": "workflowbuild.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "workflowbuild.install.before_install"
# after_install = "workflowbuild.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "workflowbuild.uninstall.before_uninstall"
# after_uninstall = "workflowbuild.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "workflowbuild.utils.before_app_install"
# after_app_install = "workflowbuild.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "workflowbuild.utils.before_app_uninstall"
# after_app_uninstall = "workflowbuild.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "workflowbuild.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
  "Lead": {
      "on_change":"workflowbuild.events.lead_event.after_save_all"
  }
}
# doc_events = {"Lead": {"before_save":"workflowbuild.lead_event.after_save_all"}}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"workflowbuild.tasks.all"
# 	],
# 	"daily": [
# 		"workflowbuild.tasks.daily"
# 	],
# 	"hourly": [
# 		"workflowbuild.tasks.hourly"
# 	],
# 	"weekly": [
# 		"workflowbuild.tasks.weekly"
# 	],
# 	"monthly": [
# 		"workflowbuild.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "workflowbuild.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "workflowbuild.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "workflowbuild.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["workflowbuild.utils.before_request"]
# after_request = ["workflowbuild.utils.after_request"]

# Job Events
# ----------
# before_job = ["workflowbuild.utils.before_job"]
# after_job = ["workflowbuild.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"workflowbuild.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

