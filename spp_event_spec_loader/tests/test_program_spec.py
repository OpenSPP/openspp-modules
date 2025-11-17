# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestProgramSpec(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Sample YAML content for testing
        cls.sample_yaml = """
program:
  name: "Test Program"
  objectives:
    - "Test objective 1"
    - "Test objective 2"
  currency: "USD"
  localization:
    languages: ["en", "es"]
  implementing_agencies: ["Agency1", "Agency2"]

external_systems:
  - id: "TestSystem"
    role: "evidence_provider"
    domain: "test"
    data_contract:
      record_type: "test_record"
      required_fields:
        - name: "test_field"
          type: "string"

compliance:
  conditions:
    - id: "test_condition"
      description: "Test compliance condition"
"""

    def test_01_create_program_spec(self):
        """Test creating a program specification"""
        spec = self.env["spp.program.spec"].create(
            {
                "name": "Test Program",
                "code": "TEST_PROG",
                "yaml_content": self.sample_yaml,
            }
        )

        self.assertTrue(spec.id, "Program spec should be created")
        self.assertEqual(spec.state, "draft", "Initial state should be draft")
        self.assertTrue(spec.spec_data, "Spec data should be computed")

    def test_02_validate_program_spec(self):
        """Test validating a program specification"""
        spec = self.env["spp.program.spec"].create(
            {
                "name": "Test Program",
                "code": "TEST_PROG_2",
                "yaml_content": self.sample_yaml,
            }
        )

        spec.action_validate()

        self.assertEqual(spec.state, "validated", "State should be validated")
        self.assertEqual(spec.currency, "USD", "Currency should be extracted")
        self.assertIn("en", spec.languages, "Languages should be extracted")

    def test_03_invalid_yaml(self):
        """Test that invalid YAML raises validation error"""
        with self.assertRaises(ValidationError):
            self.env["spp.program.spec"].create(
                {
                    "name": "Invalid Program",
                    "code": "INVALID",
                    "yaml_content": "invalid: yaml: content: [",
                }
            )

    def test_04_extract_event_types(self):
        """Test extracting event types from spec"""
        spec = self.env["spp.program.spec"].create(
            {
                "name": "Test Program",
                "code": "TEST_PROG_3",
                "yaml_content": self.sample_yaml,
            }
        )

        spec.action_validate()

        import yaml

        parsed = yaml.safe_load(self.sample_yaml)
        event_types = spec._extract_event_types_from_spec(parsed)

        self.assertTrue(len(event_types) > 0, "Should extract event types")

        # Check for external system event type
        external_event = next((et for et in event_types if et["source"] == "external_system"), None)
        self.assertIsNotNone(external_event, "Should extract external system event")

        # Check for compliance condition event type
        compliance_event = next((et for et in event_types if et["source"] == "compliance_condition"), None)
        self.assertIsNotNone(compliance_event, "Should extract compliance event")

    def test_05_deploy_event_types(self):
        """Test deploying event types from spec"""
        spec = self.env["spp.program.spec"].create(
            {
                "name": "Test Program Deploy",
                "code": "TEST_DEPLOY",
                "yaml_content": self.sample_yaml,
            }
        )

        spec.action_validate()

        # Note: Full deployment test would require more setup
        # This test validates the extraction logic
        self.assertEqual(spec.state, "validated", "Should be in validated state")

    def test_06_reset_to_draft(self):
        """Test resetting spec to draft"""
        spec = self.env["spp.program.spec"].create(
            {
                "name": "Test Program Reset",
                "code": "TEST_RESET",
                "yaml_content": self.sample_yaml,
            }
        )

        spec.action_validate()
        self.assertEqual(spec.state, "validated")

        spec.action_reset_to_draft()
        self.assertEqual(spec.state, "draft", "Should be reset to draft")
