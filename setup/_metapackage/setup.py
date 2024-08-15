import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-openspp-modules",
    description="OpenSPP Modules",
    version=version,
    dependency_links=[
        'https://github.com/OpenSPP/openg2p-registry/archive/refs/tags/v17.0.1.2-openspp.tar.gz',
        'https://github.com/OpenSPP/openg2p-program/archive/refs/tags/v17.0.1.2-openspp.tar.gz',
    ],
    install_requires=[
        'odoo-addons-spp_base>=17.0,<17.1',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 17.0',
    ]
)
