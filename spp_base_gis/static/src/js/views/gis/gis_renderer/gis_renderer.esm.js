/** @odoo-module */

import {Component, onMounted, onPatched, onWillStart, reactive, useState} from "@odoo/owl";
import {addFieldDependencies, extractFieldsFromArchInfo} from "@web/model/relational_model/utils";
import {LayersPanel} from "../layers_panel/layers_panel.esm";
import {RelationalModel} from "@web/model/relational_model/relational_model";
import {dataLayersStore} from "../../../data_layers_store.esm";
import {loadBundle} from "@web/core/assets";
import {parseXML} from "@web/core/utils/xml";
import {rasterLayersStore} from "../../../raster_layers_store.esm";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

// GisRenderer component definition.
export class GisRenderer extends Component {
    // Component setup lifecycle hook.
    setup() {
        // Initialize component state.
        this.state = useState({
            isModified: false,
            isFit: false,
        });

        // Initialize properties to store model information.
        this.models = [];
        this.cfg_models = [];
        this.dataLayerModel = {};

        this.sources = [];
        this.layers = [];
        this.geoTypes = ["Polygon", "LineString", "Point"];

        // Create reactive layer stores with change handlers.
        this.rasterLayersStore = reactive(rasterLayersStore, () => this.onRasterLayerChanged());
        this.dataLayersStore = reactive(dataLayersStore, () => this.onDataLayerChanged());

        // Initialize Odoo services.
        this.orm = useService("orm");
        this.view = useService("view");
        this.user = useService("user");
        this.fields = useService("field");
        this.actionService = useService("action");
        this.rpc = useService("rpc");

        this.sourceId = `gisViewSource`;

        // Load additional services required by the RelationalModel.
        this.services = RelationalModel.services.reduce((services, serviceKey) => {
            services[serviceKey] = useService(serviceKey);
            return services;
        }, {});

        this.getMapTilerKey();

        onWillStart(async () => {
            return Promise.all([
                // Load external JavaScript and CSS libraries.
                loadBundle({
                    jsLibs: [
                        "/spp_base_gis/static/lib/turf-3.0.11/turf.min.js",
                        "/spp_base_gis/static/lib/maptiler-sdk-js-1.2.0/maptiler-sdk.umd.min.js",
                        "/spp_base_gis/static/lib/mapbox-gl-draw-1.2.0/mapbox-gl-draw.js",
                        "/spp_base_gis/static/lib/maptiler-geocoding-control-1.2.0/maptilersdk.umd.js",
                    ],
                    cssLibs: [
                        "/spp_base_gis/static/lib/maptiler-sdk-js-1.2.0/maptiler-sdk.css",
                        "/spp_base_gis/static/lib/mapbox-gl-draw-1.2.0/mapbox-gl-draw.css",
                        "/spp_base_gis/static/lib/maptiler-geocoding-control-1.2.0/style.css",
                    ],
                }),
                this.loadDataLayerForm(),
                (this.isGisAdmin = await this.user.hasGroup("spp_base_gis.group_gis_admin")),
            ]);
        });

        onMounted(() => {
            maptilersdk.config.apiKey = this.mapTilerKey;
            this.setupSourceAndLayer();

            this.renderMap();
        });

        onPatched(() => {
            this.setupFeatureCollection();
            this.map.getSource(this.sourceId).setData(this.featureCollection);
        });
    }

    async getMapTilerKey() {
        try {
            const response = await this.rpc("/get_maptiler_api_key");
            this.mapTilerKey = response.mapTilerKey;
            if (response.mapTilerKey) {
                this.mapTilerKey = response.mapTilerKey;
            } else {
                console.log("Error: Api Key not found.");
            }
        } catch (error) {
            console.error("Error fetching environment variable:", error);
        }
    }

    setupFeatureCollection() {
        const records = this.props.data.records;
        const features = [];
        this.dataLayersStore.getLayers.forEach((layer) => {
            records.forEach((item) => {
                const values = item._values || item;
                const jsonGeometry = values[layer.geo_field_id[1]];
                if (jsonGeometry) {
                    features.push({
                        type: "Feature",
                        geometry: JSON.parse(jsonGeometry),
                        properties: {
                            resModel: item.resModel,
                            resId: item.config.resId,
                        },
                    });
                }
            });
            this.createDefaultDataLayers(layer);
        });

        this.featureCollection = {
            type: "FeatureCollection",
            features,
        };
    }

