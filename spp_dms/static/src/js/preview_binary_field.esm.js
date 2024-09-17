/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useFileViewer} from "@web/core/file_viewer/file_viewer_hook";
import {useService} from "@web/core/utils/hooks";

export class PreviewRecordWidget extends Component {
    setup() {
        // Services setup
        this.store = useService("mail.store");
        this.fileViewer = useFileViewer();
        this.orm = useService("orm");
        this.fileName = this.props.record.data.name || "Unknown File";
    }

    // Method to handle file preview
    async onFilePreview(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        // Fetch the binary content of the file
        const recordId = this.props.record.resId;
        const model = this.props.record.resModel;
        const mimetype = this.props.record.data.mimetype;
        const filename = this.props.record.data.name;

        try {
            // Use the ORM service to read the binary data from the record
            const result = await this.orm.read(model, [recordId], ["content"]);

            if (result && result.length > 0 && result[0].content) {
                const attachment = this.store.Attachment.insert({
                    id: recordId,
                    filename: filename,
                    name: filename,
                    mimetype: mimetype,
                    raw: result[0].content_file,
                    model_name: model,
                });

                // Open the file viewer with the loaded attachment
                this.fileViewer.open(attachment);
            } else {
                console.error("No binary content found.");
            }
        } catch (error) {
            console.error("Error fetching binary content:", error);
        }
    }
}

PreviewRecordWidget.template = "dms.PreviewBinaryField";

// Register the widget in the Odoo registry
const previewRecordWidget = {
    component: PreviewRecordWidget,
    display_name: "Preview File Widget",
    supportedTypes: ["binary"],
};

// Register this widget as an independent widget in the field registry
registry.category("fields").add("preview_widget", previewRecordWidget);
