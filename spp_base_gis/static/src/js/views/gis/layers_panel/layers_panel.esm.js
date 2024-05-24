/** @odoo-module */

import {Component, onWillStart, useState} from "@odoo/owl";
import {useOwnedDialogs, useService} from "@web/core/utils/hooks";

import {CheckBox} from "@web/core/checkbox/checkbox";
import {FormViewDialog} from "@web/views/view_dialogs/form_view_dialog";
import {Layout} from "@web/search/layout";
import {Notebook} from "@web/core/notebook/notebook";
import {_t} from "@web/core/l10n/translation";
import {dataLayersStore} from "../../../data_layers_store.esm";
import {rasterLayersStore} from "../../../raster_layers_store.esm";

export class LayersPanel extends Component {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.view = useService("view");
        this.rpc = useService("rpc");
        this.user = useService("user");
        // Initialize gisLayers with the expected structure
        this.state = useState({gisLayers: {actives: [], backgrounds: []}, isFolded: false});
        this.addDialog = useOwnedDialogs();
        this.rasterLayersStore = rasterLayersStore;

        onWillStart(async () => {
            try {
                await Promise.all([this.loadIsAdmin(), this.loadLayers()]);
                // Ensure gisLayers.actives is an array before iterating
                if (Array.isArray(this.state.gisLayers.actives)) {
                    this.state.gisLayers.actives.forEach((val) => {
                        const element = this.props.dataLayerModel.records.find((el) => el.resId === val.id);
                        // Check if element is found to avoid assigning undefined properties
                        if (element) {
                            const obj = {id: element.id, resId: element.resId};
                            Object.assign(val, obj);
                        }
                    });
                }
                // Set layers in the store
                rasterLayersStore.setLayers(this.state.gisLayers.backgrounds);
                dataLayersStore.setLayers(this.state.gisLayers.actives);
                this.numberOfLayers = dataLayersStore.count + rasterLayersStore.count;
            } catch (error) {
                console.error("Error during onWillStart:", error);
            }
        });
    }

    sortStart({element}) {
        element.classList.add("shadow");
    }

    async loadIsAdmin() {
        try {
            const result = await this.user.hasGroup("spp_base_gis.group_gis_admin");
            this.isGisAdmin = result;
        } catch (error) {
            console.error("Error loading admin status:", error);
        }
    }

    async loadLayers() {
        try {
            const result = await this.orm.call(this.props.model, "get_gis_layers", [this.env.config.viewId]);
            this.state.gisLayers = result;
        } catch (error) {
            console.error("Error loading layers:", error);
        }
    }

    async sort(dataRowId, {previous}) {
        const refId = previous ? previous.dataset.id : null;
        this.resequence(dataRowId, refId);
        try {
            if (this.isGisAdmin) {
                await this.resequenceAndUpdate(dataRowId, refId);
            } else {
                this.state.gisLayers.actives.forEach((element, index) => {
                    this.onDataLayerChange(element, "onSequenceChanged", index + 1);
                });
            }
        } catch (error) {
            console.error("Error sorting layers:", error);
        }
    }

    resquence(dataRowId, refId) {
        const fromIndex = this.state.gisLayers.actives.findIndex((layer) => layer.id === dataRowId);
        const record = this.state.gisLayers.actives.splice(fromIndex, 1)[0];

        let toIndex = refId ? this.state.gisLayers.actives.findIndex((layer) => layer.id === refId) : 0;
        toIndex += fromIndex < toIndex ? 1 : 0;

        this.state.gisLayers.actives.splice(toIndex, 0, record);
    }

    async resequenceAndUpdate(dataRowId, refId) {
        try {
            await this.props.dataLayerModel.resequence(dataRowId, refId, {handleField: "sequence"});
            this.props.dataLayerModel.records.forEach((element) => {
                this.onDataLayerChange(element, "onSequenceChanged", element.data.sequence);
            });
        } catch (error) {
            console.error("Error updating sequence:", error);
        }
    }

    /**
     * Called when a raster layer is changed. The raster layer is set to visible and then
     * notifies the store of the change.
     * @param {Object} layer
     * @param {Object} value
     */
    onRasterChange(layer, value) {
        // Update the properties of the raster layer if it exists and value is provided
        const rasterLayer = rasterLayersStore.getLayersById(layer.id);
        if (rasterLayer && value) {
            Object.assign(rasterLayer, value);
        }

        // Use map to create a new array with updated visibility based on the layer name
        if (!value) {
            const newRasters = rasterLayersStore.getLayers.map((item) => ({
                ...item,
                isVisible: item.name === layer.name,
            }));
            rasterLayersStore.onRasterLayerChanged(newRasters);
        }
        // Notify the store that the raster layers have changed
    }

    /**
     * Called when a data layer is changed. The data layer is changed by an action and then
     * notifies the store of the change.
     * @param {Object} layer
     * @param {String} action
     * @param {Object} value
     */
    async onDataLayerChange(layer, action, value) {
        const dataLayer = dataLayersStore.getLayersById(layer.resId);
        if (!dataLayer) return;

        // Reset change indicators
        dataLayer.onLayerChanged = false;
        dataLayer.onSequenceChanged = false;

        try {
            switch (action) {
                case "onVisibleChanged": {
                    Object.assign(dataLayer, {isVisible: value, onVisibleChanged: true});
                    break;
                }
                case "onLayerChanged": {
                    const geo_field_id = await this.orm.call(dataLayer.resModel, "set_gis_field_name", [
                        value.geo_field_id,
                    ]);
                    const attribute_field_id = await this.orm.call(dataLayer.resModel, "set_gis_field_name", [
                        value.attribute_field_id,
                    ]);
                    Object.assign(dataLayer, {
                        ...value,
                        geo_field_id,
                        attribute_field_id,
                        onLayerChanged: true,
                    });
                    break;
                }
                case "onSequenceChanged": {
                    Object.assign(dataLayer, {sequence: value, onSequenceChanged: true});
                    break;
                }
            }
        } catch (error) {
            console.error("Error handling data layer change:", error);
        }
    }

    async openFormViewDialog(actionId, options) {
        const view = await this.rpc("/web/action/load", {
            action_id: actionId,
        });
        this.addDialog(FormViewDialog, {
            viewId: view.view_id[0],
            ...options,
        });
    }

    async onEditButtonSelected(dataLayer) {
        await this.openFormViewDialog("spp_base_gis.action_spp_gis_data_layer_view", {
            resModel: dataLayer.resModel,
            title: _t("Editing Data layer"),
            resId: dataLayer.resId,
            onRecordSaved: (record) => this.onDataLayerChange(dataLayer, "onLayerChanged", record.data),
        });
    }

    async onEditRasterButtonSelected(layer) {
        await this.openFormViewDialog("spp_base_gis.action_spp_gis_raster_layer_form", {
            resModel: "spp.gis.raster.layer",
            title: _t("Editing Raster Layer"),
            resId: layer.id,
            onRecordSaved: (record) => this.onRasterChange(layer, record.data),
        });
    }

    /**
     * This method allows you to open/close the panel.
     */
    fold() {
        this.state.isFolded = !this.state.isFolded;
    }

    async openNewRaster() {
        await this.openFormViewDialog("spp_base_gis.action_spp_gis_raster_layer_form", {
            resModel: "spp.gis.raster.layer",
            title: _t("Creating Raster Layer"),
            onRecordSaved: async () => {
                await this.loadLayers();
                rasterLayersStore.onRasterLayerChanged(this.state.gisLayers.backgrounds);
            },
        });
    }
}

LayersPanel.template = "spp_base_gis.LayersPanel";
LayersPanel.props = {
    model: {type: String, optional: false},
    dataLayerModel: {type: Object, optional: false},
};
LayersPanel.components = {CheckBox, Layout, Notebook};
