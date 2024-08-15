import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-modules",
    description="OpenSPP Modules",
    version=version,
    install_requires=[
        'odoo-addons-spp_base>=17.0,<17.1',
        'openg2p-registry @ git+https://github.com/OpenSPP/openg2p-registry.git@v17.0.1.2-openspp#egg=openg2p-registry',
        'openg2p-program @ git+https://github.com/OpenSPP/openg2p-program.git@v17.0.1.2-openspp#egg=openg2p-program'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 17.0',
    ]
)
