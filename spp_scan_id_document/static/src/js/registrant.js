odoo.define(function (require) {
    const initialise_url = "http://localhost:12222/initialise";
    const readdocument_url = "http://localhost:12222/readdocument";
    const shutdown_url = "http://localhost:12222/shutdown";

    var Widget = require("web.Widget");
    var field_registry = require("web.field_registry");

    var DocumentReader = Widget.extend({
        template: "id_document_reader",
        xmlDependencies: ["/spp_scan_id_document/static/src/xml/registrant_widget.xml"],
        events: {
            click: "_onClick",
        },
        init: function (parent) {
            this._super(parent);
        },
        _onClick: function () {
            fetch(initialise_url, {
                method: "GET",
            }).then(() => {
                fetch(readdocument_url, {
                    method: "GET",
                })
                    .then((read_response) => read_response.text())
                    .then((response) => {
                        document.querySelector("textarea[name='id_document_details']").value = response;
                        $('textarea[name="id_document_details"]').trigger("change");
                        fetch(shutdown_url, {
                            method: "GET",
                        }).then(() => {
                            // Shutdown completed
                        });
                    });
            });
        },
    });

    var document_reader = new DocumentReader(this);
    document_reader.prependTo(".oe_button_box");

    field_registry.add("id_document_reader", DocumentReader);
});
