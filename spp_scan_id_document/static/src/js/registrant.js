odoo.define("spp_scan_id_document.field", function (require) {
    const initialise_url = "http://localhost:12212/initialise";
    const readdocument_url = "http://localhost:12212/readdocument";
    const shutdown_url = "http://localhost:12212/shutdown";
    const qrcode_url = "http://localhost:12212/qrcode";

    var field_registry = require("web.field_registry");
    var AbstractField = require("web.AbstractField");
    var Dialog = require("web.Dialog");

    var DocumentReader = AbstractField.extend({
        template: "id_document_reader",
        xmlDependencies: ["/spp_scan_id_document/static/src/xml/registrant_widget.xml"],
        events: {
            click: "_onClick",
        },
        init: function () {
            this._super.apply(this, arguments);
            this.onclick_started = false;
            this.initialise_url = initialise_url;
            this.get_url = readdocument_url;
            this.shutdown_url = shutdown_url;

            const default_button_text = "Scan Document";
            const default_icon = "fa fa-fw o_button_icon fa-external-link";
            const default_classes = "btn oe_stat_button oe_edit_only";
            const default_classes_field = "btn btn-primary oe_edit_only";
            var icon = "";
            if (this.attrs.icon) {
                icon = "fa fa-fw o_button_icon " + this.attrs.icon;
            }
            this.text = this.attrs.text || this.attrs.title || this.attrs.string || default_button_text;
            this.icon = icon || default_icon;
            this.classes = this.attrs.classes || this.attrs.classNames || default_classes;
            this.classes_field = this.attrs.classes || default_classes_field;
        },
        _onClick: function () {
            if (!this.onclick_started) {
                this.onclick_started = true;
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
                                    if (response === "{}") {
                                        this.onclick_started = false;
                                    } else {
                                        this._setValue(response, "UPDATE");
                                        fetch(this.shutdown_url, {
                                            method: "GET",
                                        }).then(() => {
                                            // Shutdown completed
                                            this._setValue(" ", "UPDATE");
                                            this.onclick_started = false;
                                        });
                                    }
                                });
                        } else {
                            this.onclick_started = false;
                        }
                    })
                    .catch(() => {
                        this.onclick_started = false;
                        Dialog.alert(
                            this,
                            "ERROR! Unable to connect to scanner. Make sure scanner is working and connected."
                        );
                    });
            }
        },
    });

    var DocumentReaderField = DocumentReader.extend({
        template: "id_document_reader_field",
    });

    var QrDocumentReader = DocumentReader.extend({
        template: "id_document_reader",
        init: function () {
            this._super.apply(this, arguments);
            this.get_url = qrcode_url;
        },
    });

    var QrDocumentReaderField = QrDocumentReader.extend({
        template: "id_document_reader_field",
    });

    // Widgets for a button with fa-external-link design.
    field_registry.add("id_document_reader", DocumentReader);
    field_registry.add("id_document_qrreader", QrDocumentReader);

    // Widgets for a simple button without fa-external-link design.
    field_registry.add("id_document_reader_field", DocumentReaderField);
    field_registry.add("id_document_qrreader_field", QrDocumentReaderField);
});
