from odoo import api, SUPERUSER_ID

from . import models


# def post_init_hook(env):
#     contact_model = env.ref("base.model_res_partner")
#     registrant_id_field = env.ref("spp_registrant_import.field_res_partner__spp_id")
#     contact_import_match = env["spp.import.match"].search([("model_id", "=", contact_model.id)])
#     if not contact_import_match:
#         env["spp.import.match"].create(
#             {
#                 "model_id": contact_model.id,
#                 "field_ids": [
#                     (
#                         0,
#                         0,
#                         {"field_id": registrant_id_field.id},
#                     ),
#                 ],
#             }
#         )
#     else:
#         contact_import_match.write(
#             {
#                 "field_ids": [
#                     (
#                         0,
#                         0,
#                         {"field_id": registrant_id_field.id},
#                     ),
#                 ],
#             }
#         )
