import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-openspp-demo",
    description="Meta package for openspp-openspp-demo Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-g2p_connect_demo1>=15.0dev,<15.1dev',
        'odoo-addon-spp_base_demo>=15.0dev,<15.1dev',
        'odoo-addon-spp_demo>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