    setupSourceAndLayer() {
        this.rasterLayersStore.getLayers.forEach((layer) => {
            if (layer.raster_type === "d_wms") {
                const rasterLayerSourceId = `wms_${layer.id}`;
                this.createWMSRasterSource(rasterLayerSourceId, layer);
                this.createWMSRasterLayer(rasterLayerSourceId, layer);
            }
            if (layer.raster_type === "image") {
                const sourceId = `image_${layer.id}`;
                this.createImageRasterSource(sourceId, layer);
                this.createImageRasterLayer(sourceId, layer);
            }
            if (layer.raster_type === "osm" && layer.isVisible) {
                this.defaultRaster = layer;
            }
        });

        this.setupFeatureCollection();

        this.createDefaultDataSource(this.featureCollection);
    }

    async renderMap() {
        let defaultCenter = [124.74037191, 7.83479874];
        let defaultZoom = 6;
        const editInfo = await this.orm.call(this.props.data._config.resModel, "get_edit_info_for_gis", []);

        if (editInfo.default_center) {
            defaultCenter = JSON.parse(editInfo.default_center);
        }
        if (editInfo.default_zoom) {
            defaultZoom = editInfo.default_zoom;
        }

        if (this.featureCollection.features.length > 0) {
            const centroid = turf.centroid(this.featureCollection);
            defaultCenter = centroid.geometry.coordinates;
        }

        let defaultMapStyle = this.getMapStyle();

        if (this.defaultRaster) {
            if (this.defaultRaster.raster_style.includes("-")) {
                const rasterStyleArray = this.defaultRaster.raster_style.toUpperCase().split("-");
                defaultMapStyle = maptilersdk.MapStyle[rasterStyleArray[0]][rasterStyleArray[1]];
            } else {
                defaultMapStyle = maptilersdk.MapStyle[this.defaultRaster.raster_style.toUpperCase()];
            }
        }

        this.map = new maptilersdk.Map({
            container: "olmap",
            style: defaultMapStyle,
            center: defaultCenter,
            zoom: defaultZoom,
        });

        this.map.on("styledata", () => {
            this.addSourceToMap();
            this.addLayerToMap();
        });

        this.map.on("load", async () => {
            this.addSourceToMap();
            this.addLayerToMap();
        });

        this.addMouseInteraction();

        const gc = new maptilersdkMaptilerGeocoder.GeocodingControl({});
        this.map.addControl(gc, "top-left");
    }

    getMapStyle(layer) {
        let mapStyle = maptilersdk.MapStyle.STREETS;

        if (layer) {
            if (layer.raster_style.includes("-")) {
                const rasterStyleArray = layer.raster_style.toUpperCase().split("-");
                mapStyle = maptilersdk.MapStyle[rasterStyleArray[0]][rasterStyleArray[1]];
            } else {
                mapStyle = maptilersdk.MapStyle[layer.raster_style.toUpperCase()];
            }
        }
        return mapStyle;
    }

    addMouseInteraction() {
        let formViewId = null;

        if (this.env.config && this.env.config.views) {
            const viewIds = this.env.config.views;
            formViewId = [viewIds.find((subList) => subList.includes("form"))];
        }

        this.dataLayersStore.getLayers.forEach((layer) => {
            this.map.on("click", layer.id, (e) => {
                const {resModel, resId} = e.features[0].properties;
                this.props.openFormRecord(resModel, resId, formViewId);
            });

            // Change the cursor to a pointer when the mouse is over the places layer.
            this.map.on("mouseenter", layer.id, () => {
                this.map.getCanvas().style.cursor = "pointer";
            });
            // Change it back to a pointer when it leaves.
            this.map.on("mouseleave", layer.id, () => {
                this.map.getCanvas().style.cursor = "";
            });
        });
    }

    addSourceToMap() {
        this.sources.forEach((source) => {
            if (!this.map.getSource(source[0])) {
                this.map.addSource(source[0], source[1]);
            }
        });
    }

