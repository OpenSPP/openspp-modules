import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPFeedItems(models.Model):
    _name = "spp.feed.items"
    _description = "Feed Items Types"

    name = fields.Char("Feed Items Type")
