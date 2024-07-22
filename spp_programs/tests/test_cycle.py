from freezegun import freeze_time

from odoo.exceptions import ValidationError

from .common import Common


@freeze_time("2024-07-19")
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
