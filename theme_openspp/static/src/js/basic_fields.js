/** @odoo-module **/

import {FieldPhone} from "web.basic_fields";
import {patch} from "web.utils";

patch(FieldPhone.prototype, "spp_custom_fields_ui/static/src/js/basic_fields.js", {
    /**
     * @override
     * @private
     */
    _onChange() {
        this.$el.css("direction", "ltr");
        this._super.apply(this, arguments);
    },

    /**
     * @override
     * @private
     */
    _onInput() {
        this.$el.css("direction", "ltr");
        this._super.apply(this, arguments);
    },
});
