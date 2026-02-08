{
    "name": "OpenSPP Metrics Core",
    "summary": "External and internal metrics registry, feature store, and APIs",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "OpenSPP Community",
    "website": "https://github.com/OpenSPP/openspp-modules",
    "category": "Tools",
    "depends": [
        "base",
        "spp_base_common",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/menu_root.xml",
        # Load actions and views before menus to avoid ParseError on unresolved actions
        "views/metrics_admin_views.xml",
        "views/wizard_views.xml",
        "views/provider_views.xml",
        "views/registry_inspect_views.xml",
        "views/settings_wizard_views.xml",
        "views/menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
