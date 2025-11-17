# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"
    
    # This model will be extended dynamically with fields for active events
    # Example: active_compliance_attendance, active_health_verification, etc.
    
    @api.model
    def _register_dynamic_event_field(self, field_name, event_model):
        """
        Dynamically register a Many2one field for an active event type
        
        :param field_name: Field name (e.g., 'active_compliance_attendance')
        :param event_model: Technical model name (e.g., 'spp.event.compliance.attendance')
        """
        # Check if field already exists
        if field_name in self._fields:
            _logger.info("Field %s already exists on res.partner", field_name)
            return
        
        # This would require dynamic field registration
        # For now, we log the intention
        _logger.info(
            "Dynamic field registration requested: %s -> %s",
            field_name, event_model
        )
        
        # In practice, dynamic field addition requires:
        # 1. Creating ir.model.fields record
        # 2. Reloading the model
        # 3. Or using the fields API to add fields at runtime

