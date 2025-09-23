def get_param(env, key, default=None):
    return env["ir.config_parameter"].sudo().get_param(key, default)


def get_branding_config(env):
    return {
        "openspp_system_name": get_param(env, "openspp.system.name", "OpenSPP Platform"),
        "openspp_documentation_url": get_param(env, "openspp.documentation.url", "https://docs.openspp.org"),
        "openspp_support_url": get_param(env, "openspp.support.url", "https://openspp.org"),
        "openspp_show_powered_by": get_param(env, "openspp.show.powered_by", "True") == "True",
        "openspp_telemetry_enabled": get_param(env, "openspp.telemetry.enabled", "True") == "True",
        "openspp_telemetry_endpoint": get_param(env, "openspp.telemetry.endpoint", "https://telemetry.openspp.org"),
    }


def version_info_payload(env):
    system_name = get_param(env, "openspp.system.name", "OpenSPP Platform")
    return {"server_version": system_name, "server_serie": "17.0", "protocol_version": 1}


def telemetry_payload(env):
    enabled = get_param(env, "openspp.telemetry.enabled", "True") == "True"
    if not enabled:
        return {"status": "disabled", "message": "Telemetry disabled"}
    endpoint = get_param(env, "openspp.telemetry.endpoint", "https://telemetry.openspp.org")
    return {"status": "redirected", "endpoint": endpoint, "message": "Telemetry redirected to OpenSPP"}
