app_name = "incentive_compensation"
app_title = "Incentive Compensation"
app_publisher = "Adesh Katiya"
app_description = "Commission and incentive compensation engine for ERPNext"
app_email = "adeshkatiya.dev@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "incentive_compensation",
# 		"logo": "/assets/incentive_compensation/logo.png",
# 		"title": "Incentive Compensation",
# 		"route": "/incentive_compensation",
# 		"has_permission": "incentive_compensation.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/incentive_compensation/css/incentive_compensation.css"
# app_include_js = "/assets/incentive_compensation/js/incentive_compensation.js"

# include js, css files in header of web template
# web_include_css = "/assets/incentive_compensation/css/incentive_compensation.css"
# web_include_js = "/assets/incentive_compensation/js/incentive_compensation.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "incentive_compensation/public/scss/website"

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
# app_include_icons = "incentive_compensation/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "incentive_compensation.utils.jinja_methods",
# 	"filters": "incentive_compensation.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "incentive_compensation.install.before_install"
# after_install = "incentive_compensation.install.after_install"

fixtures = [
    {
        "dt": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "Commission Manager",
                    "Commission User",
                    "Commission Payout Manager",
                ],
            ]
        ],
    }
]

# Uninstallation
# ------------

# before_uninstall = "incentive_compensation.uninstall.before_uninstall"
# after_uninstall = "incentive_compensation.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "incentive_compensation.utils.before_app_install"
# after_app_install = "incentive_compensation.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "incentive_compensation.utils.before_app_uninstall"
# after_app_uninstall = "incentive_compensation.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "incentive_compensation.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "incentive_compensation.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "on_submit": "incentive_compensation.incentive_compensation.commission_engine.commission_events.on_sales_invoice_submit",
        "on_cancel": "incentive_compensation.incentive_compensation.commission_engine.commission_events.on_sales_invoice_cancel",
    },
    "Commission Statement": {
        "validate": "incentive_compensation.incentive_compensation.commission_engine.commission_events.validate_commission_statement",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"incentive_compensation.tasks.all"
# 	],
# 	"daily": [
# 		"incentive_compensation.tasks.daily"
# 	],
# 	"hourly": [
# 		"incentive_compensation.tasks.hourly"
# 	],
# 	"weekly": [
# 		"incentive_compensation.tasks.weekly"
# 	],
# 	"monthly": [
# 		"incentive_compensation.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "incentive_compensation.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "incentive_compensation.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "incentive_compensation.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "incentive_compensation.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["incentive_compensation.utils.before_request"]
# after_request = ["incentive_compensation.utils.after_request"]

# Job Events
# ----------
# before_job = ["incentive_compensation.utils.before_job"]
# after_job = ["incentive_compensation.utils.after_job"]

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
# 	"incentive_compensation.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
