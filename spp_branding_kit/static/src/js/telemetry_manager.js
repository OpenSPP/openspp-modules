/** @odoo-module **/

import {session} from "@web/session";

// Get telemetry settings from session
const telemetryEnabled = session.openspp_telemetry_enabled !== false;
const telemetryEndpoint = session.openspp_telemetry_endpoint || "https://telemetry.openspp.org";

// Log telemetry configuration for debugging
if (telemetryEnabled) {
    console.log("OpenSPP: Telemetry endpoint:", telemetryEndpoint);
} else {
    console.log("OpenSPP: Telemetry is disabled");
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
            // Replace send/abort with harmless stubs
            this.send = function () {
                return false;
            };
            this.abort = function () {
                return null;
            };
            return;
        }
        // When telemetry is enabled, do not intercept; server handles /publisher-warranty
        // Optionally, you could redirect here, but we keep the default behavior
    }

    return originalOpen.call(this, method, url, ...args);
};
