# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP Registry - Scan ID Document",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/openspp/openspp-registry",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": ["base", "g2p_registry_base"],
    "data": ["views/registrant.xml"],
    "assets": {
        "web.assets_backend": [
            "/spp_scan_id_document/static/src/js/registrant.js",
            "/spp_scan_id_document/static/src/css/registrant_widget.css",
        ],
        "web.assets_qweb": [
            "/spp_scan_id_document/static/src/xml/registrant_widget.xml"
        ],
    },
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
