/** @odoo-module */

import {LayerStore} from "./base_layers_store.esm";
import {reactive} from "@odoo/owl";

class RasterLayersStore extends LayerStore {
    getIsVisible(layer) {
        return layer.visible_on_load;
    }
    /**
     * This is called when a raster layer is changed. This will notify observers of the change.
     * @param {*} newLayers
     */
    onRasterLayerChanged(newLayers) {
        this.layers = newLayers;
    }

    getLayersById(id) {
        return this.layers.find((el) => el.id === id);
    }
}

export const rasterLayersStore = reactive(new RasterLayersStore());
