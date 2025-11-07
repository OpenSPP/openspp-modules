Changelog
=========

17.0.1.3.1
----------

**Features**:
- Added base_import override to fix batch remainder calculation issue
- Implemented proper ``Math.ceil()`` calculation for accurate step counting
- Added comprehensive batch info calculation method
- Included both modern and legacy JavaScript implementations

**Backend Changes**:
- New model: ``models/base_import.py`` - Overrides ``base_import.import``
- New method: ``_get_batch_info()`` - Calculates batch steps including remainder
- Enhanced: ``execute_import()`` - Injects accurate batch information

**Frontend Changes**:
- New file: ``static/src/js/import_action.esm.js`` - Modern JS override
- New file: ``static/src/legacy/js/import_action.js`` - Legacy JS override
- Fixed: ``totalSteps`` calculation using ``Math.ceil()`` instead of ``Math.floor() + 1``

**Testing**:
- New test file: ``tests/test_base_import_batch.py``
- Added 6 comprehensive test cases covering various scenarios
- Tests verify mathematical correctness of batch calculations

**Documentation**:
- Added ``readme/DESCRIPTION.rst`` - Feature description and technical details
- Added ``readme/CONFIGURE.rst`` - Configuration and usage guide
- Added ``readme/CHANGELOG.rst`` - This changelog

**Dependencies**:
- Added explicit dependency on ``base_import`` module

**Bug Fixes**:
- Fixed incorrect step calculation that could leave remainder records unprocessed
- Fixed progress indicator showing wrong total steps
- Ensured test imports account for all records including remainder

Impact
------

**Before**:
- 40,100 records with 2,000 batch size might show incorrect step count
- Remainder 100 records might require manual re-triggering
- Progress indicator could be inaccurate

**After**:
- 40,100 records with 2,000 batch size correctly shows 21 steps
- All records including remainder 100 are included in first test
- Progress indicator accurately reflects actual import progress

Migration Notes
---------------

This is a transparent fix that requires no data migration or user action.
Simply update the module and the fix is automatically applied.

Known Issues
------------

None at this time.

Future Enhancements
-------------------

- Add configuration option for custom batch size defaults per model
- Implement batch size auto-calculation based on record complexity
- Add visual indicator showing batch breakdown in UI

