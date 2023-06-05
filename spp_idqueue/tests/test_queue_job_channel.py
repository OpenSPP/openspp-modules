from odoo.exceptions import ValidationError

from .common import Common


class TestCustomQueueJobChannel(Common):
    def test_01_parent_required(self):
        with self.assertRaisesRegex(ValidationError, "Parent channel required."):
            self.env["queue.job.channel"].create({"name": "channel_program"})

        self.env["queue.job.channel"].create({"name": "root_test"})
