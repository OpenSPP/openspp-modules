# ABOUTME: Module initialization file for OpenSPP Branding Kit
# ABOUTME: Imports models, controllers and defines hooks for the module

from . import models
from . import controllers

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Post-installation hook to perform initial branding setup
    """
    _logger.info("OpenSPP Branding Kit: Running post-installation setup...")

    # Set default configuration parameters
    try:
        IrConfigParam = env["ir.config_parameter"].sudo()

        # Set hide paid apps to True by default (if not already set)
        if not IrConfigParam.get_param("openspp.hide_paid_apps"):
            IrConfigParam.set_param("openspp.hide_paid_apps", "True")
            _logger.info("Set hide paid apps to True by default")

        # Set default app filter to 'apps_only' (if not already set)
        if not IrConfigParam.get_param("openspp.default_app_filter"):
            IrConfigParam.set_param("openspp.default_app_filter", "apps_only")
            _logger.info("Set default app filter to 'apps_only'")

    except Exception as e:
        _logger.warning(f"Error setting default parameters: {e}")

    # Disable Odoo branding elements
    try:
        # Deactivate brand promotion view
        brand_promotion = env.ref("web.brand_promotion_message", raise_if_not_found=False)
        if brand_promotion:
            brand_promotion.active = False
            _logger.info("Disabled Odoo brand promotion message")

        # Disable update notification cron jobs (search by model/method)
        Cron = env["ir.cron"].sudo()

        # Disable module update related cron jobs
        module_update_crons = Cron.search(
            [
                "|",
                "|",
                ("model", "=", "ir.module.module"),
                ("model", "=", "publisher_warranty.contract"),
                ("cron_name", "ilike", "module"),
            ]
        )
        for cron in module_update_crons:
            if cron.active:
                cron.active = False
                _logger.info(f"Disabled cron job: {cron.name}")

        # Disable theme store menu if it exists
        theme_menu = env["ir.ui.menu"].sudo().search([("name", "ilike", "Theme Store")], limit=1)
        if theme_menu and theme_menu.active:
            theme_menu.active = False
            _logger.info("Disabled Theme Store menu")

    except Exception as e:
        _logger.warning(f"Error during branding setup: {e}")

    # Update company information
    try:
        Company = env["res.company"].sudo()
        main_company = Company.browse(1)  # Main company
        if main_company.exists():
            main_company.write(
                {
                    "report_header": "OpenSPP Platform",
                    "report_footer": "OpenSPP - Open Source Social Protection Platform",
                    "website": "https://openspp.org",
                }
            )
            _logger.info("Updated main company branding")
    except Exception as e:
        _logger.warning(f"Error updating company data: {e}")

    _logger.info("OpenSPP Branding Kit: Post-installation setup completed")


def uninstall_hook(env):
    """
    Uninstall hook to clean up configuration parameters
    """
    _logger.info("OpenSPP Branding Kit: Running uninstall cleanup...")

    # Remove the hide_paid_apps parameter
    try:
        IrConfigParam = env["ir.config_parameter"].sudo()
        param = IrConfigParam.search([("key", "=", "openspp.hide_paid_apps")])
        if param:
            param.unlink()
            _logger.info("Removed hide_paid_apps parameter")
    except Exception as e:
        _logger.warning(f"Error removing configuration parameter: {e}")

    # Optionally re-enable Odoo branding elements
    # This is commented out by default to maintain debranding even after uninstall
    # Uncomment if you want to restore Odoo branding on module removal

    # try:
    #     brand_promotion = env.ref('web.brand_promotion_message', raise_if_not_found=False)
    #     if brand_promotion:
    #         brand_promotion.active = True
    # except Exception as e:
    #     _logger.warning(f"Error during uninstall cleanup: {e}")

    _logger.info("OpenSPP Branding Kit: Uninstall cleanup completed")
