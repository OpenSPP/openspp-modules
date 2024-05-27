from odoo import fields, models


class CustomOpenIDVCIssuer(models.Model):
    _inherit = "g2p.openid.vci.issuers"

    issuer_type = fields.Selection(
        selection_add=[
            (
                "GroupRegistry",
                "GroupRegistry",
            )
        ],
        ondelete={"GroupRegistry": "cascade"},
    )

    def set_from_static_file_GroupRegistry(
        self, module_name="spp_openid_vci_group", file_name="", field_name="", **kwargs
    ):
        return self.set_from_static_file_Registry(
            module_name=module_name, file_name=file_name, field_name=field_name, **kwargs
        )

    def set_default_credential_type_GroupRegistry(self):
        self.credential_type = "GroupRegistry"

    def issue_vc_GroupRegistry(self, auth_claims, credential_request):
        return self.issue_vc_Registry(auth_claims, credential_request)

    def set_default_auth_allowed_issuers_GroupRegistry(self):
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url").rstrip("/")
        endpoint = "/api/v1/security"
        self.auth_allowed_issuers = f"{web_base_url}{endpoint}"
