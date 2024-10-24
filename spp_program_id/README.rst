==================
OpenSPP Program ID
==================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:90e26ff9c645deb9e5f3b4e57b71225d1d2185d96c18affdc01b9aa9f3e17b89
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Alpha-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alpha
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OpenSPP%2Fopenspp--modules-lightgray.png?logo=github
    :target: https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_program_id
    :alt: OpenSPP/openspp-modules

|badge1| |badge2| |badge3|

OpenSPP Program ID
==================

This document describes the **OpenSPP Program ID** module, an extension
to the OpenSPP platform. This module enhances the existing **OpenG2P:
Programs** functionality by adding unique, system-generated IDs to each
program for improved tracking and reference.

Purpose
-------

The **OpenSPP Program ID** module aims to:

-  **Provide Unique Program Identification**: Generate and assign a
   distinct ID to each program, allowing for easy identification and
   reference.
-  **Enhance Data Management**: Improve the organization and management
   of program data by introducing a standardized identification system.
-  **Facilitate Integration**: Enable seamless integration with other
   systems or modules by providing a consistent program identifier.

Module Dependencies and Integration
-----------------------------------

1. `spp_programs <spp_programs>`__:

   -  Leverages the core program management features provided by the
      OpenSPP Programs module.
   -  Extends program models and views to incorporate the program ID
      field.

2. `g2p_programs <g2p_programs>`__:

   -  Builds upon the program structure and functionality provided by
      the G2P Programs module.
   -  Integrates with program views to display the generated program ID.

Additional Functionality
------------------------

-  **Program ID Generation**:

   -  Automatically generates a unique program ID using a defined
      sequence (``program.id.sequence``) upon program creation.
   -  Ensures that each program has a distinct identifier.

-  **Program ID Field**:

   -  Introduces a new field, ``program_id``, in the ``g2p.program``
      model to store the generated unique ID.
   -  Makes the ``program_id`` field read-only to prevent accidental
      modification.

-  **View Integration**:

   -  Integrates the ``program_id`` field into relevant program views:

      -  **Search Filter**: Adds ``program_id`` as a search filter
         option in the program list view.
      -  **List View**: Displays the ``program_id`` alongside other
         program details in the program list view.
      -  **Form View**: Shows the ``program_id`` prominently within the
         program form view.

Conclusion
----------

The **OpenSPP Program ID** module enhances the OpenSPP platform by
providing a simple yet powerful mechanism for uniquely identifying
programs. This enhancement contributes to better data management, easier
referencing, and smoother integration with other systems, ultimately
improving the efficiency and usability of the OpenSPP platform.

.. IMPORTANT::
   This is an alpha version, the data model and design can change at any time without warning.
   Only for development or testing purpose, do not use in production.
   `More details on development status <https://odoo-community.org/page/development-status>`_

**Table of contents**

.. contents::
   :local:

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OpenSPP/openspp-modules/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OpenSPP/openspp-modules/issues/new?body=module:%20spp_program_id%0Aversion:%2017.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
.. |maintainer-nhatnm0612| image:: https://github.com/nhatnm0612.png?size=40px
    :target: https://github.com/nhatnm0612
    :alt: nhatnm0612

Current maintainers:

|maintainer-jeremi| |maintainer-gonzalesedwin1123| |maintainer-nhatnm0612| 

This module is part of the `OpenSPP/openspp-modules <https://github.com/OpenSPP/openspp-modules/tree/17.0/spp_program_id>`_ project on GitHub.

You are welcome to contribute.
