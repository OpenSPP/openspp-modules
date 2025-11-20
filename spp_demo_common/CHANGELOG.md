# Changelog

## 2025-11-20

### 2025-11-20 14:30:00 - [ADD] track queue jobs in demo data generator

- Added `queue_job_ids` computed field to link queue jobs to demo data generator records
- Added `queue_job_count` field to display number of associated jobs
- Added "Queue Jobs" page in form view to display job status and details
- Leverages `res_id` and `res_model` fields from queue_job model for automatic tracking
