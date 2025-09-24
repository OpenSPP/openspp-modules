from odoo import _, api, fields, models


class SppStarter(models.TransientModel):
    _name = "spp.starter"
    _description = "SPP Starter"

    STATE_SELECTION = [
        ("0", "Organization Setup"),
        ("1", "Registry Setup"),
        ("2", "Chosen Registry Setup"),
    ]
    SP_MIS_STATE_SELECTION = [
        ("0", "SP-MIS"),
        ("1", "Service Points"),
        ("2", "Cash Transfer"),
        ("3", "In-Kind Transfer"),
    ]
    FARMER_STATE_SELECTION = [
        ("0", "Farmer Registry"),
    ]

    state = fields.Selection(
        selection=STATE_SELECTION,
        required=True,
        default="0",
    )
    state_spmis = fields.Selection(
        selection=SP_MIS_STATE_SELECTION,
        required=True,
        default="0",
    )
    state_farmer = fields.Selection(
        selection=FARMER_STATE_SELECTION,
        required=True,
        default="0",
    )
    is_last_step = fields.Boolean(compute="_compute_is_last_step")
    # STEP 1
    org_name = fields.Char(
        readonly=True,
        help="Identify the company for record-keeping and customization.",
    )
    org_address = fields.Char(
        readonly=True,
        help="For record-keeping and location-based features.",
    )
    org_phone = fields.Char(
        readonly=True,
        help="For contact and possibly for integrations like SMS alerts.",
    )
    org_currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
        context={"active_test": False},
        help="To set the default currency for financial transactions.",
    )
    # STEP 2
    registry_target = fields.Selection(
        selection=[
            ("spmis", "SP-MIS"),
            ("farmer", "Farmer Registry"),
        ],
        readonly=True,
        default="spmis",
        help="To customize data models and interfaces.",
    )

    location_assignment = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To decide whether geo-tagging modules are needed.",
    )
    id_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To determine if identity management modules should be installed.",
    )
    # STEP 3 SP-MIS
    sp_mis_demo_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To gauge whether demo module for SP-MIS is needed.",
    )

    # STEP 4 SP-MIS
    service_point_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To gauge whether additional logistics modules are needed.",
    )
    # STEP 5 SP-MIS
    cash_transfer_needed = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To install cash transfer modules.",
    )
    bank_details_needed = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To add functionality for storing financial information.",
    )
    # STEP 6 SP-MIS
    conducting_inkind_transfer = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="yes",
        help="To decide if modules for inventory management are needed.",
    )

    # STEP 3 Farmer Registry
    farmer_demo_management = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No"),
        ],
        readonly=True,
        default="no",
        help="To gauge whether demo module for farmer registry is needed.",
    )

    def _compute_is_last_step(self):
        for rec in self:
            if rec.registry_target == "spmis":
                rec.is_last_step = (
                    rec.state == rec.STATE_SELECTION[-1][0] and rec.state_spmis == rec.SP_MIS_STATE_SELECTION[-1][0]
                )
            if rec.registry_target == "farmer":
                rec.is_last_step = (
                    rec.state == rec.STATE_SELECTION[-1][0] and rec.state_farmer == rec.FARMER_STATE_SELECTION[-1][0]
                )

    def action_done(self):
        self.ensure_one()
        self._adjust_main_company_details()
        modules = self._install_modules()
        modules.button_immediate_install()
        self._remove_default_products_if_needed()
        self._remove_fake_apps_menu()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_last_state(self):
        self.ensure_one()
        state_int = int(self.state)
        if state_int == len(self.STATE_SELECTION) - 1:
            if self.registry_target == "spmis" and int(self.state_spmis) > 0:
                self.state_spmis = str(int(self.state_spmis) - 1)
            elif self.registry_target == "farmer" and int(self.state_farmer) > 0:
                self.state_farmer = str(int(self.state_farmer) - 1)
            else:
                self.state = str(state_int - 1)
        else:
            self.state = str(max(state_int - 1, 0))
        return self._reopen()

    def action_next_state(self):
        self.ensure_one()
        state_int = int(self.state)
        if state_int < len(self.STATE_SELECTION) - 1:
            self.state = str(state_int + 1)
        if state_int == len(self.STATE_SELECTION) - 1:
            if self.registry_target == "spmis":
                self.state_spmis = str(int(self.state_spmis) + 1)
            if self.registry_target == "farmer":
                self.state_farmer = str(int(self.state_farmer) + 1)
        return self._reopen()

    def _adjust_main_company_details(self):
        self.ensure_one()
        self.env.company.sudo().write(
            {
                "name": self.org_name,
                "street": self.org_address,
                "phone": self.org_phone,
                "currency_id": self.org_currency_id.id,
            }
        )

    def _find_module(self, module_name):
        return self.env.ref(f"base.module_{module_name}", raise_if_not_found=False)

    def _add_module_if_found(self, res, module_name):
        if module := self._find_module(module_name):
            res |= module
        return res

    def _install_spmis_base_modules(self, res):
        for module_name in [
            "spp_base_spmis",
            "spp_programs",
            "spp_change_request",
            "spp_change_request_change_info",
            "spp_event_data",
        ]:
            res = self._add_module_if_found(res, module_name)
        return res

    def _install_spmis_demo_modules(self, res):
        if self.sp_mis_demo_management == "yes":
            for module_name in ["spp_base_demo", "spp_mis_demo"]:
                res = self._add_module_if_found(res, module_name)
        return res

    def _install_spmis_feature_modules(self, res):
        module_map = {
            "location_assignment": "spp_area",
            "service_point_management": "spp_service_points",
            "cash_transfer_needed": "spp_entitlement_cash",
            "bank_details_needed": "g2p_bank",
            "conducting_inkind_transfer": "spp_entitlement_in_kind",
        }
        for field, module_name in module_map.items():
            if getattr(self, field) == "yes":
                res = self._add_module_if_found(res, module_name)
        return res

    def _install_farmer_modules(self, res):
        res = self._add_module_if_found(res, "spp_farmer_registry_base")
        if self.location_assignment == "yes":
            res = self._add_module_if_found(res, "spp_area_gis")
        if self.farmer_demo_management == "yes":
            for module_name in ["spp_base_demo", "spp_farmer_registry_demo", "spp_programs"]:
                res = self._add_module_if_found(res, module_name)
        return res

    def _install_modules(self):
        self.ensure_one()
        res = self._find_module("theme_openspp_muk") or self.env["ir.module.module"]

        if self.registry_target == "spmis":
            res = self._install_spmis_base_modules(res)
            res = self._install_spmis_demo_modules(res)
            res = self._install_spmis_feature_modules(res)
        elif self.registry_target == "farmer":
            res = self._install_farmer_modules(res)

        if self.id_management == "yes":
            res = self._add_module_if_found(res, "spp_idpass")

        return res

    def _remove_default_products_if_needed(self):
        self.ensure_one()
        if self.conducting_inkind_transfer != "yes" or "product.template" not in self.env:
            return
        all_products = self.env["product.template"].sudo().search([])
        return all_products.write({"active": False})

    @api.model
    def _remove_fake_apps_menu(self):
        return self.env["ir.config_parameter"].sudo().set_param("spp_starter.show_spp_starter", "False")

    def _reopen(self):
        self.ensure_one()
        return {
            "name": _(self._description),
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
