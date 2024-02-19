/** @odoo-module **/

import {DomainField, domainField} from "@web/views/fields/domain/domain_field";
import {registry} from "@web/core/registry";

export class DomainFieldExtend extends DomainField {
    _getAllowedModels() {
        return ["g2p.program.create.wizard", "g2p.eligibility.manager"];
    }

    // Overwrite getEvaluatedDomain
    getEvaluatedDomain(props = this.props) {
        var domain = super.getEvaluatedDomain(props);
        var added_domain = [];
        if (this._getAllowedModels().includes(props.record.evalContext.active_model)) {
            // Modification is only used for specific models
            if (props.record.evalContext.target_type === "group") {
                added_domain = [
                    ["is_group", "=", true],
                    ["is_registrant", "=", true],
                ];
            } else {
                added_domain = [
                    ["is_group", "=", false],
                    ["is_registrant", "=", true],
                ];
            }
            if (added_domain) {
                domain.push.apply(domain, added_domain);
            }
        }
        return domain;
    }
}

export var domainFieldExtend = {...domainField};

domainFieldExtend.component = DomainFieldExtend;

registry.category("fields").add("domain", domainFieldExtend, {force: true});
