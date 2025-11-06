# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class Base(models.AbstractModel):
    """Extend base model to automatically populate res_id in queue jobs."""

    _inherit = "base"

    @api.model
    def _job_store_values(self, job):
        """
        Override to automatically populate res_id and res_model in queue jobs.

        This method is called when a job is being stored in the database.
        It extracts the record ID from the recordset that created the job
        and stores it in res_id field for later monitoring.

        :param job: current queue_job.job.Job instance.
        :return: dictionary for setting job values.
        """
        vals = super()._job_store_values(job)

        # Get the recordset that is creating the job
        recordset = job.recordset

        # If the recordset has a single record, store its ID
        if recordset and len(recordset) == 1:
            vals["res_id"] = recordset.id
            vals["res_model"] = recordset._name
        # If the recordset has multiple records, store the first ID
        elif recordset and len(recordset) > 1:
            vals["res_id"] = recordset[0].id
            vals["res_model"] = recordset._name

        return vals
