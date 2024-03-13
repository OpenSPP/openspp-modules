from odoo import fields, models, api


class SPPDMSDirectory(models.Model):
    _name = "spp.dms.directory"
    _description = "DMS Directory"

    _rec_name = "complete_name"
    _order = "complete_name"

    complete_name = fields.Char("Directory Name", compute="_compute_complete_name", store=True, recursive=True)
    parent_path = fields.Char(index=True)
    is_root_directory = fields.Boolean(default=False)
    parent_id = fields.Many2one(
        comodel_name="spp.dms.directory",
        string="Parent Directory",
        ondelete="restrict",
        # Access to a directory doesn't necessarily mean access its parent, so
        # prefetching this field could lead to misleading access errors
        prefetch=False,
        index=True,
        store=True,
        readonly=False,
        compute="_compute_parent_id",
        copy=True,
        default=lambda self: self._default_parent_id(),
    )
    root_directory_id = fields.Many2one(
        "dms.directory", "Root Directory", compute="_compute_root_id", store=True
    )
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
                category.complete_name = "{} / {}".format(
                    category.parent_id.complete_name,
                    category.name,
                )
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
                record.root_directory_id = record
            else:
                # recursively check all parent nodes up to the root directory
                if not record.parent_id.root_directory_id:
                    record.parent_id._compute_root_id()
                record.root_directory_id = record.parent_id.root_directory_id
