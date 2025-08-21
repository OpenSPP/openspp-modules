/** @odoo-module **/
// ABOUTME: Client-side logic to filter paid apps from the Apps menu
// ABOUTME: Sets the apps_menu context when accessing the Apps list

import {registry} from "@web/core/registry";
import {actionService} from "@web/webclient/actions/action_service";

// Extend the action service to add apps_menu context
const appsFilterActionService = {
    ...actionService,
    start(env, ...args) {
        const service = actionService.start(env, ...args);
        const originalDoAction = service.doAction;

        // Override doAction to add apps_menu context
        service.doAction = async function (actionRequest, options = {}) {
            // Check if this is the Apps menu action
            if (actionRequest) {
                // Handle action ID strings
                if (typeof actionRequest === "string") {
                    const appsActionIds = [
                        "base.open_module_tree",
                        "base.action_module_tree",
                        "base.action_module_immediate_install",
                    ];

                    if (appsActionIds.some((id) => actionRequest.includes(id))) {
                        options.additionalContext = options.additionalContext || {};
                        options.additionalContext.apps_menu = true;
                    }
                }
                // Handle action objects
                else if (
                    typeof actionRequest === "object" &&
                    actionRequest.res_model === "ir.module.module"
                ) {
                    // Check if we're in the Apps menu (kanban view)
                    if (actionRequest.view_mode && actionRequest.view_mode.includes("kanban")) {
                        options.additionalContext = options.additionalContext || {};
                        options.additionalContext.apps_menu = true;
                    }
                }
            }

            return originalDoAction.call(this, actionRequest, options);
        };

        return service;
    },
};

// Register the extended service
registry.category("services").add("action", appsFilterActionService, {force: true});
