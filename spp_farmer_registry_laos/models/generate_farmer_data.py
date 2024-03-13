import hashlib
import json
import math
import random

from odoo import api, fields, models

from ..tools import generate_polygon, random_location_in_laos

NAMES = [
    "Aguta",
    "Aprot",
    "Arusei",
    "Ayabei",
    "Barkutwo",
    "Barmasai",
    "Barngetuny",
    "Barsosio",
    "Bethwell",
    "Bitok",
    "Busendich",
    "Changeywo",
    "Cheboi",
    "Cheboiboch",
    "Cheboror",
    "Chege",
    "Chelangat",
    "Chelule",
    "Chemjor",
    "Chemlany",
    "Chemoiywo",
    "Chemosin",
    "Chemutai",
    "Chenonge",
    "Chepchirchir",
    "Chepkemei",
    "Chepkesis",
    "Chepkorir",
    "Chepkosgei",
    "Chepkurui",
    "Cheprot",
    "Cheptais",
    "Chepyego",
    "Cherigat",
    "Cherotich",
    "Cheyech",
    "Cheywa",
    "Chirlee",
    "Dickson",
    "Ebuya",
    "Eyapan",
    "Gitahi",
    "Gwako",
    "Jebet",
    "Jebiwott",
    "Jemaiyo",
    "Jepkesho",
    "Jepkirui",
    "Jerop",
    "Kabiga",
    "Kagika",
    "Kamathi",
    "Kamau",
    "Kamworor",
    "Kandie",
    "Kaptich",
    "Karoki",
    "Kasimili",
    "Kataron",
    "Kibore",
    "Kibowen",
    "Kilel",
    "Kimani",
    "Kimeli",
    "Kimemia",
    "Kimobwa",
    "Kimurgor",
    "Kimwei",
    "Kinuthia",
    "Kinyanjui",
    "Kinyor",
    "Kiogora",
    "Kipkoskei",
    "Kiplitany",
    "Kipsiele",
    "Kipterege",
    "Kirwa",
    "Kisorio",
    "Kithuka",
    "Kitur",
    "Kitwara",
    "Kiyara",
    "Kiyeng",
    "Kogo",
    "Koinange",
    "Komen",
    "Korikwiang",
    "Kororia",
    "Koskei",
    "Kotut",
    "Kurgat",
    "Kuria",
    "Kwalia",
    "Kwambai",
    "Kwemoi",
    "Larabal",
    "Lelei",
    "Lesuuda",
    "Limo",
    "Longosiwa",
    "Loroupe",
    "Loyanae",
    "Magut",
    "Maina",
    "Makau",
    "Malakwen",
    "Masai",
    "Mburu",
    "Moiben",
    "Mugo",
    "Mumbi",
    "Musyoki",
    "Mutahi",
    "Mutai",
    "Mwangangi",
    "Mwangi",
    "Ndungu",
    "Ngugi",
    "Njenga",
    "Njeri",
    "Nyambura",
    "Oduya",
    "Onyango",
    "Sigei",
    "Songok",
    "Tergat",
    "Wacera",
    "Wairimu",
    "Waithaka",
    "Wambui",
    "Wangari",
    "Wanjiku",
    "Wanjiru",
]

