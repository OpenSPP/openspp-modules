import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-openspp-demo",
    description="Meta package for openspp-openspp-demo Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-g2p_connect_demo>=15.0dev,<15.1dev',
        'odoo-addon-spp_base_demo>=15.0dev,<15.1dev',
        'odoo-addon-spp_change_request_add_children_demo>=15.0dev,<15.1dev',
        'odoo-addon-spp_custom_filter_ui>=15.0dev,<15.1dev',
        'odoo-addon-spp_demo>=15.0dev,<15.1dev',
        'odoo-addon-spp_event_demo>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
