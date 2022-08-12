import datetime
import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class ProgramTestIDEligibilityDeduplicate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        _logger.info("Program Testing: SETUP INITIALIZED")
        super(ProgramTestIDEligibilityDeduplicate, cls).setUpClass()

        # Initial Setup of Variables
        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "family_name": "Doe",
                "given_name": "John",
                "name": "John Doe",
                "is_group": False,
            }
        )
        cls.registrant_2 = cls.env["res.partner"].create(
            {
                "family_name": "Doe",
                "given_name": "Jane",
                "name": "Jane Doe",
                "is_group": False,
            }
        )
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
            }
        )
        cls.group_2 = cls.env["res.partner"].create(
            {
                "name": "Group 2",
                "is_group": True,
            }
        )

        currency_id = (
            cls.env.user.company_id.currency_id
            and cls.env.user.company_id.currency_id.id
            or None
        )

        cls.program_1_id = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 1",
                "currency_id": currency_id,
                "amount_per_cycle": 20,
                "amount_per_individual_in_group": 10,
            }
        )

        # Add Program
        program_1_form = cls.program_1_id.create_program()
        program_1_id = program_1_form["res_id"]
        cls.program_1 = cls.env["g2p.program"].search([("id", "=", program_1_id)])
        if cls.program_1:
            _logger.info(
                "Program Testing: Created Program 1 with ID: %s" % cls.program_1.id
            )
        cls.program_2_id = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Test Program 2",
                "currency_id": currency_id,
                "amount_per_cycle": 100,
                "amount_per_individual_in_group": 10,
            }
        )
        program_2_form = cls.program_2_id.create_program()
        program_2_id = program_2_form["res_id"]
        cls.program_2 = cls.env["g2p.program"].search([("id", "=", program_2_id)])
        if cls.program_2:
            _logger.info(
                "Program Testing: Created Program 2 with ID: %s" % cls.program_2.id
            )

        cls.program_1.write({"target_type": "individual"})
        cls.program_2.write({"target_type": "group"})

        # Add Beneficiaries
        _logger.info(
            "Program Testing: Adding Program: %s, Beneficiaries: %s"
            % (cls.program_1.name, cls.registrant_1.name)
        )
        cls.program_1.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.registrant_1.id})]}
        )
        cls.program_1.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.registrant_2.id})]}
        )
        if cls.program_1.program_membership_ids:
            _logger.info(
                "Program Testing: Added Program: %s, Beneficiaries: %s"
                % (
                    cls.program_1.name,
                    cls.program_1.program_membership_ids[0].partner_id.name,
                )
            )

        _logger.info(
            "Program Testing: Adding Program: %s, Beneficiaries (Group): %s"
            % (cls.program_2.name, cls.group_1.name)
        )
        cls.program_2.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.group_1.id})]}
        )
        cls.program_2.write(
            {"program_membership_ids": [(0, 0, {"partner_id": cls.group_2.id})]}
        )
        if cls.program_2.program_membership_ids:
            _logger.info(
                "Program Testing: Added Program: %s, Beneficiaries: %s"
                % (
                    cls.program_2.name,
                    cls.program_2.program_membership_ids[0].partner_id.name,
                )
            )
        # Add ID Eligibility Manager
        _logger.info("Program Testing: Adding ID Eligibility Manager For Program 1")

        cls.manager_1 = cls.env["g2p.program_membership.manager.id_dedup"].create(
            {
                "name": "ID Manager 1",
                "program_id": cls.program_1.id,
            }
        )
        cls.program_1.write(
            {
                "eligibility_managers": [
                    (
                        0,
                        0,
                        {
                            "program_id": cls.program_1.id,
                            "manager_ref_id": "g2p.program_membership.manager.id_dedup, %s"
                            % cls.manager_1.id,
                            "manager_id": cls.manager_1.id,
                        },
                    )
                ]
            }
        )
        if cls.program_1.eligibility_managers:
            _logger.info(
                "Program Testing: Added Program: %s, Eligibility Manager: %s"
                % (
                    cls.program_1.name,
                    cls.program_1.eligibility_managers[1].display_name,
                )
            )

        _logger.info("Program Testing: Adding ID Eligibility Manager For Program 2")

        cls.manager_2 = cls.env["g2p.program_membership.manager.id_dedup"].create(
            {
                "name": "ID Manager 2",
                "program_id": cls.program_2.id,
            }
        )
        cls.program_2.write(
            {
                "eligibility_managers": [
                    (
                        0,
                        0,
                        {
                            "program_id": cls.program_2.id,
                            "manager_ref_id": "g2p.program_membership.manager.id_dedup, %s"
                            % cls.manager_2.id,
                            "manager_id": cls.manager_2.id,
                        },
                    )
                ]
            }
        )
        if cls.program_2.eligibility_managers:
            _logger.info(
                "Program Testing: Added Program: %s, Eligibility Manager: %s"
                % (
                    cls.program_2.name,
                    cls.program_2.eligibility_managers[1].display_name,
                )
            )

        # Enroll Beneficiaries without ID expecting NONE will be enrolled
        _logger.info(
            "Program Testing: Program %s Beneficiaries Enrollment: %s Expecting NONE will be enrolled"
            % (
                cls.program_1.name,
                cls.program_1.program_membership_ids[0].partner_id.name,
            )
        )
        cls.program_1.enroll_eligible_registrants()
        if cls.program_1.program_membership_ids[0].state == "enrolled":
            _logger.info(
                "Program Testing: Program %s Beneficiaries Enrolled: %s"
                % (
                    cls.program_1.name,
                    cls.program_1.program_membership_ids[0].partner_id.name,
                )
            )
        else:
            _logger.info("Program Testing: NONE Enrolled in %s" % cls.program_1.name)
        _logger.info(
            "Program Testing: Program %s Beneficiaries Enrollment: %s Expecting NONE will be enrolled"
            % (
                cls.program_2.name,
                cls.program_2.program_membership_ids[0].partner_id.name,
            )
        )
        cls.program_2.enroll_eligible_registrants()
        if cls.program_2.program_membership_ids[0].state == "enrolled":
            _logger.info(
                "Program Testing: Program %s Beneficiaries Enrolled: %s"
                % (
                    cls.program_2.name,
                    cls.program_2.program_membership_ids[0].partner_id.name,
                )
            )
        else:
            _logger.info("Program Testing: NONE Enrolled in %s" % cls.program_2.name)

        # Beneficiaries Add IDS
        current_date = datetime.datetime.now().date()
        expiry_date = current_date + datetime.timedelta(days=7)

        _logger.info("Program Testing: Adding Testing ID Type")

        cls.idtype = cls.env["g2p.id.type"].create(
            {
                "name": "Testing ID Type",
            }
        )
        if len(cls.idtype) > 0:
            _logger.info("Program Testing: Testing ID Type ADDED")
            _logger.info("Program Testing: Adding IDS for %s" % cls.registrant_1.name)
            cls.registrant_1.write(
                {
                    "reg_ids": [
                        (
                            0,
                            0,
                            {
                                "registrant": cls.registrant_1.id,
                                "id_type": cls.idtype.id,
                                "value": "123456789",
                                "expiry_date": expiry_date,
                            },
                        )
                    ]
                }
            )
            if len(cls.registrant_1.reg_ids) > 0:
                _logger.info(
                    "Program Testing: IDS for %s: ADDED" % cls.registrant_1.name
                )
            else:
                _logger.info(
                    "Program Testing: IDS for %s: FAILED" % cls.registrant_1.name
                )
            _logger.info("Program Testing: Adding IDS for %s" % cls.registrant_2.name)
            cls.registrant_2.write(
                {
                    "reg_ids": [
                        (
                            0,
                            0,
                            {
                                "registrant": cls.registrant_1.id,
                                "id_type": cls.idtype.id,
                                "value": "123456789",
                                "expiry_date": expiry_date,
                            },
                        )
                    ]
                }
            )
            if len(cls.registrant_2.reg_ids) > 0:
                _logger.info(
                    "Program Testing: IDS for %s: ADDED" % cls.registrant_2.name
                )
            else:
                _logger.info(
                    "Program Testing: IDS for %s: FAILED" % cls.registrant_2.name
                )
            _logger.info("Program Testing: Adding IDS for %s" % cls.group_1.name)
            cls.group_1.write(
                {
                    "reg_ids": [
                        (
                            0,
                            0,
                            {
                                "registrant": cls.group_1.id,
                                "id_type": cls.idtype.id,
                                "value": "123456789",
                                "expiry_date": expiry_date,
                            },
                        )
                    ]
                }
            )
            if len(cls.group_1.reg_ids) > 0:
                _logger.info("Program Testing: IDS for %s: ADDED" % cls.group_1.name)
            else:
                _logger.info("Program Testing: IDS for %s: FAILED" % cls.group_1.name)
            _logger.info("Program Testing: Adding IDS for %s" % cls.group_2.name)
            cls.group_2.write(
                {
                    "reg_ids": [
                        (
                            0,
                            0,
                            {
                                "registrant": cls.group_2.id,
                                "id_type": cls.idtype.id,
                                "value": "123456789",
                                "expiry_date": expiry_date,
                            },
                        )
                    ]
                }
            )
            if len(cls.group_2.reg_ids) > 0:
                _logger.info("Program Testing: IDS for %s: ADDED" % cls.group_2.name)
            else:
                _logger.info("Program Testing: IDS for %s: FAILED" % cls.group_2.name)
        else:
            _logger.info("Program Testing: Adding Testing ID Type FAILED")

        # Try Enrolling now when IDs has been ADDED
        _logger.info(
            "Program Testing: RETRY Program %s Beneficiaries Enrollment: %s Expecting %s to be enrolled"
            % (
                cls.program_1.name,
                cls.program_1.program_membership_ids,
                cls.program_1.program_membership_ids,
            )
        )
        cls.program_1.enroll_eligible_registrants()
        if cls.program_1.program_membership_ids[0].state == "enrolled":
            _logger.info(
                "Program Testing: Program %s Beneficiaries Enrolled: %s"
                % (
                    cls.program_1.name,
                    cls.program_1.program_membership_ids,
                )
            )
        else:
            _logger.info("Program Testing: NONE Enrolled in %s" % cls.program_1.name)
        _logger.info(
            "Program Testing: RETRY Program %s Beneficiaries Enrollment: %s Expecting %s to be enrolled"
            % (
                cls.program_2.name,
                cls.program_2.program_membership_ids,
                cls.program_2.program_membership_ids,
            )
        )
        cls.program_2.enroll_eligible_registrants()
        if cls.program_2.program_membership_ids[0].state == "enrolled":
            _logger.info(
                "Program Testing: Program %s Beneficiaries Enrolled: %s"
                % (
                    cls.program_2.name,
                    cls.program_2.program_membership_ids,
                )
            )
        else:
            _logger.info("Program Testing: NONE Enrolled in %s" % cls.program_2.name)

    def test_01_deduplication(self):
        # Test the Deduplication on the Programs now with ID Deduplication Managers

        # Add first the ID Deduplication Manager
        _logger.info(
            "Program Testing: Adding ID Deduplication Manager For Program %s"
            % self.program_1.name
        )

        self.manager_1 = self.env["g2p.deduplication.manager.id_dedup"].create(
            {
                "name": "ID Manager 1",
                "program_id": self.program_1.id,
                "supported_id_document_types": [(4, self.idtype.id)],
            }
        )
        if self.manager_1:
            _logger.info(
                "Program Testing: Deduplication Manager For Program %s ADDED"
                % self.program_1.name
            )
            _logger.info(
                "Program Testing: Assigining Deduplication Manager %s For Program %s"
                % (self.manager_1.name, self.program_1.name)
            )

            self.program_1.write(
                {
                    "deduplication_managers": [
                        (
                            0,
                            0,
                            {
                                "program_id": self.program_1.id,
                                "manager_ref_id": "g2p.deduplication.manager.id_dedup, %s"
                                % self.manager_1.id,
                                "manager_id": self.manager_1.id,
                            },
                        )
                    ]
                }
            )
            if len(self.program_1.deduplication_managers) > 0:
                _logger.info(
                    "Program Testing: Deduplication Manager For Program %s ASSIGNED"
                    % self.program_1.name
                )
                _logger.info(
                    "Program Testing: Program: %s, Checking Deduplication"
                    % self.program_1.name
                )
                self.program_1.deduplicate_beneficiaries()
                _logger.info(
                    "Program Testing: Program: %s, Deduplications Count: %s"
                    % (self.program_1.name, self.program_1.duplicate_membership_count)
                )
            else:
                _logger.info(
                    "Program Testing: Adding Deduplication Manager For Program %s FAILED"
                    % self.program_1.name
                )

        else:
            _logger.info(
                "Program Testing: Adding Deduplication Manager For Program %s FAILED"
                % self.program_1.name
            )

        # Add first the ID Deduplication Manager

        _logger.info(
            "Program Testing: Adding ID Deduplication Manager For Program %s"
            % self.program_2.name
        )

        self.manager_2 = self.env["g2p.deduplication.manager.id_dedup"].create(
            {
                "name": "ID Manager 2",
                "program_id": self.program_2.id,
                "supported_id_document_types": [(4, self.idtype.id)],
            }
        )
        if self.manager_2:
            _logger.info(
                "Program Testing: Deduplication Manager For Program %s ADDED"
                % self.program_2.name
            )
            _logger.info(
                "Program Testing: Assigining Deduplication Manager %s For Program %s"
                % (self.manager_2.name, self.program_2.name)
            )

            self.program_2.write(
                {
                    "deduplication_managers": [
                        (
                            0,
                            0,
                            {
                                "program_id": self.program_2.id,
                                "manager_ref_id": "g2p.deduplication.manager.id_dedup, %s"
                                % self.manager_2.id,
                                "manager_id": self.manager_2.id,
                            },
                        )
                    ]
                }
            )
            # Add Members to the Group with Duplicate IDs
            self.group_1.write(
                {"group_membership_ids": [(0, 0, {"individual": self.registrant_1.id})]}
            )
            self.group_2.write(
                {"group_membership_ids": [(0, 0, {"individual": self.registrant_2.id})]}
            )
            if len(self.program_2.deduplication_managers) > 0:
                _logger.info(
                    "Program Testing: Deduplication Manager For Program %s ASSIGNED"
                    % self.program_2.name
                )
                _logger.info(
                    "Program Testing: Program: %s, Checking Deduplication"
                    % self.program_2.name
                )
                self.program_2.deduplicate_beneficiaries()
                _logger.info(
                    "Program Testing: Program: %s, Deduplications Count: %s"
                    % (self.program_2.name, self.program_2.duplicate_membership_count)
                )
            else:
                _logger.info(
                    "Program Testing: Adding Deduplication Manager For Program %s FAILED"
                    % self.program_2.name
                )

        else:
            _logger.info(
                "Program Testing: Adding Deduplication Manager For Program %s FAILED"
                % self.program_2.name
            )
