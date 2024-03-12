/** @odoo-module */

import {GisArchParser} from "./gis_arch_parser.esm";
import {GisCompiler} from "./gis_compiler.esm";
import {GisController} from "./gis_controller/gis_controller.esm";
import {GisRenderer} from "./gis_renderer/gis_renderer.esm";
import {RelationalModel} from "@web/model/relational_model/relational_model";
import {_lt} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

export const gisView = {
    type: "gis",
    display_name: _lt("GIS"),
    icon: "fa fa-solid fa-map",
    multiRecord: true,
    ArchParser: GisArchParser,
    Controller: GisController,
    Model: RelationalModel,
    Renderer: GisRenderer,
    Compiler: GisCompiler,

    props: (genericProps, view) => {
        const {ArchParser} = view;
        const {arch, relatedModels, resModel} = genericProps;
        const archInfo = new ArchParser().parse(arch, relatedModels, resModel);

        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
            archInfo,
        };
    },
};

registry.category("views").add("gis", gisView);
