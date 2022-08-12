# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP POS",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "LGPL-3",
    "depends": ["base", "point_of_sale", "g2p_registry_base", "g2p_programs"],
    "assets": {
        "point_of_sale.assets": [
            "spp_pos/static/src/js/models.js",
            "spp_pos/static/src/js/action_button.js",
            "spp_pos/static/src/js/popup_voucher.js",
            "spp_pos/static/src/js/check_keypress_entitlement.js",
        ],
        "web.assets_qweb": [
            "spp_pos/static/src/view/action_button.xml",
            "spp_pos/static/src/view/popup_voucher.xml",
        ],
    },
    "data": [
        "data/entitlement_product.xml",
        "views/product_template_views.xml",
    ],
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
