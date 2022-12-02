odoo.define("spp_scan_id_document.field", function (require) {
    const initialise_url = "http://localhost:12212/initialise";
    const readdocument_url = "http://localhost:12212/readdocument";
    const shutdown_url = "http://localhost:12212/shutdown";
    const qrcode_url = "http://localhost:12212/qrcode";

    var field_registry = require("web.field_registry");
    var AbstractField = require("web.AbstractField");

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
        },
        _onClick: function () {
            if (!this.onclick_started) {
                this.onclick_started = true;
                fetch(this.initialise_url, {
                    method: "GET",
                }).then((initialise_response) => {
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
                                        this.onclick_started = false;
                                    });
                                }
                            });
                    } else {
                        this.onclick_started = false;
                    }
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
    field_registry.add("id_document_reader", DocumentReader); // Calls readdocument api
    field_registry.add("id_document_qrreader", QrDocumentReader); // Calls qrcode api

    // widgets for a simple button without fa-external-link design.
    field_registry.add("id_document_reader_field", DocumentReaderField); // Calls readdocument api
    field_registry.add("id_document_qrreader_field", QrDocumentReaderField); // Calls qrcode api
});
