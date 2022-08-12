# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models

from ..programs import G2PProgram

_logger = logging.getLogger(__name__)


class ProgramManager(models.Model):
    _name = "g2p.program.manager"
    _description = "Program Manager"
    _inherit = "g2p.manager.mixin"

    program_id = fields.Many2one("g2p.program", "Program")

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.manager.default", "Default")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class BaseProgramManager(models.AbstractModel):
    _name = "g2p.base.program.manager"
    _description = "Base Program Manager"

    name = fields.Char("Manager Name", required=True)
    program_id = fields.Many2one("g2p.program", string="Program", required=True)

    def last_cycle(self):
        """
        Returns the last cycle of the program
        Returns:
            cycle: the last cycle of the program
        """
        # TODO: implement this
        # sort the program's cycle by sequence and return the last one
        raise NotImplementedError()

    def new_cycle(self):
        """
        Create the next cycle of the program
        Returns:
            cycle: the newly created cycle
        """
        raise NotImplementedError()


class DefaultProgramManager(models.Model):
    _name = "g2p.program.manager.default"
    _inherit = ["g2p.base.program.manager", "g2p.manager.source.mixin"]
    _description = "Default Program Manager"

    number_of_cycles = fields.Integer(string="Number of cycles", default=1)
    copy_last_cycle_on_new_cycle = fields.Boolean(
        string="Copy previous cycle", default=True
    )

    #  TODO: review 'calendar.recurrence' module, it seem the way to go for managing the recurrence
    # recurrence_id = fields.Many2one('calendar.recurrence', related='event_id.recurrence_id')

    def last_cycle(self):
        """
        Returns the last cycle of the program
        Returns:
            cycle: the last cycle of the program
        """
        cycles = self.env["g2p.cycle"].search(
            [("program_id", "=", self.program_id.id)], order="sequence desc", limit=1
        )
        return cycles and cycles[0] or None

    def new_cycle(self):
        """
        Create the next cycle of the program
        Returns:
            cycle: the newly created cycle
        """
        for rec in self:
            cycles = self.env["g2p.cycle"].search(
                [("program_id", "=", rec.program_id.id)]
            )
            new_cycle = None
            _logger.info("cycles: %s", cycles)
            cm = rec.program_id.get_manager(G2PProgram.MANAGER_CYCLE)
            if len(cycles) == 0:
                _logger.info("cycle manager: %s", cm)
                new_cycle = cm.new_cycle("Cycle 1", datetime.now(), 1)
            else:
                last_cycle = rec.last_cycle()
                new_sequence = last_cycle.sequence + 1
                new_cycle = cm.new_cycle(
                    f"Cycle {new_sequence}",
                    last_cycle.start_date + timedelta(days=cm.cycle_duration),
                    new_sequence,
                )

            # Copy the enrolled beneficiaries
            if new_cycle is not None:
                program_beneficiaries = rec.program_id.get_beneficiaries(
                    "enrolled"
                ).mapped("partner_id.id")
                cm.add_beneficiaries(new_cycle, program_beneficiaries, "enrolled")
            return new_cycle
