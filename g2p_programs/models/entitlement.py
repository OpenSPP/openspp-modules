# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
from uuid import uuid4

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class G2PEntitlement(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "g2p.entitlement"
    _description = "Entitlement"
    _order = "id desc"
    _check_company_auto = True

    @api.model
    def _generate_code(self):
        return str(uuid4())[4:-8][3:]

    name = fields.Char(compute="_compute_name")
    code = fields.Char(
        default=lambda x: x._generate_code(), required=True, readonly=True, copy=False
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    cycle_id = fields.Many2one("g2p.cycle", required=True)
    program_id = fields.Many2one("g2p.program", related="cycle_id.program_id")

    valid_from = fields.Date(required=False)
    valid_until = fields.Date(
        default=lambda self: fields.Date.add(fields.Date.today(), years=1)
    )

    is_cash_entitlement = fields.Boolean("Cash Entitlement", default=False)
    currency_id = fields.Many2one(
        "res.currency", readonly=True, related="journal_id.currency_id"
    )
    initial_amount = fields.Monetary(required=True, currency_field="currency_id")
    balance = fields.Monetary(compute="_compute_balance")  # in company currency
    # TODO: implement transactions against this entitlement

    journal_id = fields.Many2one(
        "account.journal",
        "Disbursement Journal",
        store=True,
        compute="_compute_journal_id",
    )
    disbursement_id = fields.Many2one("account.payment", "Disbursement Journal Entry")

    date_approved = fields.Date("Date Approved")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_validation", "Pending Validation"),
            ("approved", "Approved"),
            ("trans2FSP", "Transferred to FSP"),
            ("rdpd2ben", "Redeemed/Paid to Beneficiary"),
            ("rejected1", "Rejected: Beneficiary didn't want the entitlement"),
            ("rejected2", "Rejected: Beneficiary account does not exist"),
            ("rejected3", "Rejected: Other reason"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
        "Status",
        default="draft",
        copy=False,
    )

    _sql_constraints = [
        (
            "unique_entitlement_code",
            "UNIQUE(code)",
            "The entitlement code must be unique.",
        ),
    ]

    def fields_view_get(
        self, view_id=None, view_type="list", toolbar=False, submenu=False
    ):
        res = super(G2PEntitlement, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

        group_g2p_admin = self.env.user.has_group("g2p_registrant.group_g2p_admin")
        if not group_g2p_admin:
            if view_type != "search":
                group_g2p_registrar = self.env.user.has_group(
                    "g2p_registrant.group_g2p_registrar"
                )
                g2p_program_validator = self.env.user.has_group(
                    "g2p_programs.g2p_program_validator"
                )

                if group_g2p_registrar or g2p_program_validator:
                    raise ValidationError(
                        _("You have no access in the Entitlement List View")
                    )

        return res

    def _compute_name(self):
        for record in self:
            name = _("Entitlement")
            initial_amount = "{:,.2f}".format(record.initial_amount)
            if record.is_cash_entitlement:
                name += (
                    " Cash ["
                    + str(record.currency_id.symbol)
                    + " "
                    + initial_amount
                    + "]"
                )
            else:
                name += " (" + str(record.code) + ")"
            record.name = name

    @api.depends("initial_amount")
    def _compute_balance(self):
        for record in self:
            record.balance = record.initial_amount

    @api.depends("cycle_id.program_id.journal_id")
    def _compute_journal_id(self):
        for record in self:
            record.journal_id = (
                record.cycle_id
                and record.cycle_id.program_id
                and record.cycle_id.program_id.journal_id
                and record.cycle_id.program_id.journal_id.id
                or None
            )

    @api.autovacuum
    def _gc_mark_expired_entitlement(self):
        self.env["g2p.entitlement"].search(
            ["&", ("state", "=", "approved"), ("valid_until", "<", fields.Date.today())]
        ).write({"state": "expired"})

    def can_be_used(self):
        # expired state are computed once a day, so can be not synchro
        return self.state == "approved" and self.valid_until >= fields.Date.today()

    def unlink(self):
        if self.state == "draft":
            return super(G2PEntitlement, self).unlink()
        else:
            raise ValidationError(
                _("Only draft entitlements are allowed to be deleted")
            )

    def approve_entitlement(self):
        amt = 0.0
        state_err = 0
        sw = 0
        for rec in self:
            if rec.state in ("draft", "pending_validation"):
                fund_balance = self.check_fund_balance(rec.cycle_id.program_id.id) - amt
                if fund_balance >= rec.initial_amount:
                    amt += rec.initial_amount
                    # Prepare journal entry (account.move) via account.payment
                    payment = {
                        "partner_id": rec.partner_id.id,
                        "payment_type": "outbound",
                        "amount": rec.initial_amount,
                        "currency_id": rec.journal_id.currency_id.id,
                        "journal_id": rec.journal_id.id,
                        "partner_type": "supplier",
                    }
                    new_payment = self.env["account.payment"].create(payment)
                    rec.update(
                        {
                            "disbursement_id": new_payment.id,
                            "state": "approved",
                            "date_approved": fields.Date.today(),
                        }
                    )
                else:
                    raise UserError(
                        _(
                            "The fund for the program: %s[%.2f] is insufficient for the entitlement: %s"
                        )
                        % (rec.cycle_id.program_id.name, fund_balance, rec.code)
                    )
            else:
                state_err += 1
                if sw == 0:
                    sw = 1
                    message = _(
                        "<b>Entitle State Error! Entitlements not in 'pending validation' state:</b>\n"
                    )
                message += _(
                    "Program: %s, Beneficiary: %s.\n"
                    % (rec.cycle_id.program_id.name, rec.partner_id.name)
                )

        if state_err > 0:
            kind = "danger"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Entitlement"),
                    "message": message,
                    "sticky": True,
                    "type": kind,
                },
            }

    def check_fund_balance(self, program_id):
        company_id = self.env.user.company_id and self.env.user.company_id.id or None
        retval = 0.0
        if company_id:
            params = (
                company_id,
                program_id,
            )

            # Get the current fund balance
            fund_bal = 0.0
            sql = """
                select sum(amount) as total_fund
                from g2p_program_fund
                where company_id = %s
                    AND program_id = %s
                    AND state = 'posted'
                """
            self._cr.execute(sql, params)
            program_funds = self._cr.dictfetchall()
            fund_bal = program_funds[0]["total_fund"] or 0.0

            # Get the current entitlement totals
            total_entitlements = 0.0
            sql = """
                select sum(a.initial_amount) as total_entitlement
                from g2p_entitlement a
                    left join g2p_cycle b on b.id = a.cycle_id
                where a.company_id = %s
                    AND b.program_id = %s
                    AND a.state = 'approved'
                """
            self._cr.execute(sql, params)
            entitlements = self._cr.dictfetchall()
            total_entitlements = entitlements[0]["total_entitlement"] or 0.0

            retval = fund_bal - total_entitlements
        return retval

    def open_entitlement_form(self):
        return {
            "name": "Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement",
            "res_id": self.id,
            "view_id": self.env.ref("g2p_programs.view_entitlement_form").id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def open_disb_form(self):
        for rec in self:
            if rec.disbursement_id:
                res_id = rec.disbursement_id.id
                return {
                    "name": "Disbursement",
                    "view_mode": "form",
                    "res_model": "account.payment",
                    "res_id": res_id,
                    "view_id": self.env.ref("account.view_account_payment_form").id,
                    "type": "ir.actions.act_window",
                    "target": "current",
                }
