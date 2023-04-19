import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-openspp-program",
    description="Meta package for openspp-openspp-program Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-g2p_entitlement_cash>=15.0dev,<15.1dev',
        'odoo-addon-spp_basic_cash_entitlement_spent>=15.0dev,<15.1dev',
        'odoo-addon-spp_dashboard>=15.0dev,<15.1dev',
        'odoo-addon-spp_entitlement_basket>=15.0dev,<15.1dev',
        'odoo-addon-spp_entitlement_in_kind>=15.0dev,<15.1dev',
        'odoo-addon-spp_pos>=15.0dev,<15.1dev',
        'odoo-addon-spp_programs>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
