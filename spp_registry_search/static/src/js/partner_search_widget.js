/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PartnerSearchWidget extends Component {
    static template = "spp_registry_search.PartnerSearchWidget";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            searchFields: [],
            selectedField: "",
            searchValue: "",
            searching: false,
        });

        onWillStart(async () => {
            await this.loadSearchFields();
        });
    }

    async loadSearchFields() {
        try {
            const fields = await this.orm.call(
                "res.partner",
                "get_searchable_fields",
                []
            );
            this.state.searchFields = fields;
            if (fields.length > 0) {
                this.state.selectedField = fields[0].field_name;
            }
        } catch (error) {
            console.error("Error loading searchable fields:", error);
        }
    }

    onFieldChange(event) {
        this.state.selectedField = event.target.value;
    }

    onSearchValueChange(event) {
        this.state.searchValue = event.target.value;
    }

    async onSearch() {
        if (!this.state.selectedField || !this.state.searchValue) {
            return;
        }

        this.state.searching = true;
        try {
            const results = await this.orm.call(
                "res.partner",
                "search_by_field",
                [this.state.selectedField, this.state.searchValue]
            );

            // Open the partner list with the search results
            await this.action.doAction({
                type: "ir.actions.act_window",
                name: "Search Results",
                res_model: "res.partner",
                views: [[false, "list"], [false, "form"]],
                domain: [["id", "in", results]],
                target: "current",
            });
        } catch (error) {
            console.error("Error searching partners:", error);
        } finally {
            this.state.searching = false;
        }
    }

    onKeyPress(event) {
        if (event.key === "Enter") {
            this.onSearch();
        }
    }
}

registry.category("actions").add("partner_search_widget", PartnerSearchWidget);

