from .common import Common


class TestRegistrant(Common):
    def test_01_compute_inkind_entitlements_count(self):
        self.registrant._compute_inkind_entitlements_count()
        self.assertEqual(
            self.registrant.inkind_entitlements_count,
            1,
            "Registrant should have correct inkind entitlements count!",
        )
