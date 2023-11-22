from odoo.tools import safe_eval

from .insert_operator import insert_operator


def field_onchange(obj, on_change_field_name, field_name, operator="="):
    eligibility_domain = obj.eligibility_domain
    domain = []
    if eligibility_domain not in [None, "[]"]:
        # Do not remove other filters
        # Convert the string to list of tuples
        domain = safe_eval.safe_eval(eligibility_domain)

        crvs_dom = list(filter(lambda x: field_name in x, domain))
        if crvs_dom:
            domain.remove(crvs_dom[0])

    fields = on_change_field_name.split(".")
    value = obj
    while fields:
        field = fields.pop(0)
        if hasattr(value, field):
            value = getattr(value, field)
        else:
            value = None

    if value:
        domain.append((field_name, operator, value))

    eligibility_domain = str(insert_operator(domain))
    obj.eligibility_domain = eligibility_domain
