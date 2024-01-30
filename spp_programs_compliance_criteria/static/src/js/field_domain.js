// Web.basic_fields module is already deprecated in odoo 17, need to find a way to do this in odoo 17

odoo.define("spp_programs_compliance_criteria.field_domain", function (require) {
    const {FieldDomain} = require("web.basic_fields");

    FieldDomain.include({
        init: function () {
            this._super.apply(this, arguments);
            this.hideResult = this.nodeOptions.hide_result;
        },

        _replaceContent: function () {
            this._super.apply(this, arguments);
            if (this.hideResult) {
                this.$el.find(".fa-arrow-right").remove();
                this.$el.find(".o_domain_show_selection_button").remove();
                this.$el.find(".o_refresh_count").remove();
            }
        },
    });
});
