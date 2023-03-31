odoo.define("spp_idqueue.FormController", function (require) {
    var FormController = require("web.FormController");
    var session = require("web.session");

    FormController.include({
        willStart() {
            const sup = this._super(...arguments);
            const acl = session.user_has_group("spp_idqueue.group_g2p_id_requestor").then((hasGroup) => {
                if (this.modelName === "res.partner" && hasGroup) {
                    this.hasActionMenus = false;
                }
            });
            return Promise.all([sup, acl]);
        },
    });
});
