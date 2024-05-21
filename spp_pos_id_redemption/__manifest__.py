# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP POS: ID Redemption",
    "category": "OpenSPP",
    "version": "17.0.1.0.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Beta",
    "maintainers": ["jeremi", "gonzalesedwin1123", "reichie020212"],
    "depends": [
        "base",
        "point_of_sale",
        "spp_pos",
        "g2p_registry_base",
        "g2p_registry_individual",
        "g2p_registry_group",
        "g2p_programs",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "spp_pos_id_redemption/static/src/view/popup_voucher.xml",
            "spp_pos_id_redemption/static/src/view/product_list.xml",
            "spp_pos_id_redemption/static/src/js/popup_voucher.js",
            "spp_pos_id_redemption/static/src/js/product_list.js",
            "spp_pos_id_redemption/static/src/js/pos_store.js",
        ],
    },
    "data": [
        "views/registrant_view.xml",
    ],
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}