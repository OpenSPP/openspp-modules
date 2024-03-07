/** @odoo-module **/

import {Component} from "@odoo/owl";
import {RPCErrorDialog} from "@web/core/errors/error_dialogs";
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";

export class DocumentReader extends Component {
    setup() {
        this.widget = {
            icon: "fa fa-fw o_button_icon fa-external-link",
            classes: "btn oe_stat_button oe_edit_only",
            classes_field: "btn btn-primary oe_edit_only",
            text: "Scan Document",
        };
        this.initialise_url = DocumentReader.initialise_url;
        this.get_url = DocumentReader.readdocument_url;
    }

    onClick() {
        const {fetch} = browser;
        fetch(this.initialise_url, {
            method: "GET",
        })
            .then((initialise_response) => {
                if (initialise_response.ok) {
                    fetch(this.get_url, {
                        method: "GET",
                    })
                        .then((read_response) => read_response.text())
                        .then((response) => {
                            this.props.record._update({id_document_details: response});
                        });
                }
            })
            .catch(() => {
                this.props.record.model.dialog.add(RPCErrorDialog, {
                    message:
                        "ERROR! Unable to connect to scanner. Make sure scanner is working and connected.",
                    traceback:
                        "ERROR! Unable to connect to scanner. Make sure scanner is working and connected.",
                });
            });
    }
}

DocumentReader.initialise_url = "http://localhost:12212/initialise";
DocumentReader.readdocument_url = "http://localhost:12212/readdocument";
DocumentReader.shutdown_url = "http://localhost:12212/shutdown";
DocumentReader.qrcode_url = "http://localhost:12212/qrcode";
DocumentReader.template = "spp_scan_id_document.id_document_reader";

class DocumentReaderField extends DocumentReader {}

DocumentReaderField.template = "spp_scan_id_document.id_document_reader_field";

class QrDocumentReader extends DocumentReader {
    setup() {
        super.setup();
        this.get_url = DocumentReader.qrcode_url;
    }
}

class QrDocumentReaderField extends QrDocumentReader {}

QrDocumentReaderField.template = "spp_scan_id_document.id_document_reader_field";

export const documentReader = {
    component: DocumentReader,
};

export const documentReaderField = {
    component: DocumentReaderField,
};

export const qrDocumentReader = {
    component: QrDocumentReader,
};

export const qrDocumentReaderField = {
    component: QrDocumentReaderField,
};

registry.category("fields").add("id_document_reader", documentReader);
registry.category("fields").add("id_document_reader_field", documentReaderField);

registry.category("fields").add("id_document_qrreader", qrDocumentReader);
registry.category("fields").add("id_document_qrreader_field", qrDocumentReaderField);
