from . import models

# Expose post_init_hook at module level (supports both signatures)
from .models import providers as _providers  # noqa: F401


def post_init_hook(env_or_cr, registry=None):
    """Bridge Odoo's env-based hook to our cr-based provider registrar.

    - If called with an Environment (env), pass env.cr to the providers hook
    - If called with (cr, registry), forward as-is
    """
    # If it's an Environment instance, use its cursor
    if hasattr(env_or_cr, "cr") and getattr(env_or_cr, "__class__", None).__name__ == "Environment":
        return _providers.post_init_hook(env_or_cr.cr, registry)
    # Otherwise assume it's a cursor
    return _providers.post_init_hook(env_or_cr, registry)
