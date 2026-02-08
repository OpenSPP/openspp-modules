from . import models
from . import controllers
from . import wizard

from odoo import api, SUPERUSER_ID


def post_init_hook(env_or_cr, registry=None):
    """Post init hook compatible with Odoo calling conventions.

    Accepts either (env) or (cr, registry) depending on Odoo version/context.
    """
    # Detect if first argument is an Environment or a Cursor
    if hasattr(env_or_cr, "cr") and hasattr(env_or_cr, "uid"):
        # Some environments expose uid; treat as env
        env = env_or_cr
    elif hasattr(env_or_cr, "cr") and hasattr(env_or_cr, "_cnx"):
        # Cursor (psycopg2); build env
        env = api.Environment(env_or_cr, SUPERUSER_ID, {})
    else:
        try:
            # If it's already an Environment instance
            from odoo.api import Environment

            if isinstance(env_or_cr, Environment):
                env = env_or_cr
            else:
                env = api.Environment(env_or_cr, SUPERUSER_ID, {})
        except Exception:
            env = api.Environment(env_or_cr, SUPERUSER_ID, {})
    env["openspp.indicator.value"]._ensure_base_table()
    env["openspp.indicator.value"]._ensure_partitions()
