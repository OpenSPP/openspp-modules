import logging

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, ValidationError

_logger = logging.getLogger(__name__)


class G2pProgramCreateWizard(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    compliance_criteria = fields.Boolean()
    compliance_kind = fields.Selection(
        selection=[
            ("g2p.program_membership.manager.default", "Default"),
            ("g2p.program_membership.manager.sql", "SQL-based"),
            ("g2p.program_membership.manager.tags", "Tag-based"),
        ],
        default="g2p.program_membership.manager.default",
    )
    compliance_domain = fields.Text(default="[]")
    compliance_tag_id = fields.Many2one(comodel_name="g2p.registrant.tags", string="Compliance Tag")
    compliance_sql = fields.Text(string="Compliance SQL Query")
    compliance_sql_query_valid = fields.Selection(
        [
            ("need_checking", "Need Checking"),
            ("valid", "Valid"),
            ("invalid", "Invalid"),
        ],
        string="Compliance SQL Query Status",
        default="need_checking",
    )

    @api.onchange("compliance_sql")
    def _onchange_compliance_sql(self):
        self.compliance_sql_query_valid = "need_checking"

    def create_program(self):
        action = super().create_program()
        if self.compliance_criteria:
            program = self.env["g2p.program"].browse(action["res_id"])
            self._create_compliance_manager(program)
        return action

    def test_compliance_sql_query(self):
        self.ensure_one()
        sql = self._generate_sql_query(sql=self.compliance_sql)
        try:
            with self._cr.savepoint():
                self._cr.execute(sql)
                beneficiaries = self._cr.dictfetchall()
                if not len(beneficiaries) or not beneficiaries[0].get("id"):
                    raise MissingError(_("Query is not valid!"))
                self.compliance_sql_query_valid = "valid"
        except Exception as e:
            _logger.error(e.args)
            self.compliance_sql_query_valid = "invalid"
        return self._reopen_self()

    def _check_compliance_manager_info(self):
        self.ensure_one()
        if not self.compliance_criteria:
            return
        err_msg = _("Not enough information for creating compliance manager!")
        if not self.compliance_kind:
            raise ValidationError(err_msg)
        if self.compliance_kind == "g2p.program_membership.manager.default" and not self.compliance_domain:
            raise ValidationError(err_msg)
        elif self.compliance_kind == "g2p.program_membership.manager.sql" and (
            not self.compliance_sql or self.compliance_sql_query_valid != "valid"
        ):
            raise ValidationError(err_msg)
        elif self.compliance_kind == "g2p.program_membership.manager.tags" and not self.compliance_tag_id:
            raise ValidationError(err_msg)

    def _create_compliance_manager(self, program):
        self.ensure_one()
        program.ensure_one()
        self._check_compliance_manager_info()
        manager = self.env[self.compliance_kind].sudo().create(self._prepare_compliance_criteria_create_vals(program))
        program.write(
            {
                "compliance_managers": [
                    (
                        0,
                        0,
                        {
                            "manager_ref_id": "%s,%d" % (self.compliance_kind, manager.id),
                        },
                    ),
                ],
            }
        )

    def _prepare_compliance_criteria_create_vals(self, program):
        """
        Preparing vals for creating compliance criteria manager for new program.

        :param program: instance of g2p.program()
        :return (dictionary): create vals for compliance criteria manager
        :raise: NotImplementedError for compliance_kind not yet existed

        How to inherit this function:
        ```python
            def _prepare_compliance_criteria_create_vals(self, program):
                if self.compliance_kind = "new.manager.type":
                    return {
                        "key": "value",
                        ...
                    }
                return super()._prepare_compliance_criteria_create_vals(program)
        ```
        """
        if self.compliance_kind == "g2p.program_membership.manager.default":
            return {
                "name": "Default",
                "program_id": program.id,
                "admin_area_ids": [(6, 0, self.admin_area_ids.ids)],
                "eligibility_domain": self.compliance_domain,
            }
        elif self.compliance_kind == "g2p.program_membership.manager.sql":
            return {
                "name": "SQL Query",
                "program_id": program.id,
                "sql_query": self.compliance_sql,
                "sql_query_valid": "valid",
                "sql_query_valid_message": "",
                "sql_record_count": 0,
            }
        elif self.compliance_kind == "g2p.program_membership.manager.tags":
            return {
                "name": "Tags Manager",
                "program_id": program.id,
                "tags_id": self.compliance_tag_id.id,
                "area_id": self.area_id.id,
            }
        raise NotImplementedError()
