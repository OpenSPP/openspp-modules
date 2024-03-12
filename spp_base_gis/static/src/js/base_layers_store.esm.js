/** @odoo-module */

export class LayerStore {
    constructor() {
        if (this.constructor === LayerStore) {
            throw new Error("Abstract classes can't be instantiated.");
        }
    }

    setLayers(layers) {
        const newLayers = layers.map((layer) => {
            Object.defineProperty(layer, "isVisible", {
                value: false,
                writable: true,
            });
            layer.isVisible = this.getIsVisible(layer);
            return layer;
        });
        this.layers = newLayers;
    }

    getIsVisible(layer) {
        return Boolean(layer);
    }

    get getLayers() {
        return this.layers;
    }

    getLayersById(resId) {
        return this.layers.find((el) => el.resId === resId);
    }

    get count() {
        return this.layers.length;
    }
}
