/** @odoo-module **/

import {DomainField, domainField} from "@web/views/fields/domain/domain_field";
import {registry} from "@web/core/registry";

class DomainFieldExtend extends DomainField {}

DomainFieldExtend.template = "spp_import_dci_api.DomainField";

var domainFieldExtend = {...domainField};

domainFieldExtend.component = DomainFieldExtend;

registry.category("fields").add("domain_import_dci", domainFieldExtend);
