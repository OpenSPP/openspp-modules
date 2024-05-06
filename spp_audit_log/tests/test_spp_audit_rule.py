from odoo.tests.common import TransactionCase


class AuditRuleTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.model_1 = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.res_partner_rule = cls.env["spp.audit.rule"].search([("model_id", "=", cls.model_1.id)], limit=1)
        if not cls.res_partner_rule:
            cls.res_partner_rule = AuditRuleTest.create_audit_rule(
                name="Rule 1", model_id=cls.model_1.id, log_unlink=False
            )
        else:
            cls.res_partner_rule.update(
                {
                    "log_create": True,
                    "log_write": True,
                    "log_unlink": False,
                }
            )

        cls.res_partner = cls.env["res.partner"].create(
            {
                "name": "Res Partner Group",
                "phone": "+639266716911",
            }
        )

    @classmethod
    def create_audit_rule(cls, **kwargs):
        return cls.env["spp.audit.rule"].create(kwargs)

    def test_get_audit_rules(self):
        self.assertIsNotNone(self.res_partner.get_audit_rules("create").id)
        self.assertIsNotNone(self.res_partner.get_audit_rules("write").id)
        self.assertFalse(self.res_partner.get_audit_rules("unlink").id)

    def test_register_hook(self):
        self.assertTrue(self.env["spp.audit.rule"]._register_hook([self.res_partner_rule.id]))
        self.assertFalse(self.env["spp.audit.rule"]._register_hook([0]))

    def test_format_data_to_log(self):
        id_val = 1
        field = "name"
        old_name = "old name"
        new_name = "new name"
        not_included_field = "active"

        old_values = {
            "id": id_val,
            field: old_name,
            not_included_field: False,
        }
        new_values = {
            "id": id_val,
            field: new_name,
            not_included_field: True,
        }
        fields_to_log = [field]
        data = self.env["spp.audit.rule"]._format_data_to_log(old_values, new_values, fields_to_log)

        self.assertIn(id_val, data.keys())
        self.assertIn("old", data[id_val].keys())
        self.assertIn("new", data[id_val].keys())
        self.assertIn(field, data[id_val]["old"].keys())
        self.assertIn(field, data[id_val]["new"].keys())
        self.assertNotIn(not_included_field, data[id_val]["old"].keys())
        self.assertNotIn(not_included_field, data[id_val]["new"].keys())
        self.assertEqual(data[id_val]["old"][field], old_name)
        self.assertEqual(data[id_val]["new"][field], new_name)

    def test_get_audit_log_vals(self):
        res_id = 1
        method = "write"
        data = {res_id: {}}
        vals = self.res_partner_rule.get_audit_log_vals(res_id, method, data)

        self.assertIn("user_id", vals.keys())
        self.assertIn("model_id", vals.keys())
        self.assertIn("res_id", vals.keys())
        self.assertIn("method", vals.keys())
        self.assertIn("data", vals.keys())

        self.assertEqual(self.res_partner_rule._uid, vals["user_id"])
        self.assertEqual(self.res_partner_rule.model_id.id, vals["model_id"])
        self.assertEqual(res_id, vals["res_id"])
        self.assertEqual(method, vals["method"])
        self.assertEqual(repr(data[res_id]), vals["data"])
