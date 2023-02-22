import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-openspp-registry",
    description="Meta package for openspp-openspp-registry Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-spp_area>=15.0dev,<15.1dev',
        'odoo-addon-spp_change_request>=15.0dev,<15.1dev',
        'odoo-addon-spp_consent>=15.0dev,<15.1dev',
        'odoo-addon-spp_custom_field>=15.0dev,<15.1dev',
        'odoo-addon-spp_custom_field_custom_filter>=15.0dev,<15.1dev',
        'odoo-addon-spp_custom_fields_ui>=15.0dev,<15.1dev',
        'odoo-addon-spp_custom_filter>=15.0dev,<15.1dev',
        'odoo-addon-spp_event_data>=15.0dev,<15.1dev',
        'odoo-addon-spp_event_demo>=15.0dev,<15.1dev',
        'odoo-addon-spp_idpass>=15.0dev,<15.1dev',
        'odoo-addon-spp_idqueue>=15.0dev,<15.1dev',
        'odoo-addon-spp_rest_auth_jwt>=15.0dev,<15.1dev',
        'odoo-addon-spp_scan_id_document>=15.0dev,<15.1dev',
        'odoo-addon-spp_service_points>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
