from odoo.osv.expression import AND, OR


def insert_operator(domain):
    if not domain:
        return domain
    operator_used = AND
    if domain[0] == "|":
        operator_used = OR
    new_domain = []
    domain = list(filter(lambda a: a not in ["&", "|", "!"], domain))
    for dom in domain:
        new_domain = operator_used([new_domain, [dom]])
    return new_domain
