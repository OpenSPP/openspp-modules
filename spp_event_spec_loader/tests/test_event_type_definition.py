# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestEventTypeDefinition(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create a test program spec
        cls.program_spec = cls.env["spp.program.spec"].create({
            "name": "Test Program",
            "code": "TEST_PROG",
            "yaml_content": "program:\n  name: Test",
        })

    def test_01_create_event_type_definition(self):
        """Test creating an event type definition"""
        event_type = self.env["spp.event.type.definition"].create({
            "name": "Test Event",
            "technical_name": "spp.event.test",
            "program_spec_id": self.program_spec.id,
            "source": "custom",
        })
        
        self.assertTrue(event_type.id, "Event type should be created")
        self.assertEqual(event_type.state, "draft", "Initial state should be draft")

    def test_02_auto_generate_technical_name(self):
        """Test auto-generation of technical name"""
        event_type = self.env["spp.event.type.definition"].create({
            "name": "My Custom Event",
            "program_spec_id": self.program_spec.id,
            "source": "custom",
        })
        
        # Trigger onchange
        event_type._onchange_name()
        
        self.assertTrue(
            "my_custom_event" in event_type.technical_name,
            "Technical name should be auto-generated"
        )

    def test_03_field_definitions_json(self):
        """Test storing field definitions as JSON"""
        field_defs = [
            {"name": "test_field", "label": "Test Field", "field_type": "char"},
            {"name": "test_number", "label": "Test Number", "field_type": "float"},
        ]
        
        event_type = self.env["spp.event.type.definition"].create({
            "name": "Test Event With Fields",
            "technical_name": "spp.event.test.fields",
            "program_spec_id": self.program_spec.id,
            "source": "custom",
            "field_definitions": json.dumps(field_defs),
        })
        
        self.assertTrue(event_type.field_definitions, "Field definitions should be stored")
        
        # Validate JSON
        parsed = json.loads(event_type.field_definitions)
        self.assertEqual(len(parsed), 2, "Should have 2 field definitions")

    def test_04_generate_tree_view_xml(self):
        """Test generating tree view XML"""
        field_defs = [
            {"name": "summary", "label": "Summary", "field_type": "char"},
        ]
        
        event_type = self.env["spp.event.type.definition"].create({
            "name": "Test Event View",
            "technical_name": "spp.event.test.view",
            "program_spec_id": self.program_spec.id,
            "source": "custom",
            "field_definitions": json.dumps(field_defs),
        })
        
        tree_xml = event_type._generate_tree_view_xml()
        
        self.assertIn("<tree>", tree_xml, "Should contain tree tag")
        self.assertIn("x_name", tree_xml, "Should contain name field")

    def test_05_generate_form_view_xml(self):
        """Test generating form view XML"""
        field_defs = [
            {"name": "summary", "label": "Summary", "field_type": "char"},
            {"name": "description", "label": "Description", "field_type": "text"},
        ]
        
        event_type = self.env["spp.event.type.definition"].create({
            "name": "Test Event Form",
            "technical_name": "spp.event.test.form",
            "program_spec_id": self.program_spec.id,
            "source": "custom",
            "field_definitions": json.dumps(field_defs),
        })
        
        form_xml = event_type._generate_form_view_xml()
        
        self.assertIn("<form", form_xml, "Should contain form tag")
        self.assertIn("x_summary", form_xml, "Should contain custom fields")
        self.assertIn("x_description", form_xml, "Should contain description field")

    def test_06_deployment_flags(self):
        """Test deployment status flags"""
        event_type = self.env["spp.event.type.definition"].create({
            "name": "Test Deployment",
            "technical_name": "spp.event.test.deploy",
            "program_spec_id": self.program_spec.id,
            "source": "custom",
        })
        
        self.assertFalse(event_type.model_deployed, "Model should not be deployed initially")
        self.assertFalse(event_type.view_deployed, "Views should not be deployed initially")
        self.assertFalse(event_type.wizard_deployed, "Wizard should not be deployed initially")

