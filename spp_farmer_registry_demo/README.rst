============================
OpenSPP Farmer Registry Demo
============================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:eccedea606c9a761d0cbd0031d2cb447564601925a78c0afd042d1bc7037897e
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_farmer_registry_demo
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP Farmer Registry Demo
============================

Overview
--------

The `spp_farmer_registry_demo <spp_farmer_registry_demo>`__ module is a
demonstration module for OpenSPP that provides pre-populated data for
the farmer registry. It builds upon the
`spp_farmer_registry_base <spp_farmer_registry_base>`__ module and its
dependencies to showcase the functionalities of the farmer registry with
realistic sample data.

Purpose
-------

This module aims to:

-  Populate the farmer registry with sample data, including farmers,
   groups, farm details, agricultural activities, and assets.
-  Provide a starting point for users to explore the farmer registry and
   its various features.
-  Demonstrate how different modules, such as
   `g2p_registry_membership <g2p_registry_membership>`__,
   `queue_job <queue_job>`__, and `spp_base_demo <spp_base_demo>`__,
   integrate to create a comprehensive farmer registry system.

Module Dependencies and Integration
-----------------------------------

-  `spp_farmer_registry_base <spp_farmer_registry_base>`__\ **:** This
   module depends heavily on
   `spp_farmer_registry_base <spp_farmer_registry_base>`__, inheriting
   its models and views to extend them with demo data generation
   capabilities.
-  `g2p_registry_membership <g2p_registry_membership>`__\ **:**
   Leverages `g2p_registry_membership <g2p_registry_membership>`__ for
   creating group memberships between individual farmers and farm
   groups.
-  `queue_job <queue_job>`__\ **:** Uses `queue_job <queue_job>`__ to
   handle the generation of large datasets in the background, improving
   performance and user experience.
-  `g2p_registry_base <g2p_registry_base>`__\ **:** Depends on
   `g2p_registry_base <g2p_registry_base>`__ for the basic registrant
   models and functionalities.
-  `g2p_registry_group <g2p_registry_group>`__\ **:** Uses
   `g2p_registry_group <g2p_registry_group>`__ for creating and managing
   farm groups as registrants.
-  `spp_base_demo <spp_base_demo>`__\ **:** Inherits from
   `spp_base_demo <spp_base_demo>`__ to include basic demo data, such as
   genders.
-  `g2p_registry_individual <g2p_registry_individual>`__\ **:** Utilizes
   `g2p_registry_individual <g2p_registry_individual>`__ for creating
   individual farmer registrants.

Additional Functionality
------------------------

The `spp_farmer_registry_demo <spp_farmer_registry_demo>`__ module
introduces the following key functionalities:

-  **Sample Data Generation:** The module includes a dedicated model,
   ``spp.generate.farmer.data``, and a corresponding form view for
   generating sample farmer data. This form allows users to specify:

   -  The number of farm groups to generate.
   -  The locale for generating realistic data based on specific
      regions.
   -  Once the data generation is triggered, the module creates a queue
      job that populates the database with realistic farmer data,
      including:

      -  Farm Groups: Groups of farmers with detailed information like
         family name, national ID, contact details, and education level.
      -  Individual Farmers: Members of farm groups with personal
         information and links to their respective groups.
      -  Land Records: Land parcels associated with farm groups,
         including coordinates and geographical polygons.
      -  Agricultural Activities: Details of crop, livestock, and
         aquaculture activities undertaken by each farm group, linked to
         specific land parcels.
      -  Farm Details: Comprehensive information about farm types,
         sizes, legal status, infrastructure, technologies, and
         financial services utilized by each farm group.
      -  Farm Assets: Data on farm machinery and other assets owned by
         each farm group, categorized by type and quantity.

-  **Data Realism:** The module utilizes external libraries like
   ``faker`` to generate realistic and region-specific data for names,
   contact details, and other attributes. This ensures that the sample
   data reflects real-world scenarios.

-  **GIS Integration:** The demo data integrates with the GIS
   functionalities of
   `spp_farmer_registry_base <spp_farmer_registry_base>`__ to visualize
   the generated farms and land parcels on a map, providing a visual
   representation of the farmer registry.

Conclusion
----------

The `spp_farmer_registry_demo <spp_farmer_registry_demo>`__ module
provides a valuable tool for understanding and demonstrating the
functionalities of the OpenSPP farmer registry system. By populating the
database with realistic sample data, it allows users to explore the
system, understand its data structures, and test its various features
without having to manually create large datasets. This module simplifies
the process of getting started with OpenSPP and showcases the platform's
capabilities for managing comprehensive and detailed farmer registries.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OpenSPP/openspp-modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_farmer_registry_demo%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_farmer_registry_demo>`_ project on GitHub.

You are welcome to contribute.
