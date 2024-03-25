# Dynamic Partner Access Module for SPP Tickets

## Overview

The `spp_ticket_dynamic_access` module introduces a flexible and dynamic access control feature for managing
access rights to partner records in Odoo. It allows automatic adjustment of access rights for support staff
based on their assignment to tickets. This feature is particularly useful in scenarios where support staff
require temporary access to partner information to address tickets and where access should be revoked
automatically upon ticket closure.

## Features

- **Dynamic Access Control**: Automatically grant and revoke access for support staff to partner records based
  on ticket assignments.
- **Enhanced Security**: Ensure that access to sensitive partner information is strictly managed and
  temporary, reducing the risk of unauthorized access.
- **Seamless Integration**: Works seamlessly with existing Odoo modules, including CRM and Helpdesk, providing
  a cohesive experience.

## Installation

1. Clone or download the `dynamic_partner_access` module into your Odoo addons directory.
2. Update the Odoo app list by navigating to **Apps** > **Update Apps List** in your Odoo dashboard.
3. Install the module by searching for `Dynamic Partner Access` in the apps list and clicking **Install**.

## Configuration

After installation, perform the following steps to configure the module:

1. **Assign Support Staff to Group**: Ensure that users intended as support staff are assigned to the
   appropriate user group with access rights to manage tickets.
2. **Set Up Partner Access**: No additional configuration is required for partner access, as the module
   dynamically manages access based on ticket activity.

## Usage

To use the dynamic partner access feature:

1. **Create a Ticket**: Assign a ticket to a support staff member. Upon assignment, the module automatically
   grants the assigned user access to the associated partner record.
2. **Modify Ticket Assignment**: If a ticket is reassigned to another support staff member, the module updates
   access rights accordingly, granting access to the new assignee and revoking access from the previous
   assignee.
3. **Close a Ticket**: When a ticket is marked as resolved or closed, the module automatically revokes the
   assigned support staff's access to the associated partner record.
