/** @odoo-module **/

import {session} from "@web/session";

// Get telemetry settings from session
const telemetryEnabled = session.openspp_telemetry_enabled !== false;
const telemetryEndpoint = session.openspp_telemetry_endpoint || "https://telemetry.openspp.org";

// Log telemetry configuration for debugging
if (!telemetryEnabled) {
    console.log("OpenSPP: Telemetry is disabled");
} else {
    console.log("OpenSPP: Telemetry endpoint:", telemetryEndpoint);
}

// In Odoo 17, telemetry blocking is better handled at the controller level
// The backend controller in main.py handles the /publisher-warranty endpoint
// Additional frontend blocking can be added here if needed for specific AJAX calls

// Monitor XMLHttpRequest to block telemetry calls
const originalOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function (method, url, ...args) {
    // Telemetry patterns to block
    const telemetryPatterns = ["services.odoo.com", "apps.odoo.com", "iap.odoo.com", "/publisher-warranty"];

    const shouldBlock = telemetryPatterns.some((pattern) => url.includes(pattern));

    if (shouldBlock) {
        if (!telemetryEnabled) {
            console.log("OpenSPP: Blocked telemetry call to", url);
            // Return a dummy request that does nothing
            this.send = function () {
                // Intentionally empty to block telemetry
            };
            this.abort = function () {
                // Intentionally empty to block telemetry
            };
            return;
        }
        console.log("OpenSPP: Would redirect telemetry from", url, "to", telemetryEndpoint);
        // For now, block the call as redirection requires backend implementation
        this.send = function () {
            // Intentionally empty to block telemetry
        };
        this.abort = function () {
            // Intentionally empty to block telemetry
        };
        return;
    }

    return originalOpen.call(this, method, url, ...args);
};
