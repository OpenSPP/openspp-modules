from odoo import fields, models


class SPPEntitlementTransactions(models.Model):
    _name = "spp.entitlement.transactions"
    _description = "Entitlement Transactions"

    card_number = fields.Char()
    card_type = fields.Char()
    receipt_number = fields.Char()
    entitlement_id = fields.Many2one("g2p.entitlement", string="Entitlement")
    service_point_id = fields.Many2one("spp.service.point", string="Service Point")
    service_point_device_id = fields.Char(string="Service Point Device ID")
    user_id = fields.Many2one("res.users", "POS User", required=True)
    timestamp_transaction_created = fields.Datetime(string="Transaction Created", required=True)
    transaction_type = fields.Char()
    transaction_uuid = fields.Char(string="Transaction UUID", required=True)

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
    )
    amount_charged_by_service_point = fields.Monetary(currency_field="currency_id", default=0.0)
    value_remaining = fields.Monetary(currency_field="currency_id", default=0.0)

    program_id = fields.Many2one(
        "g2p.program",
        string="Program",
        related="entitlement_id.cycle_id.program_id",
        store=False,
    )
    cycle_id = fields.Many2one("g2p.cycle", string="Cycle", related="entitlement_id.cycle_id", store=False)

    # Constraints
    _sql_constraints = [
        (
            "transaction_uuid_unique",
            "unique(transaction_uuid)",
            "The transaction UUID must be unique!",
        )
    ]


class SPPInKindEntitlementTransactions(models.Model):
    _name = "spp.inkind.entitlement.transactions"
    _description = "In-Kind Entitlement Transactions"

    card_number = fields.Char()
    card_type = fields.Char()
    receipt_number = fields.Char()
    entitlement_id = fields.Many2one("g2p.entitlement.inkind", string="Entitlement")
    service_point_id = fields.Many2one("spp.service.point", string="Service Point")
    service_point_device_id = fields.Char(string="Service Point Device ID")
    user_id = fields.Many2one("res.users", "POS User", required=True)
    timestamp_transaction_created = fields.Datetime(string="Transaction Created", required=True)
    transaction_type = fields.Char()
    transaction_uuid = fields.Char(string="Transaction UUID", required=True)
    product_id = fields.Many2one("product.product", string="Product")
    quantity_remaining = fields.Float(digits=(10, 2))
    quantity = fields.Float(digits=(10, 2))
    uom_id = fields.Many2one("uom.uom", "Unit of Measure")
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
    )
    amount_charged_by_service_point = fields.Monetary(currency_field="currency_id", default=0.0)
    value_remaining = fields.Monetary(currency_field="currency_id", default=0.0)

    program_id = fields.Many2one(
        "g2p.program",
        string="Program",
        related="entitlement_id.cycle_id.program_id",
        store=False,
    )
    cycle_id = fields.Many2one("g2p.cycle", string="Cycle", related="entitlement_id.cycle_id", store=False)

    # Constraints
    _sql_constraints = [
        (
            "transaction_uuid_unique",
            "unique(transaction_uuid)",
            "The transaction UUID must be unique!",
        )
    ]
