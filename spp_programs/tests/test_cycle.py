from odoo import fields
from odoo.exceptions import ValidationError

from .common import Common


class TestCycle(Common):
    def test_check_dates_constrains(self):
        with self.assertRaisesRegex(ValidationError, 'The "End Date" cannot be earlier than the "Start Date".'):
            self.cycle.write(
                {
                    "end_date": "2024-07-18",
                }
            )

        with self.assertRaisesRegex(ValidationError, 'The "Start Date" cannot be earlier than today.'):
            self.cycle.write(
                {
                    "start_date": "2024-07-18",
                }
            )

    def test_get_previous_and_next_cycle(self):
        # The `cycle` from `Common` is created first.
        # To test previous/next, we need to control creation order.
        # Cycles are sorted by `create_date`.

        # Create a new program for this test to avoid interference from other tests
        self.program = self.env["g2p.program"].create(
            {
                "name": "Test Program for Cycle Navigation",
            }
        )

        # This will be the first cycle chronologically by create_date
        first_cycle = self.env["g2p.cycle"].create(
            {
                "name": "First Cycle",
                "program_id": self.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )

        # This is the middle cycle, created after first_cycle
        middle_cycle = self.env["g2p.cycle"].create(
            {
                "name": "Middle Cycle",
                "program_id": self.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )

        # The `self.cycle` from `setUp` is now the last one created.
        # Let's rename it for clarity in this test.
        last_cycle = self.env["g2p.cycle"].create(
            {
                "name": "Last Cycle",
                "program_id": self.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )

        self.assertIsNone(first_cycle.get_previous_cycle(), "First cycle should have no previous cycle.")
        self.assertEqual(
            first_cycle.get_next_cycle(), middle_cycle, "Next cycle for first_cycle should be middle_cycle."
        )
        self.assertEqual(
            middle_cycle.get_previous_cycle(), first_cycle, "Previous cycle for middle_cycle should be first_cycle."
        )
        self.assertEqual(middle_cycle.get_next_cycle(), last_cycle, "Next cycle for middle_cycle should be last_cycle.")
        self.assertEqual(
            last_cycle.get_previous_cycle(), middle_cycle, "Previous cycle for last_cycle should be middle_cycle."
        )
        self.assertIsNone(last_cycle.get_next_cycle(), "Last cycle should have no next cycle.")