PRODUCTS = [
    {
        "id": 1,
        "name_eng": "Vegetable",
        "name_lao": "ຜັກ",
    },
    {
        "id": 2,
        "name_eng": "Rice",
        "name_lao": "ເຂົ້າ",
    },
    {
        "id": 3,
        "name_eng": "Onion",
        "name_lao": "ຜັກບົ່ວ",
    },
    {
        "id": 4,
        "name_eng": "Cabbage",
        "name_lao": "ກະລໍ່າປີ",
    },
    {
        "id": 5,
        "name_eng": "Peanuts",
        "name_lao": "ຖົ່ວດິນ",
    },
    {
        "id": 6,
        "name_eng": "Cucumber",
        "name_lao": "ໝາກແຕງ",
    },
    {
        "id": 7,
        "name_eng": "Garlic",
        "name_lao": "ຜັກທຽມ",
    },
    {
        "id": 9,
        "name_eng": "Cassava",
        "name_lao": "ມັນຕົ້ນ",
    },
    {
        "id": 10,
        "name_eng": "Chili",
        "name_lao": "ໝາກເຜັດ",
    },
    {
        "id": 11,
        "name_eng": "Tea",
        "name_lao": "ຊາ",
    },
    {
        "id": 12,
        "name_eng": "Maize",
        "name_lao": "ສາລີ",
    },
    {
        "id": 13,
        "name_eng": "Sugarcane, banana",
        "name_lao": "ອ້ອຍ, ກ້ວຍ",
    },
    {
        "id": 14,
        "name_eng": "Job'tears",
        "name_lao": "ນໍ້າຕາຂອງໂຢບ",
    },
    {
        "id": 15,
        "name_eng": "Grass planting for forage",
        "name_lao": "ການປູກຫຍ້າລ້ຽງສັດ",
    },
    {
        "id": 16,
        "name_eng": "Sesame",
        "name_lao": "ໝາກງາ",
    },
    {
        "id": 17,
        "name_eng": "Bean",
        "name_lao": "ຖົ່ວ",
    },
    {
        "id": 19,
        "name_eng": "Pig",
        "name_lao": "ຫມູ",
    },
    {
        "id": 20,
        "name_eng": "Chicken",
        "name_lao": "ໄກ່",
    },
    {
        "id": 21,
        "name_eng": "Goat",
        "name_lao": "ແບ້",
    },
    {
        "id": 22,
        "name_eng": "Other 1",
        "name_lao": "ອື່ນໆ 1",
    },
]


