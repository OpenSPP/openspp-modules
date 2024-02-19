/** @odoo-module **/

import {DomainFieldExtend, domainFieldExtend} from "@spp_programs/js/domain_field";
import {registry} from "@web/core/registry";

class DomainFieldProgramCriteria extends DomainFieldExtend {}

DomainFieldProgramCriteria.template = "spp_programs_compliance_criteria.DomainField";

var domainFieldProgramCriteria = {...domainFieldExtend};

domainFieldProgramCriteria.component = DomainFieldProgramCriteria;

registry.category("fields").add("domain_program_compliance", domainFieldProgramCriteria);
