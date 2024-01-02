import xmlrpc.client
import os
import sys

# Ensure the URL is correctly formatted
url = os.getenv('ODOO_URL')
if not url.startswith('http://') and not url.startswith('https://'):
    print("Error: ODOO_URL should start with http:// or https://")
    sys.exit(1)

db = os.getenv('ODOO_DB')
username = os.getenv('ODOO_USERNAME')  # Odoo login username
password = os.getenv('ODOO_PASSWORD')  # Odoo login password
project_name = 'test_proj'  # Project name in Odoo

# GitHub issue data, passed as script arguments
issue_title = sys.argv[1]
issue_body = sys.argv[2]

# XML-RPC endpoints for Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Authenticate with Odoo
uid = common.authenticate(db, username, password, {})

# Search for the project by name to get its ID
project_id = models.execute_kw(db, uid, password,
    'project.project', 'search',
    [[['name', '=', project_name]]],
    {'limit': 1})

if not project_id:
    print("Project not found")
    sys.exit(1)

# Generate a unique XML ID for the task
# This could be based on the GitHub issue ID or another unique identifier
xml_id = f'github_{issue_title.replace(" ", "_").lower()}'

# Create a task associated with the project
task_id = models.execute_kw(db, uid, password, 'project.task', 'create', [{
    'name': issue_title,
    'description': issue_body,
    'project_id': project_id[0],  # Assuming the project ID is the first in the list
    'xml_id': xml_id,  # Set the unique XML ID for the task
}])

print(f"Task created with ID: {task_id} and XML ID: {xml_id}")
