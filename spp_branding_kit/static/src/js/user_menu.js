/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";
import {session} from "@web/session";

const userMenuRegistry = registry.category("user_menuitems");

// Get configuration from session
const docUrl = session.openspp_documentation_url || "https://docs.openspp.org";
const supportUrl = session.openspp_support_url || "https://openspp.org";

// Remove "My odoo.com account" if it exists
if (userMenuRegistry.contains("odoo_account")) {
    userMenuRegistry.remove("odoo_account");
}

// Override documentation item
if (userMenuRegistry.contains("documentation")) {
    userMenuRegistry.remove("documentation");
}
userMenuRegistry.add("documentation", function () {
    return {
        type: "item",
        id: "documentation",
        description: _t("OpenSPP Documentation"),
        callback: () => {
            browser.open(docUrl, "_blank");
        },
        sequence: 10,
    };
});

// Override support item
if (userMenuRegistry.contains("support")) {
    userMenuRegistry.remove("support");
}
userMenuRegistry.add("support", function () {
    return {
        type: "item",
        id: "support",
        description: _t("OpenSPP Support"),
        callback: () => {
            browser.open(supportUrl, "_blank");
        },
        sequence: 20,
    };
});
