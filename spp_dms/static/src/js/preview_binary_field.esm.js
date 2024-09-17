/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useFileViewer} from "@web/core/file_viewer/file_viewer_hook";
import {useService} from "@web/core/utils/hooks";

export class PreviewRecordWidget extends Component {
    setup() {
        this.store = useService("mail.store");
        this.fileViewer = useFileViewer();
    }

    async onFilePreview(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        const self = this;
        const attachment = this.store.Attachment.insert({
            id: self.props.record.resId,
            filename: self.props.record.data.name || "",
            name: self.props.record.data.name || "",
            mimetype: self.props.record.data.mimetype,
            model_name: self.props.record.resModel,
        });
        this.fileViewer.open(attachment);
    }
}

PreviewRecordWidget.template = "dms.PreviewBinaryField";

const previewRecordWidget = {
    component: PreviewRecordWidget,
    display_name: "Preview File Widget",
    supportedTypes: ["binary"],
};

registry.category("fields").add("preview_widget", previewRecordWidget);
