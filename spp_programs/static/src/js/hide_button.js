odoo.define("g2p_programs.view_cycle_form", function (require) {
    var FormController = require("web.FormController");
    const hide_states = ["approved", "distributed", "cancelled", "ended"];

    FormController.include({
        updateButtons: function () {
            this._super.apply(this, arguments);

            if (
                this.modelName === "g2p.cycle" &&
                this.$buttons &&
                this.renderer.state.data.state &&
                hide_states.includes(this.renderer.state.data.state)
            ) {
                this.$buttons.find(".o_form_button_edit").toggleClass("o_hidden", true);
                var edit_mode = this.mode === "edit";
                this.$buttons.find(".o_form_buttons_edit").toggleClass("o_hidden", !edit_mode);
                this.$buttons.find(".o_form_buttons_view").toggleClass("o_hidden", edit_mode);
            }
        },
    });
});
