/** @odoo-module */
import {LayerStore} from "./base_layers_store.esm";
import {reactive} from "@odoo/owl";

class DataLayersStore extends LayerStore {
    getIsVisible(layer) {
        return layer.active_on_startup;
    }
}

export const dataLayersStore = reactive(new DataLayersStore());
