import os
import re
import sys
import xmlrpc.client

# Sanitize user inputs


def sanitize(input_string):
    return re.sub(r"[^a-zA-Z0-9 ]", "", input_string)


# Ensure the URL is correctly formatted
url = os.getenv("ODOO_URL")
if not url.startswith("http://") and not url.startswith("https://"):
    print("Error: ODOO_URL should start with http:// or https://")
    sys.exit(1)

db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")  # Odoo login username
password = os.getenv("ODOO_PASSWORD")  # API Key is used
project_name = "OpenSPP"  # Project name in Odoo

# GitHub issue data, passed as script arguments and sanitized
issue_title = sanitize(sys.argv[1])
issue_body = sanitize(sys.argv[2])
github_issue_id = sanitize(sys.argv[3])  # Unique GitHub Issue ID

# XML-RPC endpoints for Odoo
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Authenticate with Odoo
uid = common.authenticate(db, username, password, {})

# Search for the project by name to get its ID
project_id = models.execute_kw(
    db, uid, password, "project.project", "search", [[["name", "=", project_name]]], {"limit": 1}
)

if not project_id:
    print("Project not found")
    sys.exit(1)

# Check if a task with the given GitHub issue ID already exists
task_id = models.execute_kw(
    db, uid, password, "project.task", "search", [[["x_github_issue_id", "=", github_issue_id]]], {"limit": 1}
)

if task_id:
    # Update the existing task
    models.execute_kw(
        db,
        uid,
        password,
        "project.task",
        "write",
        [
            task_id,
            {
                "name": issue_title,
                "description": issue_body,
            },
        ],
    )
    print(f"Task updated with ID: {task_id[0]}")
else:
    # Create a new task
    task_id = models.execute_kw(
        db,
        uid,
        password,
        "project.task",
        "create",
        [
            {
                "name": issue_title,
                "description": issue_body,
                "project_id": project_id[0],
                "x_github_issue_id": github_issue_id,  # Set the GitHub issue ID
            }
        ],
    )
    print(f"Task created with ID: {task_id}")
