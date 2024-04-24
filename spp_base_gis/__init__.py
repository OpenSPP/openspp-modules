# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from . import controllers
from . import expression
from . import models
from . import fields
from . import operators

from odoo import _
from odoo.exceptions import MissingError


def init_postgis(env):
    """Initialize postgis
    Add PostGIS support to the database. PostGIS is a spatial database
    extender for PostgreSQL object-relational database. It adds support for
    geographic objects allowing location queries to be run in SQL.
    """
    cr = env.cr
    cr.execute(
        """
        SELECT
            tablename
        FROM
            pg_tables
        WHERE
            tablename='spatial_ref_sys';
    """
    )
    check = cr.fetchone()
    if check:
        return {}
    try:
        cr.execute(
            """
        CREATE EXTENSION postgis;
        CREATE EXTENSION postgis_topology;
    """
        )
    except Exception as exc:
        raise MissingError(
            _(
                "Error, can not automatically initialize spatial postgis"
                " support. Database user may have to be superuser and"
                " postgres/postgis extensions with their devel header have"
                " to be installed. If you do not want Odoo to connect with a"
                " super user you can manually prepare your database. To do"
                " this, open a client to your database using a super user and"
                " run:\n"
                "CREATE EXTENSION postgis;\n"
                "CREATE EXTENSION postgis_topology;\n"
            )
        ) from exc
