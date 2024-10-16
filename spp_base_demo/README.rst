=================
OpenSPP Base Demo
=================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:8fad1c221cd46ddf8909226c36336e809b26beb4d6c145696801e74f7c529440
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_base_demo
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP Base Demo
=================

This module provides demonstration data for the OpenSPP system. It
populates the database with sample records for various entities,
allowing users to explore the system's functionalities with
pre-populated data.

Purpose
-------

The primary purpose of the `spp_base_demo <spp_base_demo>`__ module is
to:

-  **Provide realistic sample data:** Offers a pre-configured dataset
   that mimics real-world scenarios, enabling users to interact with the
   system as if it were managing actual social protection programs and
   registries.
-  **Facilitate user training and exploration:** Allows new users to
   familiarize themselves with the system's interface, data structures,
   and workflows without having to manually create large amounts of test
   data.
-  **Showcase system capabilities:** Demonstrates the potential of
   OpenSPP by illustrating how different modules interact and how data
   flows through the system.

Module Dependencies and Integration
-----------------------------------

-  `g2p_registry_base <g2p_registry_base>`__ (G2P Registry: Base):
   Utilizes the base registry module to populate the system with sample
   registrant data, including individuals and potentially groups.
-  `g2p_programs <g2p_programs>`__ (G2P Programs): Leverages the
   programs module to create demo programs, define eligibility criteria,
   and potentially simulate program cycles and beneficiary enrollment.
-  `product <product>`__ (Products): Utilizes the product module to
   create sample products, potentially representing goods or services
   distributed through social protection programs.
-  `stock <stock>`__ (Inventory): May potentially integrate with the
   inventory module to manage and track the stock levels of goods
   related to program benefits.

Additional Functionality and Data Examples
------------------------------------------

The `spp_base_demo <spp_base_demo>`__ module includes data files that
populate the database with sample records for various entities. Here are
some examples:

-  **Users Data (data/users_data.xml):** Creates demo user accounts with
   different roles and permissions, allowing users to explore the system
   from various perspectives.
-  **Gender Data (data/gender_data.xml):** Defines common gender options
   used for registrant demographic information.
-  **Product Data (data/product_data.xml):** Creates sample product
   records, potentially categorized by type, to represent goods
   distributed through programs.

Conclusion
----------

The `spp_base_demo <spp_base_demo>`__ module serves as a valuable tool
for users, implementers, and trainers to understand and explore the
OpenSPP platform's capabilities. By providing realistic demo data, the
module accelerates the learning curve and allows users to experience the
system's full potential firsthand.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OpenSPP/openspp-modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_base_demo%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* OpenSPP.org

Maintainers
-----------

.. |maintainer-jeremi| image:: https://github.com/jeremi.png?size=40px
    :target: https://github.com/jeremi
    :alt: jeremi
.. |maintainer-gonzalesedwin1123| image:: https://github.com/gonzalesedwin1123.png?size=40px
    :target: https://github.com/gonzalesedwin1123
    :alt: gonzalesedwin1123
.. |maintainer-reichie020212| image:: https://github.com/reichie020212.png?size=40px
    :target: https://github.com/reichie020212
    :alt: reichie020212

Current maintainers:

|maintainer-jeremi| |maintainer-gonzalesedwin1123| |maintainer-reichie020212| 

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_base_demo>`_ project on GitHub.

You are welcome to contribute.
