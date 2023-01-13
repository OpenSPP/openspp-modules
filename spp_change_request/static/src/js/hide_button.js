odoo.define("spp_change_request.view_change_request_form", function (require) {
    var FormController = require("web.FormController");
    var session = require("web.session");
    var user = session.uid;

    FormController.include({
        updateButtons: function () {
            if (this.modelName === "spp.change.request") {
                if (
                    this.renderer.state.data.state === "draft" &&
                    this.renderer.state.data.assign_to_id.data.id !== user &&
                    this.renderer.state.data.create_uid.data.id !== user
                ) {
                    this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", true);
                } else {
                    this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", false);
                }
            } else {
                this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", false);
            }
            var edit_mode = this.mode === "edit";
            this.$buttons.find(".o_form_buttons_edit").toggleClass("o_hidden", !edit_mode);
            this.$buttons.find(".o_form_buttons_view").toggleClass("o_hidden", edit_mode);
        },
    });
});
