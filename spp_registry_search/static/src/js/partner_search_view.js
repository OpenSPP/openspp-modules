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
        this.notification = useService("notification");

        // Get context from action props
        const context = this.props.action?.context || {};
        const defaultPartnerType = context.default_partner_type || "individual";
        this.hidePartnerType = context.hide_partner_type || false;
        this.formViewRef = context.form_view_ref || null;

        this.state = useState({
            searchFields: [],
            selectedField: "",
            selectedFieldInfo: null,
            searchValue: "",
            fieldOptions: [],
            partnerType: defaultPartnerType,
            searching: false,
            results: [],
            showResults: false,
            selectedIds: new Set(),
            searchFilters: [],
            selectedFilterIds: new Set(),
        });

        onWillStart(async () => {
            await this.loadSearchFields(this.state.partnerType);
            await this.loadSearchFilters(this.state.partnerType);
            // Try to restore previous search state
            await this.restoreSearchState();
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
            selectedFilterIds: Array.from(this.state.selectedFilterIds),
        };
        sessionStorage.setItem(this.getSearchStateKey(), JSON.stringify(searchState));
    }

    async restoreSearchState() {
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
                    this.state.selectedFilterIds = new Set(state.selectedFilterIds || []);

                    // Restore field info and options for relational fields
                    if (this.state.selectedField) {
                        const fieldInfo = this.state.searchFields.find(
                            (f) => f.field_name === this.state.selectedField
                        );
                        this.state.selectedFieldInfo = fieldInfo;

                        if (fieldInfo) {
                            if (fieldInfo.field_type === "selection" && fieldInfo.selection) {
                                this.state.fieldOptions = fieldInfo.selection;
                            } else if (fieldInfo.field_type === "many2one" && fieldInfo.relation) {
                                try {
                                    const options = await this.orm.call("res.partner", "get_field_options", [
                                        fieldInfo.relation,
                                    ]);
                                    this.state.fieldOptions = options;
                                } catch (error) {
                                    console.error("Error loading field options during restore:", error);
                                }
                            }
                        }
                    }
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

    async loadSearchFilters(partnerType = null) {
        try {
            const filters = await this.orm.call("res.partner", "get_search_filters", [partnerType]);
            this.state.searchFilters = filters;
            // Don't auto-select any filters by default
            this.state.selectedFilterIds.clear();
        } catch (error) {
            console.error("Error loading search filters:", error);
        }
    }

    async onFieldChange(event) {
        this.state.selectedField = event.target.value;
        this.state.searchValue = "";
        this.state.fieldOptions = [];

        // Find the selected field info
        const fieldInfo = this.state.searchFields.find((f) => f.field_name === this.state.selectedField);
        this.state.selectedFieldInfo = fieldInfo;

        // Load options for relational fields
        if (fieldInfo) {
            if (fieldInfo.field_type === "selection" && fieldInfo.selection) {
                // Selection field - options are already loaded
                this.state.fieldOptions = fieldInfo.selection;
            } else if (fieldInfo.field_type === "many2one" && fieldInfo.relation) {
                // Many2one field - load options from related model
                try {
                    const options = await this.orm.call("res.partner", "get_field_options", [
                        fieldInfo.relation,
                    ]);
                    this.state.fieldOptions = options;
                } catch (error) {
                    console.error("Error loading field options:", error);
                }
            }
        }
    }

    onSearchValueChange(event) {
        this.state.searchValue = event.target.value;
    }

    get isArchivedFilterSelected() {
        // Check if any selected filter is for archived records
        const selectedFilters = this.state.searchFilters.filter((f) =>
            this.state.selectedFilterIds.has(f.id)
        );

        return selectedFilters.some((filter) => {
            try {
                const domain = JSON.parse(filter.domain || "[]");
                // Check if domain contains active = False in any format
                return domain.some((condition) => {
                    if (Array.isArray(condition) && condition.length === 3) {
                        return condition[0] === "active" && condition[1] === "=" && condition[2] === false;
                    }
                    return false;
                });
            } catch (error) {
                console.error("Error parsing filter domain for archive check:", error);
                return false;
            }
        });
    }

    get combinedFilterDomain() {
        // Combine all selected filter domains
        const selectedFilters = this.state.searchFilters.filter((f) =>
            this.state.selectedFilterIds.has(f.id)
        );

        if (selectedFilters.length === 0) {
            return "[]";
        }

        // Parse all filter domains
        const parsedDomains = [];
        for (const filter of selectedFilters) {
            try {
                const domain = JSON.parse(filter.domain || "[]");
                if (domain && domain.length > 0) {
                    parsedDomains.push(domain);
                }
            } catch (error) {
                console.error("Error parsing filter domain:", error);
            }
        }

        if (parsedDomains.length === 0) {
            return "[]";
        }

        // Single filter - just return it
        if (parsedDomains.length === 1) {
            return JSON.stringify(parsedDomains[0]);
        }

        // Multiple filters - combine with OR logic
        // Odoo domain syntax: ['|', cond1, cond2] for OR
        // For n conditions, we need (n-1) '|' operators at the beginning
        const combinedDomain = [];

        // Add (n-1) OR operators at the beginning
        for (let i = 0; i < parsedDomains.length - 1; i++) {
            combinedDomain.push("|");
        }

        // Add all conditions (flattened)
        for (const domain of parsedDomains) {
            for (const condition of domain) {
                combinedDomain.push(condition);
            }
        }

        return JSON.stringify(combinedDomain);
    }

    onFilterChange(event) {
        // Handle multiple select
        const selectedOptions = Array.from(event.target.selectedOptions);
        this.state.selectedFilterIds.clear();

        selectedOptions.forEach((option) => {
            this.state.selectedFilterIds.add(parseInt(option.value));
        });
    }

    removeFilter(filterId) {
        // Remove a specific filter from selection
        this.state.selectedFilterIds.delete(filterId);
    }

    async onPartnerTypeChange(event) {
        this.state.partnerType = event.target.value;
        // Reload fields and filters based on selected partner type
        await this.loadSearchFields(this.state.partnerType);
        await this.loadSearchFilters(this.state.partnerType);
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

            // Always use backend method for consistency
            results = await this.orm.call("res.partner", "search_by_field", [
                this.state.selectedField,
                this.state.searchValue || "", // Pass empty string for "search all"
                isGroup,
                this.combinedFilterDomain,
            ]);

            if (results && results.length > 0) {
                // Load partner details with proper context for archived records
                const searchReadDomain = [["id", "in", results]];
                const searchReadFields = [
                    "name",
                    "address",
                    "phone",
                    "tags_ids",
                    "birthdate",
                    "registration_date",
                    "is_group",
                    "active",
                ];

                if (this.isArchivedFilterSelected) {
                    // Use webSearchRead with context for archived records
                    this.state.results = await this.orm.call("res.partner", "search_read", [], {
                        domain: searchReadDomain,
                        fields: searchReadFields,
                        context: {active_test: false},
                    });
                } else {
                    this.state.results = await this.orm.searchRead(
                        "res.partner",
                        searchReadDomain,
                        searchReadFields
                    );
                }
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
        this.state.selectedFilterIds.clear();
        // Clear saved state for current partner type
        sessionStorage.removeItem(this.getSearchStateKey());
    }

    async onArchiveSelected() {
        // Archive selected records
        if (this.state.selectedIds.size === 0) {
            return;
        }

        const ids = Array.from(this.state.selectedIds);

        try {
            // Call Odoo's action_archive method
            await this.orm.call("res.partner", "action_archive", [ids]);

            // Refresh the search
            await this.onSearch();

            // Show success notification
            this.notification.add(`${ids.length} record(s) archived successfully`, {
                type: "success",
            });
        } catch (error) {
            console.error("Error archiving records:", error);
            this.notification.add("Failed to archive records", {
                type: "danger",
            });
        }
    }

    async onUnarchiveSelected() {
        // Unarchive selected records
        if (this.state.selectedIds.size === 0) {
            return;
        }

        const ids = Array.from(this.state.selectedIds);

        try {
            // Call Odoo's action_unarchive method
            await this.orm.call("res.partner", "action_unarchive", [ids]);

            // Refresh the search
            await this.onSearch();

            // Show success notification
            this.notification.add(`${ids.length} record(s) unarchived successfully`, {
                type: "success",
            });
        } catch (error) {
            console.error("Error unarchiving records:", error);
            this.notification.add("Failed to unarchive records", {
                type: "danger",
            });
        }
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
