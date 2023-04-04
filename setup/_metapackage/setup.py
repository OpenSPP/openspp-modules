import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-openspp-api",
    description="Meta package for openspp-openspp-api Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-spp_api>=15.0dev,<15.1dev',
        'odoo-addon-spp_base_api>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
