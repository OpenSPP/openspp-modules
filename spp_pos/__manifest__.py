# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
{
    "name": "OpenSPP POS",
    "summary": "The OpenSPP Pos module extends the standard Odoo Point of Sale system to facilitate secure redemption of social protection entitlements for beneficiaries. It performs real-time validation of entitlement codes and designates specific products purchasable using these benefits.",
    "category": "OpenSPP",
    "version": "17.0.1.3.0",
    "sequence": 1,
    "author": "OpenSPP.org",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "license": "LGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["jeremi", "gonzalesedwin1123"],
    "depends": ["base", "point_of_sale", "g2p_registry_base", "g2p_programs"],
    "assets": {
        "point_of_sale._assets_pos": [
            "spp_pos/static/src/view/action_button.xml",
            "spp_pos/static/src/view/popup_voucher.xml",
            "spp_pos/static/src/js/action_button.js",
            "spp_pos/static/src/js/popup_voucher.js",
            "spp_pos/static/src/js/check_keypress_entitlement.js",
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
