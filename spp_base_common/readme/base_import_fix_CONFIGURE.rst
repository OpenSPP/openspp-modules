Base Import Fix Configuration
=============================

No additional configuration is required. The module automatically overrides the
base_import functionality once installed.

How to Use
----------

1. **Install the Module**:
   Navigate to Apps > Search "OpenSPP Base (Common)" > Install

2. **Import Data with Batching**:
   - Go to any model's import view (e.g., Contacts > Favorites > Import records)
   - Upload your CSV/Excel file
   - Set the batch size in the import options (default is 2000)
   - Click "Test" to see accurate step calculation
   - The system will now correctly calculate steps including any remainder

3. **Verify Accurate Calculation**:
   - Check the browser console for log messages showing batch calculation
   - Example: ``[SPP Base Import] Batch calculation - Total records: 40100, Batch size: 2000, Total steps: 21``

Import Process
--------------

**Test Import (Dry Run)**:
When you click "Test" with a large dataset:

1. The system calculates total records and batch size
2. Uses ``math.ceil(records / batch_size)`` for accurate step count
3. Shows progress with correct total steps
4. All records including remainder are accounted for

**Actual Import**:
When you click "Import":

1. Same calculation as test import
2. Progress indicator shows accurate completion percentage
3. All batches including remainder are processed
4. No records are left behind

Batch Size Recommendations
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Dataset Size
     - Recommended Batch Size
     - Expected Steps
   * - < 1,000
     - 100-500
     - Disable batching
   * - 1,000 - 10,000
     - 500-1,000
     - 2-20 steps
   * - 10,000 - 100,000
     - 1,000-2,000
     - 10-100 steps
   * - > 100,000
     - 2,000-5,000
     - 20+ steps

Troubleshooting
---------------

**Issue**: Still seeing incorrect step count

**Solution**:
1. Clear browser cache and refresh
2. Ensure module is properly installed
3. Check browser console for error messages
4. Verify JavaScript files are loaded (check Network tab)

**Issue**: Import seems to skip records

**Solution**:
1. Check import results for error messages
2. Verify CSV file format is correct
3. Review logs for batch calculation messages
4. Ensure batch size is appropriate for dataset

Logging
-------

The module provides detailed logging for debugging:

**Backend Logs** (Python):

.. code-block::

    INFO - Batch calculation - Total records: 40100, Batch size: 2000,
           Total steps: 21, Full batches: 20, Remainder: 100

**Frontend Logs** (JavaScript Console):

.. code-block::

    [SPP Base Import] Batch calculation - Total records: 40100,
                      Batch size: 2000, Total steps: 21

