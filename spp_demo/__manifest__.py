#
# Copyright (c) 2022 Newlogic.
#
# This file is part of newlogic-g2p-erp.
# See https://github.com/newlogic/newlogic-g2p-erp/ for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
{
    "name": "OpenSPP Demo",
    "category": "OpenSPP",
    "version": "15.0.0.0.1",
    "sequence": 1,
    "author": "Newlogic",
    "website": "https://newlogic.com/",
    "license": "OPL-1",
    "depends": [
        "spp_base_demo",
        "g2p_registry_base",
        "g2p_programs",
        "spp_custom_field",
        "spp_dashboard",
        "spp_idpass",
        "spp_helpdesk",
        "spp_area",
        "theme_openspp",
        "spp_photo",
        "spp_pos",
        "spp_sms",
        "celery",
    ],
    "external_dependencies": {"python": ["faker"]},
    "data": [
        "security/ir.model.access.csv",
        "views/generate_data_view.xml",
        "views/generate_program_view.xml",
    ],
    "assets": {},
    "demo": [],
    "images": [],
    "application": True,
    "installable": True,
    "auto_install": False,
}
