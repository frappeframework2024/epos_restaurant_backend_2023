from . import __version__ as app_version
import frappe
app_name = "epos_restaurant_2023"
app_title = "ePOS Restaurant"
app_publisher = "Tes Pheakdey"
app_description = "epos restaurant 2023 by ESTC "
app_email = "pheakdey.micronet@gmail.com"
app_license = "MIT"



# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/epos_restaurant_2023/css/epos_restaurant_2023.css"
app_include_js = [
    "/assets/epos_restaurant_2023/js/epos_restaurant_2023.js",
    "/assets/epos_restaurant_2023/js/echarts.min.js",
    "/assets/epos_restaurant_2023/js/html2canvas.min.js",
]
 

additional_print_settings =["compact_item_print"]



# include js, css files in header of web template
# web_include_css = "/assets/epos_restaurant_2023/css/epos_restaurant_2023.css"
# web_include_js = "/assets/epos_restaurant_2023/js/epos_restaurant_2023.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "epos_restaurant_2023/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_list_js = {"Translation": "public/js/translation_list.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

#add methods and filters to jinja environment
jinja = {
	"methods": [
        "epos_restaurant_2023.api.jinja_filters.get_total",
        "epos_restaurant_2023.api.jinja_filters.get_exchange_rate",
        "epos_restaurant_2023.api.jinja_filters.get_combo_product_by_kitchen_group",
    ],
    "filters": [
                "epos_restaurant_2023.api.jinja_filters.unique",
                "epos_restaurant_2023.api.jinja_filters.format_currency",
                "epos_restaurant_2023.api.jinja_filters.format_second_currency",
                "epos_restaurant_2023.api.jinja_filters.to_json",
            
            ], 
}   


# Installation
# ------------

# before_install = "epos_restaurant_2023.install.before_install"
# after_install = "epos_restaurant_2023.install.after_install"

before_migrate =[
    "epos_restaurant_2023.migrate.before_migrate" ,
]
after_migrate = [
    "epos_restaurant_2023.migrate.after_migrate",
    "epos_restaurant_2023.store_procedures.execute.execute"
]
 
# Uninstallation
# ------------

# before_uninstall = "epos_restaurant_2023.uninstall.before_uninstall"
# after_uninstall = "epos_restaurant_2023.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "epos_restaurant_2023.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Employee": "epos_restaurant_2023.query_permission.get_employee_permission"
}
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_update": [
            "epos_restaurant_2023.api.utils.generate_data_for_sync_record",
            "epos_restaurant_2023.api.utils.sync_data_to_server_on_submit",
              "epos_restaurant_2023.api.override.set_custom_timestamps"
        ],
        "after_rename": [
                "epos_restaurant_2023.api.utils.generate_data_for_sync_record_on_rename",
                ],
        "on_trash": [
            "epos_restaurant_2023.api.utils.generate_data_for_sync_record_on_delete"
        ],
        "on_submit":[
            "epos_restaurant_2023.api.utils.sync_data_to_server_on_submit",
            "epos_restaurant_2023.api.override.set_custom_timestamps"
            ],
        "validate":[
            "epos_restaurant_2023.api.utils.validate_queue_job_status",
            "epos_restaurant_2023.api.override.set_custom_timestamps"
        ],
        "before_insert":[
                "epos_restaurant_2023.api.override.set_custom_timestamps"
        ],
        "before_save":[
                "epos_restaurant_2023.api.override.set_custom_timestamps"
        ]
	},
    "Comment":{
        "after_insert":"epos_restaurant_2023.api.utils.sync_comment_to_server"
    },
    "Module Profile":{
        "on_update":"epos_restaurant_2023.override_methods.module_profile.on_update"
    },
}


def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Cache-Control"] = "no-cache"
    return response



#Scheduled Tasks
#---------------

scheduler_events = {
    "cron": {
      "*/1 * * * *": [
            "epos_restaurant_2023.api.schedule_task.generate_audit_trail_from_version",
            "epos_restaurant_2023.api.sync_api.get_all_data_for_sync_from_server",
            "epos_restaurant_2023.configuration.doctype.schedule_job_config.schedule_job_config.check_custom_schedule",
        ],

        "*/5 * * * *": [
            "epos_restaurant_2023.api.utils.re_run_fail_jobs",
            "epos_restaurant_2023.api.utils.update_temp_menu_product_photo_schedule"
		],

        "*/30 * * * *":[
            "epos_restaurant_2023.api.quickbook_intergration.config.refresh_token"
        ],
        "0 */12 * * *":[
            "epos_restaurant_2023.api.ftp_backup.execute_backup_command",
            "epos_restaurant_2023.api.api.update_summary_to_customers"
        ],
        
        "0 1 * * *":[
            "epos_restaurant_2023.api.archive_data.delete_archive_transaction", # 1 AM every daty
           
        ],

        "0 */3 * * *":[ ##Every 3 hours at minute 0
            "epos_restaurant_2023.api.api.run_get_update_pos_station_license_enqueue"
        ]

	},
    "all": [
		"epos_restaurant_2023.api.custom_reminder.send_reminders",
        "epos_restaurant_2023.api.ftp_backup.run_on_startup",
	],
    "daily":[
        "epos_restaurant_2023.api.coupon.update_manager_coupon_status",
        "epos_restaurant_2023.api.archive_data.archive_transactions"
    ],
    "weekly":[
        "epos_restaurant_2023.api.coupon_transaction_backup_db.delete_last_30_days_data"
    ]
   

    
}




# Testing
# -------

# before_tests = "epos_restaurant_2023.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	# "frappe.desk.doctype.event.event.get_events": "epos_restaurant_2023.event.get_events"
    "frappe.desk.desktop.get_workspace_sidebar_items" : "epos_restaurant_2023.api.api.get_workspace_sidebar_items",
    "frappe.desk.query_report.export_query" : "epos_restaurant_2023.api.data_export.data_export_override.export_to_excel"
}
 
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "epos_restaurant_2023.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"epos_restaurant_2023.auth.validate"
# ]

on_login = "epos_restaurant_2023.api.utils.successful_login"

fixtures = [
   
    {"dt": "Province"},
    {"dt": "Numbers"},
    {"dt": "Custom Field"},
    {"dt": "Predefine Data"},
    {"dt": "Custom HTML Block"},
    {"dt": "POS Translation","filters": [["is_standard", "=", "1"]]},
    {"dt": "Predefine SPA Commission Code","filters": [["is_standard", "=", "1"]]},

    {"dt": "Print Style","filters": [["name", "=", "Default Style"]]},
    {"dt": "Print Format","filters": [["name", "IN", ["Commercial Tax Invoice A4"]]]},
    

    ## workflow
    {"dt": "Workflow Action Master"},
    {"dt": "Workflow State"},
    {"dt": "Workflow"},
    {"dt": "Translation"},
    {"dt": "Video Help Document"}
    
]

website_route_rules = [
        {'from_route': '/epos_frontend/<path:app_path>', 'to_route': 'epos_frontend'},
        
        {'from_route': '/emenu/<path:app_path>', 'to_route': 'emenu'},
        {'from_route': '/gym/<path:app_path>', 'to_route': 'gym'},
        {'from_route': '/login/<path:app_path>', 'to_route': 'epos_frontend'},
        {'from_route': '/embed/<path:app_path>', 'to_route': 'embed'},
        {'from_route': '/e-menu/<path:app_path>', 'to_route': 'e-menu'}, 
       
      
         
]

# website_route_rules = [{'from_route': '/embed/<path:app_path>', 'to_route': 'embed'},]

