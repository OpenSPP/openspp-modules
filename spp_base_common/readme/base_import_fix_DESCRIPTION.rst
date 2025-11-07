Base Import Batch Remainder Fix
================================

This module extends Odoo's base_import functionality to properly handle remainder
records in batch imports.

Problem Statement
-----------------

When importing large datasets with batching enabled, the standard Odoo base_import
module sometimes miscalculates the total number of steps, particularly when there
are remainder records that don't fill a complete batch.

For example:
- Importing 40,100 records with a batch size of 2,000
- Standard calculation: ``Math.floor(40100/2000) + 1 = 20 + 1 = 21`` (sometimes adds extra step)
- This could miss the remainder 100 records on the initial test import

Solution
--------

This module overrides the batch calculation logic in both the backend (Python) and
frontend (JavaScript) to use proper ceiling division:

- Backend: Uses ``math.ceil(total_records / batch_size)`` for accurate step calculation
- Frontend: Uses ``Math.ceil()`` instead of ``Math.floor() + 1`` to prevent extra steps

Benefits
--------

1. **Accurate Step Calculation**: Ensures the exact number of steps needed including remainders
2. **Complete Test Imports**: Test imports now properly account for all records including remainders
3. **Better User Experience**: Users see accurate progress during import operations
4. **Prevents Data Loss**: Ensures no records are left out of the import process

Examples
--------

.. code-block::

    Records: 40,100 | Batch: 2,000 | Steps: 21 (20 × 2,000 + 1 × 100)
    Records: 40,000 | Batch: 2,000 | Steps: 20 (20 × 2,000 + 0 remainder)
    Records:    100 | Batch: 2,000 | Steps:  1 (0 × 2,000 + 1 × 100)

Technical Details
-----------------

**Python Override** (``models/base_import.py``):
- Adds ``_get_batch_info()`` method for accurate calculation
- Overrides ``execute_import()`` to inject batch info
- Provides detailed logging for debugging

**JavaScript Override** (``static/src/js/import_action.esm.js``):
- Patches the ``ImportAction`` component's ``totalSteps`` getter
- Uses ``Math.ceil()`` for proper remainder handling

**Legacy Support** (``static/src/legacy/js/import_action.js``):
- Overrides legacy ``call_import`` method
- Ensures backward compatibility with older Odoo versions

Testing
-------

Comprehensive test suite in ``tests/test_base_import_batch.py`` covers:
- Batch calculation with remainder records
- Batch calculation without remainder records
- Small datasets (smaller than batch size)
- Edge cases (zero records, zero batch size, negative values)
- Various batch sizes to ensure consistency
- Mathematical correctness (equivalence to ``math.ceil``)