class SPPLaosGenerateFarmerData(models.Model):
    _name = "spp.laos.generate.farmer.data"
    _description = "Generate Farm Data For Laos"

    name = fields.Char()
    num_groups = fields.Integer("Number of Groups", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    def generate_sample_data(self):
        batches = math.ceil(self.num_groups / 1000)

        for _ in range(0, batches):
            # self.with_delay()._generate_sample_data(res=self)
            self._generate_sample_data(res=self)

    @api.model
    def _generate_sample_data(self, **kwargs):
        res = kwargs.get("res")

        kind_farm_id = self.env.ref("spp_farmer_registry_base.kind_farm").id
        num_groups = min(res.num_groups, 1000)

        for i in range(0, num_groups):
            group_id = res._generate_group_data(i, kind_farm_id)
            self._generate_event_data_cycle2a(group_id)
            self._generate_event_data_cycle2b(group_id)
            self._generate_event_data_cycle2c(group_id)
            self._generate_event_data_cycle3a(group_id)
            self._generate_event_data_cycle3b(group_id)
            land_record_id = res._generate_land_record_record(group_id)
            group_id.farm_land_rec_id = land_record_id.id
            group_id.coordinates = land_record_id.land_coordinates
            product = random.choice(PRODUCTS)
            res._generate_farm_activity(group_id, product)

            if res.state == "draft":
                res.update({"state": "generate"})

        msg = "Task Queue called task: model [{}] and method [{}].".format(
            self._name,
            "_generate_sample_data",
        )

        return {"result": msg, "res_model": self._name, "res_ids": [res.id]}

    def _generate_group_data(self, index, kind_id):
        group_name = f"{random.choice(NAMES)} Farm"
        id_group = "demo." + hashlib.md5(f"{group_name} {index}".encode()).hexdigest()

        group_vals = {
            "id": id_group,
            "name": group_name,
            "kind": kind_id,
            "is_registrant": True,
            "is_group": True,
        }

        return self.env["res.partner"].create(group_vals)

    def _generate_land_record_record(self, group_id):
        latitude, longitude = random_location_in_laos()

        land_coordinates = {"type": "Point", "coordinates": [longitude, latitude]}

        points = generate_polygon(latitude, longitude, random.randrange(50, 500))

        land_geo_polygon = {"type": "Polygon", "coordinates": [points]}

        return self.env["spp.land.record"].create(
            {
                "land_farm_id": group_id.id,
                "land_name": group_id.name,
                "land_coordinates": json.dumps(land_coordinates),
                "land_geo_polygon": json.dumps(land_geo_polygon),
            }
        )

    def _generate_farm_activity(self, group_id, product):
        product_id = product.get("id")
        product_name_eng = product.get("name_eng")
        product_name = product.get("name_lao")
        target_year = str(random.randint(2000, 2050))

        self.env["spp.farm.activity"].create(
            {
                "prod_farm_id": group_id.id,
                "product_id": product_id,
                "product_name_eng": product_name_eng,
                "product_name": product_name,
                "target_year": target_year,
            }
        )

    def _create_event_data(self, model_name, group_id):
        vals_list = {
            "model": model_name,
            "partner_id": group_id.id,
        }
        event_id = self.env["spp.event.data"].create(vals_list)
        return event_id

    def _generate_event_data_cycle2a(self, group_id):
        event_id = self._create_event_data("spp.event.cycle2a", group_id)
        vals = self._generate_event_data_vals()

        event = self.env["spp.event.cycle2a"].create(vals)
        event_id.res_id = event.id

    def _generate_event_data_cycle3a(self, group_id):
        event_id = self._create_event_data("spp.event.cycle3a", group_id)
        vals = self._generate_event_data_vals()

        event = self.env["spp.event.cycle3a"].create(vals)
        event_id.res_id = event.id

    def _generate_event_data_cycle3b(self, group_id):
        event_id = self._create_event_data("spp.event.cycle3b", group_id)
        vals = self._generate_event_data_vals()

        event = self.env["spp.event.cycle3b"].create(vals)
        event_id.res_id = event.id

    def _generate_event_data_vals(self):
        no_hh_member = random.randint(1, 100)
        no_indigenous = random.randint(1, no_hh_member)
        percent_indigenous = no_indigenous / no_hh_member * 100
        no_15_35 = random.randint(1, no_indigenous)
        percent_15_35 = no_15_35 / no_hh_member * 100
        cycle_vals = {
            "no_woman_headed": 0,
            "no_better_off": 0,
            "no_medium": 0,
            "no_poor": 0,
        }
        total_member = no_hh_member
        for val in cycle_vals:
            if total_member > 0:
                value = random.randint(0, total_member)
                cycle_vals[val] = value
                total_member -= value

        cycle_vals2 = {
            "no_male": 0,
            "no_female": 0,
            "no_both": 0,
        }
        total_member = no_hh_member
        for val in cycle_vals2:
            if total_member > 0:
                value = random.randint(0, total_member)
                cycle_vals2[val] = value
                total_member -= value

        cycle_vals.update(cycle_vals2)

        cycle_vals.update(
            {
                "no_hh_member": no_hh_member,
                "no_indigenous": no_indigenous,
                "percent_indigenous": percent_indigenous,
                "no_15_35": no_15_35,
                "percent_15_35": percent_15_35,
            }
        )
        return cycle_vals

    def _generate_event_data_cycle2b(self, group_id):
        event_id = self._create_event_data("spp.event.cycle2b", group_id)

        cycle2b_vals = {
                "no_implemented": random.randint(0, 100),
                "no_on_going": random.randint(0, 100),
                "no_not_implemented": random.randint(0, 100),
                "production_area": random.randint(0, 100),
                "agricultural_yield": random.randint(0, 100),
                "agricultural_productivity": random.randint(0, 100),
            }
        event = self.env["spp.event.cycle2b"].create(cycle2b_vals)
        event_id.res_id = event.id

    def _generate_event_data_cycle2c(self, group_id):
        event_id = self._create_event_data("spp.event.cycle2c", group_id)

        cycle2c_vals = {
                "no_livestock_project": random.randint(0, 100),
                "no_livestock_present": random.randint(0, 100),
                "no_livestock_consumption": random.randint(0, 100),
                "no_livestock_sold": random.randint(0, 100),
                "no_livestock_increase": random.randint(0, 100),
            }
        event = self.env["spp.event.cycle2c"].create(cycle2c_vals)
        event_id.res_id = event.id
