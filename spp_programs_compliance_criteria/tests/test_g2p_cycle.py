from odoo.exceptions import ValidationError

from . import common


class TestG2pCycle(common.Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.individual_1 = cls._create_individual({"name": "Individual 1"})
        cls.individual_2 = cls._create_individual({"name": "Individual 2"})
        cls.individual_3 = cls._create_individual({"name": "Individual 3"})
        cls._test = cls.program_create_wizard(
            {
                "target_type": "individual",
                "compliance_criteria": True,
                "compliance_kind": "g2p.program_membership.manager.default",
                "compliance_domain": f"[['id', '=', {cls.individual_3.id}]]",
                "import_beneficiaries": "yes",
            }
        )
        action = cls._test.create_program()
        cls.program = cls.env["g2p.program"].browse(action["res_id"])

    @classmethod
    def _create_individual(self, vals):
        vals.update(
            {
                "is_registrant": True,
                "is_group": False,
            }
        )
        return self.env["res.partner"].create(vals)

    def _set_filtering_mechanism(self, value):
        if value not in ["0", "1", "2"]:
            value = "0"
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .set_param(
                "spp_programs_compliance_criteria.beneficiaries_automated_filtering_mechanism",
                value,
            )
        )

    def test_01_create_cycle_without_automated_filtering_mechanism(self):
        self._set_filtering_mechanism("100")
        self.program.create_new_cycle()
        cycle = self.program.cycle_ids[0]
        self.assertTrue(
            len(self.program.program_membership_ids) == len(cycle.cycle_membership_ids),
            "Cycle membership should be copied from program!",
        )
        self.assertListEqual(
            self.program.program_membership_ids.mapped("state"),
            cycle.cycle_membership_ids.mapped("state"),
            "Cycle membership should be copied from program!",
        )
        cycle.prepare_entitlement()
        self.assertTrue(
            len(cycle.cycle_membership_ids) == len(cycle.entitlement_ids),
            "One entitlement should be generated for each membership!",
        )
        self.assertTrue(
            cycle.allow_filter_compliance_criteria,
            "Program having compliance manager should allow its cycles to filter!",
        )
        cycle.action_filter_beneficiaries_by_compliance_criteria()
        self.assertTrue(
            len(cycle.cycle_membership_ids)
            > len(cycle.cycle_membership_ids.filtered(lambda cm: cm.state == "enrolled")),
            "Number of enrolled membership should be reduced after filtering!",
        )

    def test_02_create_cycle_automated_filtering_on_entitlement_creating(self):
        self._set_filtering_mechanism("2")
        self.program.create_new_cycle()
        cycle = self.program.cycle_ids[0]
        self.assertTrue(
            len(self.program.program_membership_ids) == len(cycle.cycle_membership_ids),
            "Cycle membership should be copied from program!",
        )
        self.assertListEqual(
            self.program.program_membership_ids.mapped("state"),
            cycle.cycle_membership_ids.mapped("state"),
            "Cycle membership should be copied from program!",
        )
        cycle.prepare_entitlement()
        self.assertTrue(
            len(cycle.cycle_membership_ids) > len(cycle.entitlement_ids),
            "Entitlement should only be created for member which satisfied the condition of compliance manager!",
        )

    def test_03_create_cycle_automated_filtering_on_membership_creating(self):
        self._set_filtering_mechanism("1")
        self.program.create_new_cycle()
        cycle = self.program.cycle_ids[0]
        self.assertTrue(
            len(self.program.program_membership_ids) > len(cycle.cycle_membership_ids),
            "Cycle membership should not be copied from program!",
        )
        cycle.prepare_entitlement()
        self.assertTrue(
            len(cycle.cycle_membership_ids) == len(cycle.entitlement_ids),
            "One entitlement should be generated for each membership!",
        )

    def test_04_other_test(self):
        self.program.create_new_cycle()
        cycle = self.program.cycle_ids[0]
        cycle.state = "approved"
        cycle.action_filter_beneficiaries_by_compliance_criteria()
        cycle.state = "to_approve"
        self.program.write({"compliance_managers": [(5, 0, 0)]})
        err_msg = "^Cycle is not on correct condition to filter by compliance!$"
        with self.assertRaisesRegex(ValidationError, err_msg):
            cycle.action_filter_beneficiaries_by_compliance_criteria()
