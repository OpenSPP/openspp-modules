from ast import literal_eval

from odoo import _, api, fields, models
from odoo.osv.expression import AND
from odoo.tools import human_size


class SPPDMSDirectory(models.Model):
    _name = "spp.dms.directory"
    _description = "DMS Directory"

    _rec_name = "complete_name"
    _order = "complete_name"

    name = fields.Char(required=True, index="btree")
    complete_name = fields.Char("Directory Name", compute="_compute_complete_name", store=True, recursive=True)
    parent_path = fields.Char(index=True)
    is_root_directory = fields.Boolean(default=False)
    parent_id = fields.Many2one(
        comodel_name="spp.dms.directory",
        string="Parent Directory",
        ondelete="restrict",
        prefetch=False,
        index=True,
        store=True,
        readonly=False,
        compute="_compute_parent_id",
        copy=True,
        default=lambda self: self._default_parent_id(),
    )
    root_directory_id = fields.Many2one("spp.dms.directory", "Root Directory", compute="_compute_root_id", store=True)
    child_directory_ids = fields.One2many(
        comodel_name="spp.dms.directory",
        inverse_name="parent_id",
        string="Subdirectories",
        auto_join=False,
        copy=False,
    )
    file_ids = fields.One2many(
        comodel_name="spp.dms.file",
        inverse_name="directory_id",
        string="Files",
        auto_join=False,
        copy=False,
    )
    count_elements = fields.Integer(compute="_compute_count_elements")
    count_directories = fields.Integer(compute="_compute_count_directories", string="Count Subdirectories Title")
    count_directories_title = fields.Char(compute="_compute_count_directories", string="Count Subdirectories")
    count_files = fields.Integer(compute="_compute_count_files", string="Count Files Title")
    count_files_title = fields.Char(compute="_compute_count_files", string="Count Files")
    count_total_directories = fields.Integer(compute="_compute_count_total_directories", string="Total Subdirectories")
    count_total_files = fields.Integer(compute="_compute_count_total_files", string="Total Files")
    size = fields.Float(compute="_compute_size")
    human_size = fields.Char(compute="_compute_human_size")

    def _default_parent_id(self):
        context = self.env.context
        if context.get("active_model") == self._name and context.get("active_id"):
            return context["active_id"]
        else:
            return False

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name

    @api.depends("is_root_directory")
    def _compute_parent_id(self):
        for record in self:
            if record.is_root_directory:
                record.parent_id = None
            else:
                record.parent_id = record.parent_id

    @api.depends("is_root_directory", "parent_id")
    def _compute_root_id(self):
        for record in self:
            if record.is_root_directory:
                record.root_directory_id = record.id
            else:
                if not record.parent_id.root_directory_id:
                    record.parent_id._compute_root_id()
                record.root_directory_id = record.parent_id.root_directory_id

    def _compute_size(self):
        sudo_model = self.env["spp.dms.file"].sudo()
        for record in self:
            # Avoid NewId
            if not record.id:
                record.size = 0
                continue
            recs = sudo_model.search_read(
                domain=[("directory_id", "child_of", record.id)],
                fields=["size"],
            )
            record.size = sum(rec.get("size", 0) for rec in recs)

    @api.depends("size")
    def _compute_human_size(self):
        for item in self:
            item.human_size = human_size(item.size) if item.size else False

    @api.depends("child_directory_ids")
    def _compute_count_directories(self):
        for record in self:
            directories = len(record.child_directory_ids)
            record.count_directories = directories
            record.count_directories_title = _("%s Subdirectories") % directories

    @api.depends("file_ids")
    def _compute_count_files(self):
        for record in self:
            files = len(record.file_ids)
            record.count_files = files
            record.count_files_title = _("%s Files") % files

    @api.depends("child_directory_ids", "file_ids")
    def _compute_count_elements(self):
        for record in self:
            elements = record.count_files
            elements += record.count_directories
            record.count_elements = elements

    def _compute_count_total_directories(self):
        for record in self:
            count = self.search_count([("id", "child_of", record.id)]) if record.id else 0
            record.count_total_directories = count - 1 if count > 0 else 0

    def _compute_count_total_files(self):
        model = self.env["spp.dms.file"]
        for record in self:
            # Prevent error in some NewId cases
            record.count_total_files = model.search_count([("directory_id", "child_of", record.id)]) if record.id else 0

    def action_spp_dms_directories_all_directory(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("spp_dms.action_spp_dms_directory")
        domain = AND(
            [
                literal_eval(action["domain"].strip()),
                [("parent_id", "child_of", self.id)],
            ]
        )
        action["domain"] = domain
        action["context"] = dict(
            self.env.context,
            default_parent_id=self.id,
            searchpanel_default_parent_id=self.id,
        )
        return action

    def action_spp_dms_files_all_directory(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("spp_dms.action_spp_dms_file")
        domain = AND(
            [
                literal_eval(action["domain"].strip()),
                [("directory_id", "child_of", self.id)],
            ]
        )
        action["domain"] = domain
        action["context"] = dict(
            self.env.context,
            default_directory_id=self.id,
            searchpanel_default_directory_id=self.id,
        )
        return action
