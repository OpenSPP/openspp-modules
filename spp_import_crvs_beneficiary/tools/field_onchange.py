from odoo.tools import safe_eval

from .insert_operator import insert_operator


def field_onchange(obj, on_change_field_name, field_name):
    eligibility_domain = obj.eligibility_domain
    domain = []
    if eligibility_domain not in [None, "[]"]:
        # Do not remove other filters
        # Convert the string to list of tuples
        domain = safe_eval.safe_eval(eligibility_domain)

        crvs_dom = list(filter(lambda x: field_name in x, domain))
        if crvs_dom:
            domain.remove(crvs_dom[0])

    if getattr(obj, on_change_field_name):
        domain.append((field_name, "=", getattr(obj, on_change_field_name)))

    eligibility_domain = str(insert_operator(domain))
    obj.eligibility_domain = eligibility_domain