    createWMSRasterSource(sourceId, layer) {
        const url = `${layer.url}?layers=${layer.wms_layer_name}&tiled=true&service=WMS&request=GetMap&styles=&format=image/png&transparent=true&width=256&height=256&crs=EPSG:3857&srs=EPSG:3857&bbox={bbox-epsg-3857}`;
        this.sources.push([
            sourceId,
            {
                type: "raster",
                tiles: [url],
                tileSize: 256,
            },
        ]);
    }

    createWMSRasterLayer(sourceId, layer) {
        const opacity = Math.min(1, Math.max(0, layer.opacity));

        this.layers.push({
            type: "raster",
            id: sourceId,
            source: sourceId,
            paint: {
                "raster-opacity": opacity,
            },
            layout: {
                visibility: layer.isVisible ? "visible" : "none",
            },
        });
    }

    createImageRasterSource(sourceId, layer) {
        this.sources.push([
            sourceId,
            {
                type: "image",
                url: layer.image_url,
                coordinates: [
                    [layer.x_min, layer.y_max], // Top-left
                    [layer.x_max, layer.y_max], // Top-right
                    [layer.x_max, layer.y_min], // Bottom-right
                    [layer.x_min, layer.y_min], // Bottom-left
                ],
            },
        ]);
    }

    createImageRasterLayer(sourceId, layer) {
        const opacity = Math.min(1, Math.max(0, layer.image_opacity));

        this.layers.push({
            type: "raster",
            id: sourceId,
            source: sourceId,
            paint: {
                "raster-opacity": opacity,
            },
            layout: {
                visibility: layer.isVisible ? "visible" : "none",
            },
        });
    }

    createDefaultDataSource(features) {
        this.sources.push([
            this.sourceId,
            {
                type: "geojson",
                data: features,
            },
        ]);
    }

    createDefaultDataLayers(layer) {
        let layer_obj = {};
        const visibility = layer.isVisible ? "visible" : "none";
        const geoType = layer.geo_field_id[4];
        const opacity = Math.min(1, Math.max(0, layer.layer_opacity));

        if (geoType === "geo_polygon") {
            layer_obj = {
                id: layer.id,
                type: "fill",
                source: this.sourceId,
                filter: ["all", ["==", "$type", "Polygon"], ["!=", "mode", "static"]],
                layout: {
                    visibility: visibility,
                },
                paint: {
                    "fill-color": layer.begin_color,
                    "fill-opacity": opacity,
                },
            };
        }

        if (geoType === "geo_point") {
            layer_obj = {
                id: layer.id,
                type: "circle",
                source: this.sourceId,
                filter: ["all", ["==", "$type", "Point"], ["!=", "mode", "static"]],
                layout: {
                    visibility: visibility,
                },
                paint: {
                    "circle-color": layer.begin_color,
                    "circle-opacity": opacity,
                },
            };
        }

        if (geoType === "geo_line") {
            layer_obj = {
                id: layer.id,
                type: "line",
                source: this.sourceId,
                filter: ["all", ["==", "$type", "LineString"], ["!=", "mode", "static"]],
                layout: {
                    visibility: visibility,
                },
                paint: {
                    "line-color": layer.begin_color,
                    "line-opacity": opacity,
                    "line-width": 4,
                },
            };
        }

        this.layers.push(layer_obj);
    }

    addLayerToMap() {
        this.layers.forEach((layer) => {
            if (!this.map.getLayer(layer.id)) {
                this.map.addLayer(layer);
            }
        });
    }

    async loadDataLayerForm() {
        await this.loadView("spp.gis.data.layer", "form");
    }

