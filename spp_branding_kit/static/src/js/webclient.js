/** @odoo-module **/

import {WebClient} from "@web/webclient/webclient";
import {Dialog} from "@web/core/dialog/dialog";
import {patch} from "@web/core/utils/patch";
import {session} from "@web/session";

// Get branding configuration from session
const systemName = session.openspp_system_name || "OpenSPP Platform";

// Patch WebClient to use custom system name in titles
patch(WebClient.prototype, {
    setup() {
        super.setup();
        // Replace "Odoo" with custom system name in title
        this.title.setParts({zopenerp: systemName});
    },
});

// Patch Dialog to use custom system name as default title
patch(Dialog.prototype, {
    setup() {
        super.setup();
        // Set default dialog title to system name if not already set
        if (!this.props.title || this.props.title === "Odoo") {
            this.title = systemName;
        }
    },
});
