# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestBaseImportBatch(TransactionCase):
    """
    Test the base_import batch calculation override.

    Ensures that remainder records are properly included in the total steps
    calculation when importing large datasets with batching enabled.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create a base_import.import record for testing
        cls.base_import = cls.env["base_import.import"].create(
            {
                "res_model": "res.partner",
                "file_name": "test_import.csv",
            }
        )

    def test_01_batch_info_calculation_with_remainder(self):
        """Test batch calculation when there is a remainder"""
        # 40100 records with batch size 2000 should give 21 steps
        batch_info = self.base_import._get_batch_info(40100, 2000)

        self.assertEqual(
            batch_info["total_steps"],
            21,
            "40100 records with batch 2000 should create 21 steps (20 full + 1 remainder)",
        )
        self.assertEqual(batch_info["full_batches"], 20, "Should have 20 full batches of 2000")
        self.assertEqual(batch_info["remainder"], 100, "Should have 100 records in remainder")

        _logger.info("Test 01 passed: 40100/2000 = 21 steps ✓")

    def test_02_batch_info_calculation_no_remainder(self):
        """Test batch calculation when there is no remainder"""
        # 40000 records with batch size 2000 should give 20 steps (no extra step)
        batch_info = self.base_import._get_batch_info(40000, 2000)

        self.assertEqual(
            batch_info["total_steps"],
            20,
            "40000 records with batch 2000 should create exactly 20 steps",
        )
        self.assertEqual(batch_info["full_batches"], 20, "Should have 20 full batches of 2000")
        self.assertEqual(batch_info["remainder"], 0, "Should have no remainder")

        _logger.info("Test 02 passed: 40000/2000 = 20 steps ✓")

    def test_03_batch_info_calculation_small_dataset(self):
        """Test batch calculation when dataset is smaller than batch size"""
        # 100 records with batch size 2000 should give 1 step
        batch_info = self.base_import._get_batch_info(100, 2000)

        self.assertEqual(
            batch_info["total_steps"],
            1,
            "100 records with batch 2000 should create 1 step",
        )
        self.assertEqual(batch_info["full_batches"], 0, "Should have 0 full batches")
        self.assertEqual(batch_info["remainder"], 100, "Should have 100 records in remainder")

        _logger.info("Test 03 passed: 100/2000 = 1 step ✓")

    def test_04_batch_info_calculation_edge_cases(self):
        """Test edge cases for batch calculation"""
        # Test with 0 records
        batch_info = self.base_import._get_batch_info(0, 2000)
        self.assertEqual(batch_info["total_steps"], 0, "0 records should create 0 steps")

        # Test with 0 batch size
        batch_info = self.base_import._get_batch_info(1000, 0)
        self.assertEqual(batch_info["total_steps"], 0, "0 batch size should create 0 steps")

        # Test with negative values
        batch_info = self.base_import._get_batch_info(-100, 2000)
        self.assertEqual(batch_info["total_steps"], 0, "Negative records should create 0 steps")

        # Test with 1 record and batch size 1
        batch_info = self.base_import._get_batch_info(1, 1)
        self.assertEqual(batch_info["total_steps"], 1, "1 record with batch 1 should create 1 step")

        _logger.info("Test 04 passed: Edge cases handled correctly ✓")

    def test_05_batch_info_calculation_various_sizes(self):
        """Test batch calculation with various common batch sizes"""
        test_cases = [
            # (total_records, batch_size, expected_steps)
            (10000, 1000, 10),  # Perfect division
            (10001, 1000, 11),  # 1 remainder
            (10999, 1000, 11),  # 999 remainder
            (5000, 2000, 3),  # 1000 remainder
            (50000, 5000, 10),  # Perfect division
            (50001, 5000, 11),  # 1 remainder
            (100, 50, 2),  # Small dataset
            (1, 1000, 1),  # Single record
        ]

        for total_records, batch_size, expected_steps in test_cases:
            with self.subTest(
                total_records=total_records,
                batch_size=batch_size,
                expected_steps=expected_steps,
            ):
                batch_info = self.base_import._get_batch_info(total_records, batch_size)
                self.assertEqual(
                    batch_info["total_steps"],
                    expected_steps,
                    f"{total_records} records with batch {batch_size} should create "
                    f"{expected_steps} steps, got {batch_info['total_steps']}",
                )

        _logger.info("Test 05 passed: Various batch sizes calculated correctly ✓")

    def test_06_batch_info_math_ceil_equivalence(self):
        """
        Verify that our calculation matches math.ceil(total / batch_size).

        This is the correct formula and should handle all cases properly.
        """
        import math

        test_cases = [
            (40100, 2000),
            (40000, 2000),
            (100, 2000),
            (1, 1),
            (10001, 1000),
            (50000, 5000),
        ]

        for total_records, batch_size in test_cases:
            with self.subTest(total_records=total_records, batch_size=batch_size):
                batch_info = self.base_import._get_batch_info(total_records, batch_size)
                expected = math.ceil(total_records / batch_size)
                self.assertEqual(
                    batch_info["total_steps"],
                    expected,
                    f"Batch calculation should match math.ceil({total_records}/{batch_size}) = {expected}",
                )

        _logger.info("Test 06 passed: Calculations match math.ceil ✓")
