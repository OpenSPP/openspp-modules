=================================
OpenSPP Farmer Registry Dashboard
=================================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:8d4f87d4deb5727a76db1919065d06de22eb367c39c1b6aa0f5dac025feafdb8
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_farmer_registry_dashboard
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP Farmer Registry Dashboard
=================================

Overview
--------

The ``spp_farmer_registry_dashboard`` module provides a suite of
interactive dashboards and reports to visualize data from the OpenSPP
Farmer Registry. It leverages the power of data visualization to offer
insights into key metrics and trends related to registered farmers and
their agricultural practices.

Purpose
-------

This module aims to:

-  **Enhance Data Exploration**: Provide users with intuitive dashboards
   to easily explore and analyze farmer registry data.
-  **Visualize Key Metrics**: Present aggregated statistics and trends
   in a visually appealing and understandable format.
-  **Support Decision-Making**: Equip stakeholders with the insights
   needed to make informed decisions regarding agricultural programs and
   interventions.

Module Dependencies and Integration
-----------------------------------

-  `spp_farmer_registry_base <spp_farmer_registry_base>`__ : The
   dashboard module heavily relies on the data models and
   functionalities provided by
   `spp_farmer_registry_base <spp_farmer_registry_base>`__. It fetches
   data about farmers, farm groups, land records, agricultural
   activities, and other relevant information from this core module.
-  `g2p_registry_membership <g2p_registry_membership>`__ : Utilizes this
   module to display data related to group memberships, such as the
   number of farmers belonging to different types of farmer groups.
-  `spp_farmer_registry_demo <spp_farmer_registry_demo>`__ : While not a
   strict dependency, the dashboard module is particularly useful when
   used in conjunction with
   `spp_farmer_registry_demo <spp_farmer_registry_demo>`__. The demo
   data provides a rich dataset for the dashboards to visualize,
   showcasing the module's capabilities.
-  **spreadsheet_dashboard**: Leverages the ``spreadsheet_dashboard``
   module to create dynamic and interactive dashboards. This dependency
   provides the framework for embedding charts and graphs directly
   within the Odoo interface.
-  `g2p_registry_base <g2p_registry_base>`__ : Indirectly depends on
   this module through its reliance on
   `spp_farmer_registry_base <spp_farmer_registry_base>`__. The core
   registrant data structures and relationships defined in
   `g2p_registry_base <g2p_registry_base>`__ are essential for the
   dashboard's functionality.
-  `g2p_registry_group <g2p_registry_group>`__ : Utilized indirectly to
   access and display information about different types of farmer
   groups, which are defined and managed by this module.
-  `g2p_registry_individual <g2p_registry_individual>`__ : Also
   indirectly relied upon to access and visualize data related to
   individual farmers, such as their demographic information and
   registration details.

Additional Functionality
------------------------

The ``spp_farmer_registry_dashboard`` module introduces the following
key features:

-  **Interactive Dashboards**: The module provides several pre-built
   dashboards, accessible through the Odoo menu:

   -  **Farmer Registry by Month**: Visualizes the number of farmers
      registered each month, allowing users to track registration trends
      over time.
   -  **Farmer Registry by Legal Status**: Displays the distribution of
      farmers based on the legal status of their farms (e.g., owned,
      leased, communal).
   -  **Farmer with/without Training Statistics**: Presents a
      comparative view of farmers who have received formal agricultural
      training versus those who have not.
   -  **Sustainable Land & Environmental Management Statistics**:
      Visualizes data related to sustainable farming practices,
      providing insights into the adoption of environmentally friendly
      methods.

-  **Customizable Reports**: The module includes customizable report
   templates that can be generated in various formats (e.g., PDF, XLSX).
   These reports offer more detailed breakdowns of farmer data and can
   be tailored to specific reporting requirements.
-  **Data Filtering and Aggregation**: The dashboards and reports offer
   filtering options, allowing users to focus on specific subsets of
   data. For instance, users can filter data by region, farm type, crop
   type, or other relevant criteria.

Conclusion
----------

The ``spp_farmer_registry_dashboard`` module transforms raw data from
the OpenSPP Farmer Registry into actionable insights. By providing
intuitive dashboards and customizable reports, it empowers stakeholders
to analyze trends, identify patterns, and make informed decisions to
enhance the effectiveness of agricultural programs and interventions.

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OpenSPP/openspp-modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_farmer_registry_dashboard%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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

Current maintainers:

|maintainer-jeremi| |maintainer-gonzalesedwin1123| 

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_farmer_registry_dashboard>`_ project on GitHub.

You are welcome to contribute.
