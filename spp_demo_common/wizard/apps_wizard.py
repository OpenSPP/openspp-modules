from odoo import fields, models


class SPPAPPWizard(models.TransientModel):
    _name = "spp.apps.wizard"
    _description = "SPP Apps Wizard"

    not_installed_module_ids = fields.Many2many(
        comodel_name="ir.module.module",
        string="Not Installed Modules",
    )
    missing_module_ids = fields.One2many(
        comodel_name="spp.missing.module",
        inverse_name="wizard_id",
        string="Missing Modules",
    )

    def install_modules(self):
        self.ensure_one()
        modules_to_install = self.not_installed_module_ids

        if modules_to_install:
            modules_to_install.button_immediate_install()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }


class SPPMissingModule(models.TransientModel):
    _name = "spp.missing.module"
    _description = "SPP Missing Module"

    name = fields.Char(string="Module Name", readonly=True)
    wizard_id = fields.Many2one(
        comodel_name="spp.apps.wizard",
        string="Wizard",
        readonly=True,
    )
