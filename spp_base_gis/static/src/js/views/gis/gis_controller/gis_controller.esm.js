/** @odoo-module */

import {Component, useState} from "@odoo/owl";
import {useOwnedDialogs, useService} from "@web/core/utils/hooks";

import {Layout} from "@web/search/layout";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {extractFieldsFromArchInfo} from "@web/model/relational_model/utils";
import {session} from "@web/session";
import {standardViewProps} from "@web/views/standard_view_props";
import {useModelWithSampleData} from "@web/model/model";
import {usePager} from "@web/search/pager_hook";
import {useSearchBarToggler} from "@web/search/search_bar/search_bar_toggler";

export class GisController extends Component {
    /**
     * Setup the controller by using the useModel hook.
     */
    setup() {
        this.state = useState({isSavedOrDiscarded: false});
        this.actionService = useService("action");
        this.view = useService("view");
        this.addDialog = useOwnedDialogs();
        this.editable = this.props.archInfo.editable;
        this.archInfo = this.props.archInfo;
        this.model = useState(useModelWithSampleData(this.props.Model, this.modelParams));
        this.searchBarToggler = useSearchBarToggler();

        /**
         * Allow you to display records on the map thanks to the paging located
         * at the top right of the screen.
         */
        usePager(() => {
            const list = this.model.root;
            const {count, limit, offset} = list;
            return {
                offset,
                limit,
                total: count,
                onUpdate: async (args) => {
                    await list.load({limit: args.limit, offset: args.offset});
                    this.render(true);
                },
            };
        });
    }

    get modelParams() {
        const {resModel, archInfo, limit, defaultGroupBy, state, fields, searchMenuTypes} = this.props;
        const {activeFields} = extractFieldsFromArchInfo(archInfo, fields);

        // Define default modelConfig structure and override if necessary.
        let modelConfig = {
            resModel,
            fields,
            activeFields,
            openGroupsByDefault: true,
        };

        // Overwrite default modelConfig with state's modelConfig if it exists.
        if (state && state.modelState && state.modelState.config) {
            modelConfig = {...modelConfig, ...state.modelState.config};
        }

        // Use state's modelState if it exists or null.
        let modelState = null;
        if (state && state.modelState) {
            modelState = state.modelState;
        }

        return {
            config: modelConfig,
            state: modelState,
            limit: archInfo.limit || limit,
            countLimit: archInfo.countLimit,
            defaultOrderBy: archInfo.defaultOrder,
            defaultGroupBy: searchMenuTypes.includes("groupBy") ? defaultGroupBy : false,
            groupsLimit: archInfo.groupsLimit,
            multiEdit: archInfo.multiEdit,
            activeIdsLimit: session.active_ids_limit,
        };
    }

    /**
     * Opens the form editing view for the specified model and record.
     * @param {String} resModel - The name of the resource model.
     * @param {Number} resId - The ID of the resource record.
     * @param {Number} [viewId] - The ID of the view to open. If not provided, defaults to the form view.
     */
    async openFormRecord(resModel, resId, viewId) {
        try {
            // Validate input parameters
            if (!resModel || !resId) {
                throw new Error("Model name and Record ID are required to open a record.");
            }
            // Load views for the given model, with a fallback on default form view if no viewId is provided
            const {views} = await this.view.loadViews({resModel, views: [[false, "form"]]});

            const formViewId = viewId || [[views.form.id, "form"]];
            // Ensure a form view is available
            if (!formViewId) {
                throw new Error("No form view could be found for the specified model.");
            }

            // Perform the action to open the form view
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: resModel,
                views: formViewId,
                res_id: resId,
                target: "new",
                context: {edit: false, create: false},
            });
        } catch (error) {
            // Handle any errors that occur during view loading or action execution
            console.error("Error opening record:", error);
        }
    }
}

GisController.template = "spp_base_gis.GisController";
GisController.components = {Layout, SearchBar};
GisController.props = {
    ...standardViewProps,
    Model: Function,
    Renderer: Function,
    archInfo: Object,
};
