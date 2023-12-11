=========
Audit Log
=========

OpenSPP Audit Log

**Information**

This module will let you track every user's operation (create, write, unlink) on all of the records defined in Audit Rule.

Features:

* Creates an audit rule by specifying the name.
* Audit Rule can be a child or/and a parent rule.
* Operations (create, write, unlink) can be activate and deactivate.
* Operations performed by a user will be automatically recorded in the list of logs.
* Log view contains details about each operation: date, name, operation, user, old and new values of each modified field, etc.
* Action menu named 'view logs' is added on every record that will navigate to log list of specific record

Usage
=====

To create a new rule:

#. Go to ``Audit Log > Audit > Rule`` menu.
#. Click ``Create`` button.
#. To create a parent rule, leave the ``Parent Rule`` field blank.
#. To create a child rule, add value to the ``Parent Rule`` field.
#. Insert the name of the rule.
#. Check the operations you want to audit. They are already checked by default.
#. Select the model you want to be audited.

To show the list of logs:

#. Go to ``Audit Log > Audit > Log`` menu.
#. To see more details about the log, select a record.

To view logs of displayed model:

#. Select and click one record.
#. Go to ``Action > View logs``.
