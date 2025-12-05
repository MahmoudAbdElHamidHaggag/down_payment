app_name = "down_payment"
app_title = "Down Payment"
app_publisher = "Mahmoud Abd El Hamied Omr Haggag"
app_description = "Down Payment For Advanced payment for customer in sales invoice"
app_email = "haggag.haggag224@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "down_payment",
# 		"logo": "/assets/down_payment/logo.png",
# 		"title": "Down Payment",
# 		"route": "/down_payment",
# 		"has_permission": "down_payment.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/down_payment/css/down_payment.css"
# app_include_js = "/assets/down_payment/js/down_payment.js"

# include js, css files in header of web template
# web_include_css = "/assets/down_payment/css/down_payment.css"
# web_include_js = "/assets/down_payment/js/down_payment.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "down_payment/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Sales Invoice" : "public/js/add_down_invoice.js", "Sales Order" : "public/js/sales_order.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "down_payment/public/icons.svg"

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
# 	"methods": "down_payment.utils.jinja_methods",
# 	"filters": "down_payment.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "down_payment.install.before_install"
# after_install = "down_payment.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "down_payment.uninstall.before_uninstall"
# after_uninstall = "down_payment.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "down_payment.utils.before_app_install"
# after_app_install = "down_payment.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "down_payment.utils.before_app_uninstall"
# after_app_uninstall = "down_payment.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "down_payment.notifications.get_notification_config"

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
	"Sales Invoice": {
		# "on_update": "down_payment.api.create_sales_invoice_on_sales_order",
		"on_cancel": "down_payment.api.on_si_cancel",
		# "on_trash": "down_payment.api.create_sales_invoice_on_sales_order",
        # "validate": "down_payment.api.create_sales_invoice_on_sales_order"
		"on_submit": "down_payment.api.on_si_submit"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"down_payment.tasks.all"
# 	],
# 	"daily": [
# 		"down_payment.tasks.daily"
# 	],
# 	"hourly": [
# 		"down_payment.tasks.hourly"
# 	],
# 	"weekly": [
# 		"down_payment.tasks.weekly"
# 	],
# 	"monthly": [
# 		"down_payment.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "down_payment.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "down_payment.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "down_payment.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["down_payment.utils.before_request"]
# after_request = ["down_payment.utils.after_request"]

# Job Events
# ----------
# before_job = ["down_payment.utils.before_job"]
# after_job = ["down_payment.utils.after_job"]

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
# 	"down_payment.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            ["module", "=", "Down Payment"]
        ]
    }
]