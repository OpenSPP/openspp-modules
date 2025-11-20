# Changelog

## 2025-11-20

### 2025-11-20 15:45:00 - [IMP] enhance queue job tracking and prevent concurrent operations

- Added `has_ongoing_jobs` computed field to detect concurrent job operations
- Added `ongoing_job_generator_id` computed field to identify which generator has ongoing jobs
- Combined compute logic into single efficient method `_compute_ongoing_jobs_info()`
- Enhanced Queue Jobs page with state decorations, detailed form view, and exception information
- Added info alert banner to notify users when another generator is running
- Hidden Generate button when any generator has ongoing jobs to prevent race conditions

### 2025-11-20 14:30:00 - [ADD] track queue jobs in demo data generator

- Added `queue_job_ids` computed field to link queue jobs to demo data generator records
- Added `queue_job_count` field to display number of associated jobs
- Added "Queue Jobs" page in form view to display job status and details
- Leverages `res_id` and `res_model` fields from queue_job model for automatic tracking
