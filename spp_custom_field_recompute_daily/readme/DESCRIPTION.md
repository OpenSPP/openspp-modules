# OpenSPP Custom Field Recompute Daily

The 'OpenSPP Custom Field Recompute Daily' module automates the daily recalculation of specific computed fields within OpenSPP. This ensures that critical data, which depends on other system values, remains accurate and current without manual intervention, while also improving overall system performance by distributing computational load.

## Purpose

This module addresses the need for consistent and timely data accuracy for computed fields, especially those that aggregate or derive information from other records. It provides a robust mechanism to maintain the integrity of dynamic data.

*   **Automates Data Refresh**: Automatically recomputes designated fields on a daily basis, guaranteeing that derived data reflects the latest information across the system.
*   **Ensures Data Accuracy**: Maintains the precision of complex computed fields, such as program eligibility statuses or financial aggregates, which are crucial for reporting and decision-making.
*   **Optimizes System Performance**: Offloads intensive calculations to off-peak hours or background processes, preventing performance degradation during active user periods.
*   **Scales for Large Datasets**: Efficiently handles recomputation for large volumes of records by processing them in configurable batches, leveraging asynchronous job queues.
*   **Simplifies Data Management**: Eliminates the need for manual data refresh routines or complex custom scripts, streamlining system maintenance and data governance.

## Dependencies and Integration

The `spp_custom_field_recompute_daily` module integrates seamlessly with core OpenSPP components to deliver its functionality.

It relies on the [Base Setup](base_setup) module for foundational system configurations and parameters. Crucially, it leverages the [Queue Job](queue_job) module to process large recomputation tasks asynchronously, preventing system slowdowns and ensuring efficient resource utilization. This allows the system to remain responsive even when recomputing data for thousands of records.

This module serves as a foundational data maintenance service for any other OpenSPP module that utilizes computed and stored fields requiring periodic updates. By ensuring the accuracy of these fields, it indirectly supports reliable reporting, analytics, and operational processes across the entire platform.

## Additional Functionality

The module offers key capabilities to manage and optimize the daily recomputation of custom fields.

### Configurable Daily Recomputation
Users can designate any computed and stored field for daily recomputation directly from the field's definition. This ensures that fields like aggregated totals or derived statuses are automatically refreshed every 24 hours. The module specifically validates that only fields which are both *computed* and *stored* can be marked for daily recomputation, preventing erroneous configurations for non-storing or non-calculating fields.

### Optimized Batch Processing
For models with a large number of records, the module intelligently splits the recomputation task into smaller, manageable batches. This process is configurable via the 'Maximum Daily Recompute Records Count' setting, which defaults to 10,000 records. Tasks exceeding this limit are automatically added to the job queue for background processing, ensuring that recomputation does not overwhelm system resources during peak hours.

### Automated Cron Job Management
The module automatically sets up and manages a system-level cron job responsible for triggering the daily recomputation process. This cron job is scheduled to run at 1 AM local time, ensuring that recomputation occurs during off-peak hours. This automated setup removes the need for manual configuration of recurring tasks, simplifying deployment and maintenance.

## Conclusion

The `spp_custom_field_recompute_daily` module is essential for maintaining accurate, up-to-date computed data across OpenSPP, ensuring system performance and data reliability for all social protection programs.