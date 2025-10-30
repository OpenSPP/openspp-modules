/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component, onWillStart, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class PartnerSearchAction extends Component {
    static template = "spp_registry_search.PartnerSearchAction";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        // Get context from action props
        const context = this.props.action?.context || {};
        const defaultPartnerType = context.default_partner_type || "individual";
        this.hidePartnerType = context.hide_partner_type || false;
        this.formViewRef = context.form_view_ref || null;

        this.state = useState({
            searchFields: [],
            selectedField: "",
            searchValue: "",
            partnerType: defaultPartnerType,
            searching: false,
            results: [],
            showResults: false,
            selectedIds: new Set(),
        });

        onWillStart(async () => {
            await this.loadSearchFields(this.state.partnerType);
            // Try to restore previous search state
            this.restoreSearchState();
        });
    }

    getSearchStateKey() {
        // Create unique key per partner type
        return `partner_search_state_${this.state.partnerType}`;
    }

    saveSearchState() {
        const searchState = {
            selectedField: this.state.selectedField,
            searchValue: this.state.searchValue,
            partnerType: this.state.partnerType,
            results: this.state.results,
            showResults: this.state.showResults,
            selectedIds: Array.from(this.state.selectedIds),
        };
        sessionStorage.setItem(this.getSearchStateKey(), JSON.stringify(searchState));
    }

    restoreSearchState() {
        const savedState = sessionStorage.getItem(this.getSearchStateKey());
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                // Only restore if the partner type matches
                if (state.partnerType === this.state.partnerType) {
                    this.state.selectedField = state.selectedField || this.state.selectedField;
                    this.state.searchValue = state.searchValue || "";
                    this.state.results = state.results || [];
                    this.state.showResults = state.showResults || false;
                    this.state.selectedIds = new Set(state.selectedIds || []);
                }
            } catch (error) {
                console.error("Error restoring search state:", error);
            }
        }
    }

    async loadSearchFields(partnerType = null) {
        try {
            const fields = await this.orm.call("res.partner", "get_searchable_fields", [partnerType]);
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
        // Only require selected field, allow empty search value
        if (!this.state.selectedField) {
            return;
        }

        this.state.searching = true;
        this.state.showResults = false;
        try {
            // Determine is_group value based on partner type
            const isGroup = this.state.partnerType === "group";

            let results = [];

            if (!this.state.searchValue) {
                // Empty search value - get all records of this type
                const domain = [
                    ["is_group", "=", isGroup],
                    ["is_registrant", "=", true],
                ];

                results = await this.orm.search("res.partner", domain);
            } else {
                // Normal field search with value
                results = await this.orm.call("res.partner", "search_by_field", [
                    this.state.selectedField,
                    this.state.searchValue,
                    isGroup,
                ]);
            }

            if (results && results.length > 0) {
                // Load partner details
                this.state.results = await this.orm.searchRead(
                    "res.partner",
                    [["id", "in", results]],
                    ["name", "email", "phone", "mobile", "city", "country_id", "is_group"]
                );
                this.state.showResults = true;
                // Clear previous selections
                this.state.selectedIds.clear();

                // Save search state to session storage
                this.saveSearchState();
            } else {
                this.state.results = [];
                this.state.showResults = true;
                this.state.selectedIds.clear();
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

    async openPartner(partnerId, isGroup) {
        // Save current search state before navigating
        this.saveSearchState();

        // Determine the correct form view based on partner type
        let viewId = false;

        if (this.formViewRef) {
            // Use the view reference from context
            try {
                const viewRef = await this.orm.call("ir.model.data", "xmlid_to_res_id", [this.formViewRef]);
                viewId = viewRef || false;
            } catch (error) {
                console.error("Error resolving view reference:", error);
            }
        } else {
            // Auto-detect based on partner type
            const viewRefString = isGroup
                ? "g2p_registry_group.view_groups_form"
                : "g2p_registry_individual.view_individuals_form";

            try {
                viewId = await this.orm.call("ir.model.data", "xmlid_to_res_id", [viewRefString]);
            } catch (error) {
                console.error("Error resolving view reference:", error);
            }
        }

        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            res_id: partnerId,
            views: [[viewId, "form"]],
            target: "current",
            context: {
                form_view_ref: this.formViewRef,
            },
        });
    }

    onClearSearch() {
        this.state.searchValue = "";
        this.state.results = [];
        this.state.showResults = false;
        this.state.selectedIds.clear();
        // Clear saved state for current partner type
        sessionStorage.removeItem(this.getSearchStateKey());
    }

    onRowClick(event, partnerId, isGroup) {
        // Open the partner record
        this.openPartner(partnerId, isGroup);
    }

    onSelectRecord(recordId) {
        if (this.state.selectedIds.has(recordId)) {
            this.state.selectedIds.delete(recordId);
        } else {
            this.state.selectedIds.add(recordId);
        }
    }

    onSelectAll() {
        this.state.selectedIds.clear();
        this.state.results.forEach((record) => {
            this.state.selectedIds.add(record.id);
        });
    }

    onDeselectAll() {
        this.state.selectedIds.clear();
    }

    isSelected(recordId) {
        return this.state.selectedIds.has(recordId);
    }

    get hasSelections() {
        return this.state.selectedIds.size > 0;
    }

    get allSelected() {
        return this.state.results.length > 0 && this.state.selectedIds.size === this.state.results.length;
    }

    async onCreate() {
        // Determine is_group value based on partner type
        const isGroup = this.state.partnerType === "group";

        // Determine the correct form view
        let viewId = false;

        if (this.formViewRef) {
            try {
                viewId = await this.orm.call("ir.model.data", "xmlid_to_res_id", [this.formViewRef]);
            } catch (error) {
                console.error("Error resolving view reference:", error);
            }
        } else {
            const viewRefString = isGroup
                ? "g2p_registry_group.view_groups_form"
                : "g2p_registry_individual.view_individuals_form";

            try {
                viewId = await this.orm.call("ir.model.data", "xmlid_to_res_id", [viewRefString]);
            } catch (error) {
                console.error("Error resolving view reference:", error);
            }
        }

        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            views: [[viewId, "form"]],
            target: "current",
            context: {
                default_is_group: isGroup,
                default_is_registrant: true,
                form_view_ref: this.formViewRef,
            },
        });
    }

    async onImport() {
        // Determine is_group value based on partner type
        const isGroup = this.state.partnerType === "group";

        // Call Odoo's built-in import action
        await this.action.doAction({
            type: "ir.actions.client",
            tag: "import",
            params: {
                model: "res.partner",
                context: {
                    default_is_group: isGroup,
                    default_is_registrant: true,
                },
            },
        });
    }

    async onExport() {
        // Check if there are selected records
        if (this.state.selectedIds.size === 0) {
            return;
        }

        // Get the IDs of selected records
        const ids = Array.from(this.state.selectedIds);

        // Save search state before export
        this.saveSearchState();

        // Determine is_group value and correct tree view
        const isGroup = this.state.partnerType === "group";
        let treeViewId = false;

        const treeViewRefString = isGroup
            ? "g2p_registry_group.view_groups_list_tree"
            : "g2p_registry_individual.view_individuals_list_tree";

        try {
            treeViewId = await this.orm.call("ir.model.data", "xmlid_to_res_id", [treeViewRefString]);
        } catch (error) {
            console.error("Error resolving tree view reference:", error);
        }

        // Open list view with filtered records
        // User can then use Actions > Export from the list view
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: isGroup ? "Export Groups" : "Export Individuals",
            res_model: "res.partner",
            views: [[treeViewId, "list"]],
            view_mode: "list",
            target: "current",
            domain: [["id", "in", ids]],
            context: {
                default_is_group: isGroup,
                default_is_registrant: true,
            },
        });
    }
}

registry.category("actions").add("partner_search_action", PartnerSearchAction);
