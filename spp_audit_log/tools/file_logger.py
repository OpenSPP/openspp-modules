import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

_logger = logging.getLogger(__name__)


class AuditFileLogger:
    """
    File-based audit logger using RotatingFileHandler.
    Writes audit logs in JSON Lines format to prevent database bloat.
    """

    _instance = None
    _handler = None
    _logger = None
    _current_config = {}

    def __new__(cls):
        """Singleton pattern to ensure only one logger instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_config_value(self, env, key, default):
        """
        Retrieve configuration value from ir.config_parameter.

        :param env: Odoo environment
        :param key: Configuration parameter key
        :param default: Default value if parameter not found
        :return: Configuration value
        """
        try:
            param = env["ir.config_parameter"].sudo().get_param(key, default)
            return param
        except Exception as e:
            _logger.warning(
                "Failed to retrieve config parameter %s: %s. Using default: %s",
                key,
                e,
                default,
            )
            return default

    def _is_file_logging_enabled(self, env):
        """
        Check if file logging is enabled in configuration.

        :param env: Odoo environment
        :return: Boolean indicating if file logging is enabled
        """
        enabled = self._get_config_value(env, "spp.audit_log_to_file", "False")
        return enabled.lower() in ("true", "1", "yes")

    def _get_file_path(self, env):
        """
        Get the configured file path for audit logs.

        :param env: Odoo environment
        :return: File path string
        """
        return self._get_config_value(env, "spp.audit_log_file_path", "/var/log/odoo/audit.log")

    def _get_max_bytes(self, env):
        """
        Get the maximum file size in bytes before rotation.

        :param env: Odoo environment
        :return: Maximum file size in bytes
        """
        max_mb = int(self._get_config_value(env, "spp.audit_log_file_max_bytes", "10"))
        return max_mb * 1024 * 1024  # Convert MB to bytes

    def _get_backup_count(self, env):
        """
        Get the number of backup files to keep.

        :param env: Odoo environment
        :return: Backup count integer
        """
        return int(self._get_config_value(env, "spp.audit_log_file_backup_count", "5"))

    def _setup_handler(self, env):
        """
        Setup or update the RotatingFileHandler based on current configuration.

        :param env: Odoo environment
        """
        file_path = self._get_file_path(env)
        max_bytes = self._get_max_bytes(env)
        backup_count = self._get_backup_count(env)

        # Check if configuration has changed
        new_config = {
            "file_path": file_path,
            "max_bytes": max_bytes,
            "backup_count": backup_count,
        }

        if self._current_config == new_config and self._handler is not None:
            return  # Configuration unchanged, reuse existing handler

        # Close existing handler if any
        if self._handler:
            self._handler.close()
            if self._logger:
                self._logger.removeHandler(self._handler)

        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            # Create rotating file handler
            self._handler = RotatingFileHandler(
                file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )

            # Setup logger
            if self._logger is None:
                self._logger = logging.getLogger("spp.audit.file")
                self._logger.setLevel(logging.INFO)
                self._logger.propagate = False

            self._logger.addHandler(self._handler)
            self._current_config = new_config

            _logger.info(
                "Audit file logger initialized: path=%s, max_size=%dMB, backups=%d",
                file_path,
                max_bytes // (1024 * 1024),
                backup_count,
            )

        except (OSError, PermissionError) as e:
            _logger.error(
                "Failed to setup audit file logger at %s: %s. " "File logging will be disabled.",
                file_path,
                e,
            )
            self._handler = None
            self._current_config = {}

    def log_to_file(self, env, audit_rule, method, res_id, data):
        """
        Write audit log entry to JSON file.

        :param env: Odoo environment
        :param audit_rule: The audit rule record
        :param method: Operation method (create, write, unlink)
        :param res_id: Resource ID
        :param data: Dictionary containing old and new values
        """
        if not self._is_file_logging_enabled(env):
            return False

        self._setup_handler(env)

        if not self._handler:
            return False

        try:
            # Prepare log entry in JSON format
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_id": env.uid,
                "user_login": env.user.login if env.user else None,
                "model": audit_rule.model_id.model,
                "model_name": audit_rule.model_id.name,
                "res_id": res_id,
                "method": method,
                "audit_rule": audit_rule.name,
                "changes": data,
            }

            # Write as JSON Lines format (one JSON object per line)
            json_line = json.dumps(log_entry, ensure_ascii=False)
            self._logger.info(json_line)

            return True

        except Exception as e:
            _logger.error("Failed to write audit log to file: %s", e)
            return False


# Module-level singleton instance
_audit_file_logger = AuditFileLogger()


def log_audit_to_file(env, audit_rule, method, res_id, data):
    """
    Convenience function to log audit entries to file.

    :param env: Odoo environment
    :param audit_rule: The audit rule record
    :param method: Operation method (create, write, unlink)
    :param res_id: Resource ID
    :param data: Dictionary containing old and new values
    :return: Boolean indicating success
    """
    return _audit_file_logger.log_to_file(env, audit_rule, method, res_id, data)


def is_file_logging_enabled(env):
    """
    Check if file logging is enabled.

    :param env: Odoo environment
    :return: Boolean indicating if file logging is enabled
    """
    return _audit_file_logger._is_file_logging_enabled(env)
