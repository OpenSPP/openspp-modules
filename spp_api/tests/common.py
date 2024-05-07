from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_demo_id = cls.env["res.partner"].create(
            {
                "name": "Marc Demo",
                "company_id": cls.env.ref("base.main_company").id,
                "company_name": "YourCompany",
                "street": "3575  Buena Vista Avenue",
                "city": "Eugene",
                "state_id": cls.env.ref("base.state_us_41").id,
                "zip": "97401",
                "country_id": cls.env.ref("base.us").id,
                "tz": "Europe/Brussels",
                "email": "",
                "phone": "(441)-695-2334",
            }
        )
        cls.demo_user = cls.env["res.users"].create(
            {
                "partner_id": cls.partner_demo_id.id,
                "login": "random_demo_user",
                "password": "demo",
                "signature": "<span>-- <br/>+Mr Demo</span>",
                "company_id": cls.env.ref("base.main_company").id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("base.group_partner_manager").id,
                            cls.env.ref("base.group_allow_export").id,
                        ],
                    )
                ],
            }
        )
        cls.namespace_id = cls.env["spp_api.namespace"].create(
            {
                "name": "demo_namespace",
                "log_request": "debug",
                "log_response": "debug",
                "token": "demo_token",
                "version_name": "v2",
                "user_ids": [(4, cls.demo_user.id)],
            }
        )