    async loadView(model, view) {
        const viewRegistry = registry.category("views");
        const fields = await this.fields.loadFields(model, {
            attributes: ["store", "searchable", "type", "string", "relation", "selection", "related"],
        });
        const {relatedModels, views} = await this.view.loadViews({
            resModel: model,
            views: [[false, view]],
        });
        const {ArchParser, Model} = viewRegistry.get(view);

        const xmlDoc = parseXML(views[view].arch);
        const archInfo = new ArchParser().parse(xmlDoc, relatedModels, model);

        if (model === "spp.gis.data.layer") {
            const notAllowedField = Object.keys(fields).filter(
                (field) => fields[field].relation === "ir.ui.view"
            );
            notAllowedField.forEach((field) => {
                delete field[field];
            });
        }

        const {activeFields, arch_fields} = extractFieldsFromArchInfo(archInfo, fields);
        addFieldDependencies(activeFields, arch_fields, this.progressBarAggregateFields(archInfo));

        const modelConfig = {
            model,
            activeFields,
            openGroupsByDefault: true,
            domain: [],
            orderBy: [],
            groupBy: {},
            resModel: model,
            fields,
        };

        const searchParams = {
            config: modelConfig,
            limit: 10000,
            groupsLimit: Number.MAX_SAFE_INTEGER,
            countLimit: archInfo.countLimit || Number.MAX_SAFE_INTEGER,
            orderBy: [],
            resModel: model,
        };

        if (model === "spp.gis.data.layer") {
            this.dataLayerModel = new Model(this.env, searchParams, this.services);
            await this.dataLayerModel.load(searchParams);
        } else {
            const existingModel = this.models.find((e) => e.model.resModel === model);
            if (!existingModel) {
                const toLoadModel = new Model(this.env, searchParams, this.services);
                await toLoadModel.load();
                this.models.push({model: toLoadModel.root, archInfo});
            }
        }
    }

    progressBarAggregateFields(archInfo) {
        const {sumField} = archInfo.progressAttributes || {};
        return sumField ? [sumField] : [];
    }

    async onDataLayerChanged() {
        for (const layer of this.dataLayersStore.getLayers) {
            const visibility = layer.isVisible ? "visible" : "none";
            const geoType = layer.geo_field_id[4];
            const opacity = Math.min(1, Math.max(0, layer.layer_opacity));
            let layerType = "";

            if (geoType === "geo_point") {
                layerType = "circle";
            }
            if (geoType === "geo_line") {
                layerType = "line";
            }
            if (geoType === "geo_polygon") {
                layerType = "fill";
            }

            this.map.setLayoutProperty(layer.id, "visibility", visibility);
            this.map.setPaintProperty(layer.id, `${layerType}-color`, layer.begin_color);
            this.map.setPaintProperty(layer.id, `${layerType}-opacity`, opacity);
        }
    }

    async onRasterLayerChanged() {
        for (const layer of this.rasterLayersStore.getLayers) {
            if (layer.raster_type === "d_wms") {
                const rasterLayerSourceId = `wms_${layer.id}`;
                const visibility = layer.isVisible ? "visible" : "none";
                const opacity = Math.min(1, Math.max(0, layer.opacity));

                this.map.setLayoutProperty(rasterLayerSourceId, "visibility", visibility);
                this.map.setPaintProperty(rasterLayerSourceId, "raster-opacity", opacity);
            } else if (layer.raster_type === "image") {
                const sourceId = `image_${layer.id}`;
                const visibility = layer.isVisible ? "visible" : "none";
                const opacity = Math.min(1, Math.max(0, layer.image_opacity));

                const source = this.map.getSource(sourceId);
                if (source) {
                    source.updateImage({
                        url: layer.image_url,
                        coordinates: [
                            [layer.x_min, layer.y_max], // Top-left
                            [layer.x_max, layer.y_max], // Top-right
                            [layer.x_max, layer.y_min], // Bottom-right
                            [layer.x_min, layer.y_min], // Bottom-left
                        ],
                    });
                    this.map.setLayoutProperty(sourceId, "visibility", visibility);
                    this.map.setPaintProperty(sourceId, "raster-opacity", opacity);
                }
            } else if (layer.raster_type === "osm" && layer.isVisible) {
                this.map.setStyle(this.getMapStyle(layer));
            }
        }
    }
}

GisRenderer.template = "spp_base_gis.GisRenderer";
GisRenderer.props = {
    isSavedOrDiscarded: {type: Boolean},
    archInfo: {type: Object},
    data: {type: Object},
    openFormRecord: {type: Function},
    editable: {type: Boolean, optional: true},
};
GisRenderer.components = {LayersPanel};
