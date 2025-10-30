/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PartnerSearchAction extends Component {
    static template = "spp_registry_search.PartnerSearchAction";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            searchFields: [],
            selectedField: "",
            searchValue: "",
            partnerType: "individual", // Default to individual
            searching: false,
            results: [],
            showResults: false,
        });

        onWillStart(async () => {
            await this.loadSearchFields();
        });
    }

    async loadSearchFields(partnerType = null) {
        try {
            const fields = await this.orm.call(
                "res.partner",
                "get_searchable_fields",
                [partnerType]
            );
            this.state.searchFields = fields;
            if (fields.length > 0) {
                this.state.selectedField = fields[0].field_name;
            } else {
                this.state.selectedField = "";
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

    async onPartnerTypeChange(event) {
        this.state.partnerType = event.target.value;
        // Reload fields based on selected partner type
        await this.loadSearchFields(this.state.partnerType);
        // Clear search value when partner type changes
        this.state.searchValue = "";
        this.state.showResults = false;
    }

    async onSearch() {
        if (!this.state.selectedField || !this.state.searchValue) {
            return;
        }

        this.state.searching = true;
        this.state.showResults = false;
        try {
            // Determine is_group value based on partner type
            const isGroup = this.state.partnerType === "group";
            
            const results = await this.orm.call(
                "res.partner",
                "search_by_field",
                [this.state.selectedField, this.state.searchValue, isGroup]
            );

            if (results && results.length > 0) {
                // Load partner details
                this.state.results = await this.orm.searchRead(
                    "res.partner",
                    [["id", "in", results]],
                    ["name", "email", "phone", "mobile", "city", "country_id", "is_group"]
                );
                this.state.showResults = true;
            } else {
                this.state.results = [];
                this.state.showResults = true;
            }
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

    async openPartner(partnerId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            res_id: partnerId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    onClearSearch() {
        this.state.searchValue = "";
        this.state.partnerType = "individual";
        this.state.results = [];
        this.state.showResults = false;
    }
}

registry.category("actions").add("partner_search_action", PartnerSearchAction);

