/** @odoo-module */

import {archParseBoolean, getActiveActions} from "@web/views/utils";
import {Field} from "@web/views/fields/field";
import {Widget} from "@web/views/widgets/widget";
import {visitXML} from "@web/core/utils/xml";

export class GisArchParser {
    parse(xmlDoc, models, modelName) {
        const templateDocs = {};
        const fieldNodes = {};
        const widgetNodes = {};
        let widgetNextId = 0;
        const gisAttr = {
            editable: archParseBoolean(xmlDoc.getAttribute("editable")),
        };

        // Extracting multiple attributes using destructuring
        const {
            js_class: jsClass,
            limit,
            count_limit: countLimit,
            class: className = null,
            default_group_by: defaultGroupBy,
        } = xmlDoc.attributes;

        const activeActions = getActiveActions(xmlDoc);
        Object.assign(activeActions, {
            archiveGroup: archParseBoolean(xmlDoc.getAttribute("archivable"), true),
            createGroup: archParseBoolean(xmlDoc.getAttribute("group_create"), true),
            deleteGroup: archParseBoolean(xmlDoc.getAttribute("group_delete"), true),
            editGroup: archParseBoolean(xmlDoc.getAttribute("group_edit"), true),
            quickCreate: activeActions.create && archParseBoolean(xmlDoc.getAttribute("quick_create"), true),
        });

        visitXML(xmlDoc, (node) => {
            if (node.tagName === "field") {
                const fieldInfo = Field.parseFieldNode(node, models, modelName, "gis", jsClass);
                fieldNodes[fieldInfo.name] = fieldInfo;
                node.setAttribute("field_id", fieldInfo.name);
            }

            if (node.tagName === "widget") {
                const widgetId = `widget_${++widgetNextId}`;
                widgetNodes[widgetId] = Widget.parseWidgetNode(node);
                node.setAttribute("widget_id", widgetId);
            }

            // Collect template docs based on the 't-name' attribute
            if (node.hasAttribute("t-name")) {
                templateDocs[node.getAttribute("t-name")] = node;
            }
        });

        // Return parsed architecture details
        return {
            activeActions,
            className,
            defaultGroupBy,
            templateDocs,
            activeFields: fieldNodes,
            fieldNodes,
            widgetNodes,
            limit: limit ? parseInt(limit, 10) : null,
            countLimit: countLimit ? parseInt(countLimit, 10) : null,
            xmlDoc,
            ...gisAttr,
        };
    }
}
