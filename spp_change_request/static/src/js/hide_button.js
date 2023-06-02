odoo.define("spp_change_request.view_change_request_form", function (require) {
    var FormController = require("web.FormController");
    var session = require("web.session");
    var user = session.uid;

    FormController.include({
        getModelsToHide: function () {
            return ["spp.change.request"];
        },
        updateButtons: function () {
            this._super.apply(this, arguments);
            var data = this.renderer.state.data;
            if (this.getModelsToHide().includes(this.modelName)) {
                // Only for models that needs to hide edit button
                if (this.$buttons) {
                    // Check if button exists
                    this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", false);
                    if (data.state !== "draft") {
                        // Hide edit button if state is not draft
                        this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", true);
                    } else if (
                        !(
                            (data.assign_to_id &&
                                data.assign_to_id.data &&
                                data.assign_to_id.data.id === user) ||
                            (data.create_uid && data.create_uid.data && data.create_uid.data.id === user)
                        )
                    ) {
                        // If current user is neither in assign_to_id or create_uid then the edit button will hide
                        this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", true);
                    }
                    var edit_mode = this.mode === "edit";
                    this.$buttons.find(".o_form_buttons_edit").toggleClass("o_hidden", !edit_mode);
                    this.$buttons.find(".o_form_buttons_view").toggleClass("o_hidden", edit_mode);
                }
            }
        },
    });
});
