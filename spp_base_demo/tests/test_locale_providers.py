from odoo.tests.common import TransactionCase

from ..locale_providers import get_faker_provider
from ..locale_providers.en_KE import Provider as EnKeProvider
from ..locale_providers.lo_LA import Provider as LoLaProvider
from ..locale_providers.si_LK import Provider as SiLkProvider
from ..locale_providers.sw_KE import Provider as SwKeProvider
from ..locale_providers.ta_LK import Provider as TaLkProvider


class TestLocaleProviders(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_faker_provider(self):
        self.assertEqual(get_faker_provider("en_KE"), EnKeProvider)
        self.assertEqual(get_faker_provider("lo_LA"), LoLaProvider)
        self.assertEqual(get_faker_provider("si_LK"), SiLkProvider)
        self.assertEqual(get_faker_provider("sw_KE"), SwKeProvider)
        self.assertEqual(get_faker_provider("ta_LK"), TaLkProvider)
        self.assertEqual(get_faker_provider("en_US"), None)
