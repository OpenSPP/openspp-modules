# Changelog

## 2025-11-20

### 2025-11-20 16:00:00 - [ADD] comprehensive tests for queue job tracking

- Added `test_queue_job_tracking.py` with 10 comprehensive test cases
- Tests verify `res_id` and `res_model` field functionality
- Tests verify `_compute_job_ids` correctly filters jobs by record
- Tests verify `_compute_has_ongoing_jobs` detects all job states (pending, enqueued, started)
- Tests verify completed jobs (done/failed) don't trigger ongoing flag
- Tests verify model isolation - jobs from different models don't interfere
- Tests cover edge cases including empty results and mixed job states
- Updated `__init__.py` to import new test module
