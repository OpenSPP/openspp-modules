import logging

# from copy import deepcopy
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import safe_eval

from ..tools import datetime_format

# Field type mapping for Swagger
SWAGGER_FIELD_MAPPING = {
    "binary": ("string", "binary"),
    "boolean": ("boolean", ""),
    "char": ("string", ""),
    "date": ("string", "date"),
    "datetime": ("string", "date-time"),
    "float": ("number", "float"),
    "html": ("string", ""),
    "integer": ("integer", ""),
    "many2many": ("array", ""),
    "many2one": ("integer", ""),
    "many2one_reference": ("integer", ""),
    "monetary": ("number", "float"),
    "one2many": ("array", ""),
    "reference": ("string", ""),
    "selection": ("array", ""),
    "text": ("string", ""),
}

MAX_LIMIT = 500

_logger = logging.getLogger(__name__)


def convert_field_type_to_swagger(field_type):
    """
    Convert the field type to its corresponding Swagger type and format.

    Args:
        field_type (str): The field type to convert.

    Returns:
        tuple: The corresponding Swagger type and format.
    """
    swagger_type, swagger_format = "string", ""
    if field_type in SWAGGER_FIELD_MAPPING:
        swagger_type, swagger_format = SWAGGER_FIELD_MAPPING.get(field_type)
    return swagger_type, swagger_format


def format_definition_name(name):
    """
    Format the definition name by removing spaces.

    Args:
        name (str): The name to format.

    Returns:
        str: The formatted name without spaces.
    """
    return name.replace(" ", "") if name else ""


class SPPAPIPath(models.Model):
    _name = "spp_api.path"
    _order = "model_id"
    _rec_name = "model_id"
    _description = "OpenAPI Path"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    namespace_id = fields.Many2one("spp_api.namespace", string="API Namespace", required=True, ondelete="cascade")
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model = fields.Char(related="model_id.model", readonly=True, string="Model Name")
    method = fields.Selection(
        [
            ("get", "Read"),
            ("post", "Create"),
            ("put", "Update"),
            ("delete", "Delete"),
            ("patch", "Custom function"),
        ],
        required=True,
    )
    description = fields.Html()
    deprecated = fields.Boolean()
    # Read
    filter_domain = fields.Char(default="[]")
    field_ids = fields.Many2many("ir.model.fields", domain="[('model_id', '=', model_id)]", string="Fields")
    limit = fields.Integer(string="Limit of results", default=500)
    # Create / Update
    warning_required = fields.Boolean(compute="_compute_warning_required", compute_sudo=True)
    api_field_ids = fields.One2many("spp_api.field", "path_id", string="API Fields", copy=True)
    update_domain = fields.Char(default="[]")
    # Unlink
    unlink_domain = fields.Char(default="[]")
    # Custom function
    function_apply_on_record = fields.Boolean()
    function_domain = fields.Char(default="[]")
    function = fields.Char()
    function_parameter_ids = fields.One2many("spp_api.function.parameter", "path_id", string="Parameters", copy=True)

    _sql_constraints = [
        (
            "name_uniq",
            "unique (name, namespace_id, method)",
            "Name, Version, Method must be unique!",
        ),
    ]

    @api.constrains(
        "method",
        "field_ids",
    )
    def _check_field_get_method(self):
        for rec in self:
            if rec.method == "get" and not rec.field_ids:
                raise ValidationError(_("API need a specific fields list!"))

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_ids = False
        self.api_field_ids = False

    def _compute_warning_required(self):
        warning_required = False
        if self.api_field_ids:
            model_required_fields = self.model_id.field_id.filtered(lambda f: f.required).mapped("name")
            api_required_fields = self.api_field_ids.filtered(lambda f: f.required).mapped("field_id.name")
            warning_required = not all(elem in api_required_fields for elem in model_required_fields)
        self.warning_required = warning_required

    def _update_values(self, values):
        if values.get("name"):
            values["name"] = values.get("name", "").replace(" ", "")

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update(name=_("%s (copy)") % (self.name or ""))
        return super().copy(default)

    @api.model
    def create(self, values):
        self._update_values(values)
        return super().create(values)

    def write(self, values):
        self._update_values(values)
        return super().write(values)

    def get_oas_part(self):
        self = self.sudo()
        return {
            "definitions": self.get_oas_definitions_part(),
            "paths": self.get_oas_paths_part(),
            "tag": {
                "name": "%s" % self.model,
                "description": "Model %s" % self.model,
            },
        }

    def get_oas_paths_part(self):
        self.ensure_one()
        swagger_paths = {}
        # Default values
        values = {
            "description": self.description or "",
            "deprecated": self.deprecated,
            "produces": ["application/json"],
            "responses": {
                "200": {
                    "description": "OK",
                },
                "401": {
                    "description": "Unauthorized",
                    "schema": {"$ref": "#/definitions/ApiErrorResponse"},
                },
                "403": {
                    "description": "Forbidden",
                    "schema": {"$ref": "#/definitions/ApiErrorResponse"},
                },
                "404": {
                    "description": "Not found",
                    "schema": {"$ref": "#/definitions/ApiErrorResponse"},
                },
                "500": {
                    "description": "Internal server error",
                    "schema": {"$ref": "#/definitions/ApiErrorResponse"},
                },
            },
            "security": [
                {
                    "basicAuth": [],
                }
            ],
        }
        # Get
        if self.method == "get":
            # Default dict path
            get_path = f"/{self.name}"
            if get_path not in swagger_paths:
                swagger_paths.setdefault(get_path, {})
            get_one_path = "/{}/{}".format(self.name, "{Id}")
            if get_one_path not in swagger_paths:
                swagger_paths.setdefault(get_one_path, {})
            # region::Read All elements::
            definition_all = {
                "schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "$ref": f"#/definitions/{format_definition_name(self.name)}",
                            },
                        },
                        "reply_id": {
                            "type": "string",
                        },
                        "count": {
                            "type": "integer",
                        },
                        "offset": {
                            "type": "integer",
                        },
                        "limit": {
                            "type": "integer",
                        },
                        "timestamp": {
                            "type": "string",
                        },
                    },
                }
            }
            values["responses"]["200"].update(definition_all)
            values.update(parameters=self._get_parameters_all_elements())
            swagger_paths[get_path].update(
                {
                    "get": values,
                }
            )
            # endregion
            # region::Read One element::
            # values_one = deepcopy(values)
            # definition_one = {
            #     "schema": {
            #         "type": "object",
            #         "properties": {
            #             "result": {
            #                 "$ref": "#/definitions/{}".format(
            #                     format_definition_name(self.name)
            #                 ),
            #             },
            #             "reply_id": {
            #                 "type": "string",
            #             },
            #             "timestamp": {
            #                 "type": "string",
            #             },
            #         },
            #     }
            # }
            # values_one["responses"]["200"].update(definition_one)
            # values_one.update(parameters=self._get_parameters_one_element())
            # swagger_paths[get_one_path].update(
            #     {
            #         "get": values_one,
            #     }
            # )
        # endregion
        # Post
        elif self.method == "post" and self.api_field_ids:
            # Default dict path
            post_path = f"/{self.name}"
            if post_path not in swagger_paths:
                swagger_paths.setdefault(post_path, {})
            # Create element
            definition = {
                "description": _("Identifier of the resource created."),
                "schema": {
                    "type": "object",
                    "properties": {
                        "reply_id": {
                            "type": "string",
                        },
                        "timestamp": {
                            "type": "string",
                        },
                    },
                },
            }
            values["responses"]["200"].update(definition)
            values.update(
                consumes=self._form_urlencoded_consumes(),
                parameters=self._post_parameters(),
            )
            swagger_paths[post_path].update(
                {
                    "post": values,
                }
            )
        # Put
        elif self.method == "put" and self.api_field_ids:
            # Default dict path
            put_path = "/{}/{}".format(self.name, "{Id}")
            if put_path not in swagger_paths:
                swagger_paths.setdefault(put_path, {})
            # Update element
            definition = {
                "description": _("Return a boolean if update is a success."),
                "schema": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "boolean",
                        },
                        "reply_id": {
                            "type": "string",
                        },
                    },
                },
            }
            values["responses"]["200"].update(definition)
            values.update(
                consumes=self._form_urlencoded_consumes(),
                parameters=self._put_parameters(),
            )
            swagger_paths[put_path].update(
                {
                    "put": values,
                }
            )
        # Delete
        elif self.method == "delete":
            # Default dict path
            delete_path = "/{}/{}".format(self.name, "{Id}")
            if delete_path not in swagger_paths:
                swagger_paths.setdefault(delete_path, {})
            # Delete element
            definition = {
                "description": _("Return a boolean if delete is a success."),
                "schema": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "boolean",
                        },
                        "reply_id": {
                            "type": "string",
                        },
                    },
                },
            }
            values["responses"]["200"].update(definition)
            values.update(parameters=self._delete_parameters())
            swagger_paths[delete_path].update(
                {
                    "delete": values,
                }
            )
        # Put Custom function
        elif self.method == "custom":
            # Delete element
            values.update(
                consumes=self._form_urlencoded_consumes(),
                parameters=self._custom_parameters(),
            )
            route = "/{}/{}".format(self.name, "custom")
            if self.function_apply_on_record:
                route = "/{}/{}/{}".format(self.name, "custom", "{Id}")
            swagger_paths[route] = {
                "put": values,
            }
        return swagger_paths

    def get_oas_definitions_part(self):
        """
        Generates the definition for the specified model and method, and adds
        it to the swagger_definitions dictionary.

        :param swagger_definitions: A dictionary containing the swagger
                                    definitions for the current API.
        :type swagger_definitions: dict
        :return: True if the definition was generated successfully.
        :rtype: bool
        """
        self.ensure_one()
        swagger_definitions = {}
        definition_name = format_definition_name(self.name)
        if self.method == "get":
            swagger_definitions[definition_name] = {
                "type": "object",
                "properties": self.get_definition_properties(),
            }
        # Add ApiErrorResponse
        swagger_definitions["ApiErrorResponse"] = {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "description": _("Error code")},
                "error": {"type": "string", "description": _("Name of error")},
                "description": {
                    "type": "string",
                    "description": _("Description of the error"),
                },
            },
        }
        return swagger_definitions

    def _request_id_parameter(self):
        return {
            "name": "request_id",
            "in": "query",
            "description": "the unique ID created by the caller",
            "required": True,
            "type": "string",
        }

    def _from_date_parameter(self):
        return {
            "name": "from_date",
            "in": "query",
            "description": "UTC datetime for create time",
            "type": "string",
            "format": "date-time",
        }

    def _last_modified_date_parameter(self):
        return {
            "name": "last_modified_date",
            "in": "query",
            "description": "UTC datetime for update time",
            "type": "string",
            "format": "date-time",
        }

    # Fields
    def _id_parameter(self):
        """
        Generates a dictionary containing the information of the 'Id'
        parameter used in the API.

        :return: A dictionary with the 'Id' parameter information.
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "Id",
            "in": "path",
            "description": "ID",
            "required": True,
            "type": "integer",
        }

    def _domain_parameter(self):
        """
        Generates a dictionary containing the information of the 'domain'
        parameter used in the API.

        :return: A dictionary with the 'domain' parameter information.
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "domain",
            "in": "query",
            "description": "{} \n\n {}".format(
                _(
                    "Search domain to read. (" "Defaults to an empty domain " "that will match all records) "
                    # '<a href="https://www.odoo.com/documentation/15.0/'
                    # "en/developer/reference/addons/"
                    # 'orm.html#reference-orm-domains" '
                    # 'target="_blank">Documentation</a>'
                ),
                _("Example: `[('name', '=', 'Test')]`"),
            ),
            "required": False,
            "type": "string",
        }

    def _fields_parameter(self):
        """
        Generates a dictionary containing the information of the 'limit'
        parameter used in the API.

        :return: A dictionary with the 'limit' parameter information.
        :rtype: dict
        """

        self.ensure_one()
        return {
            "name": "fields",
            "in": "query",
            "description": "{} \n\n {}".format(
                _("List of fields to read. (Defaults to all fields)"),
                _("Example: `['id', 'name']`"),
            ),
            "required": False,
            "type": "string",
        }

    def _offset_parameter(self):
        """
        Generates a dictionary containing the information of the 'offset'
        parameter used in the API.

        :return: A dictionary with the 'offset' parameter information.
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "offset",
            "in": "query",
            "description": _("Number of records to skip. (Defaults to 0)"),
            "required": False,
            "type": "integer",
        }

    def _limit_parameter(self):
        """
        Generates a dictionary containing the information of the 'limit'
        parameter used in the API.

        :return: A dictionary with the 'limit' parameter information.
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "limit",
            "in": "query",
            "default": self.limit,
            "description": _("Maximum number of records to return. {}").format(
                _("(Maximum: {})").format(self.limit) if self.limit else ""
            ),
            "required": False,
            "type": "integer",
        }

    def _order_parameter(self):
        """
        Generates a dictionary containing the information of the 'order'
        parameter used in the API.

        :return: A dictionary with the 'order' parameter information.
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "order",
            "in": "query",
            "description": "{} \n\n {}".format(
                _(
                    "Param to sort result. (Defaults to no sort) "
                    "\n Field name followed by the sort operator. "
                    "(asc or desc)"
                ),
                _("Example: {}").format("`name asc` {} `name desc, id asc`".format(_("or"))),
            ),
            "required": False,
            "type": "string",
        }

    def _context_parameter(self, _type="query"):
        """
        Generates a dictionary containing the information of the 'context'
        parameter used in the API.

        :param type: The location of the parameter (e.g., 'query', 'formData').
        :type type: str
        :return: A dictionary with the 'context' parameter information.
        :rtype: dict
        """
        self.ensure_one()
        return {
            "name": "context",
            "in": _type,
            "description": "{} \n\n {}".format(_("Specific context to method"), _('Example: `{"lang": "fr_FR"}`')),
            "type": "string",
            "required": False,
        }

    # Get
    def _get_parameters_all_elements(self):
        """
        Generates a list containing dictionaries of all the parameters used
        in the 'get' method of the API.

        :return: A list with dictionaries of all 'get' parameters.
        :rtype: list
        """
        self.ensure_one()
        return [
            self._request_id_parameter(),
            self._from_date_parameter(),
            self._last_modified_date_parameter(),
            self._domain_parameter(),
            self._fields_parameter(),
            self._offset_parameter(),
            self._limit_parameter(),
            self._order_parameter(),
            self._context_parameter(),
        ]

    def _get_parameters_one_element(self):
        """
        Generates a list containing dictionaries of the parameters used
        for getting one element in the 'get' method of the API.

        :return: A list with dictionaries of 'get' parameters for one element.
        :rtype: list
        """
        self.ensure_one()
        return [
            self._request_id_parameter(),
            self._id_parameter(),
            self._fields_parameter(),
            self._context_parameter(),
        ]

    def get_domain(self, kwargs):
        domain = kwargs.get("domain", [])

        # populate domain
        if "from_date" in kwargs:
            domain.append(("create_date", ">=", kwargs["from_date"]))
            del kwargs["from_date"]

        if "last_modified_date" in kwargs:
            domain.append(("write_date", ">", kwargs["last_modified_date"]))
            del kwargs["last_modified_date"]

        # Get all fields of model
        model_fields = self.env[self.model].fields_get().keys()

        kw_copy = kwargs.copy()
        for field in kw_copy:
            if field in model_fields:
                domain.append((field, "=", kwargs[field]))
                del kwargs[field]

        del kw_copy

        if self.filter_domain:
            domain += self.eval_domain(self.filter_domain)

        return domain

    def _clean_kwargs(self, kw, keys):
        for key in kw.copy():
            if key not in keys:
                del kw[key]

    def search_treatment_kwargs(self, kwargs):
        """
        Processes the search kwargs to apply limits, domains, and fields.

        :param kwargs: A dictionary containing the search parameters.
        :type kwargs: dict
        :return: A dictionary with the processed search parameters.
        :rtype: dict
        """
        self.ensure_one()

        # Limit
        limit = kwargs.get("limit", 0)
        max_limit = self.limit if self.limit else MAX_LIMIT
        kwargs["limit"] = limit if (limit and limit <= max_limit) else max_limit

        # Offset
        kwargs["offset"] = kwargs.get("start_from", 0)
        if "start_from" in kwargs:
            del kwargs["start_from"]

        # Domain
        kwargs["domain"] = self.get_domain(kwargs)

        # Fields
        self._treatment_fields(kwargs)

        # Remove unnecessary keys
        self._clean_kwargs(kwargs, ["limit", "offset", "domain", "fields"])
        return kwargs

    def read_treatment_kwargs(self, kwargs):
        """
        Processes the read kwargs to apply fields.

        :param kwargs: A dictionary containing the read parameters.
        :type kwargs: dict
        :return: A dictionary with the processed read parameters.
        :rtype: dict
        """
        self.ensure_one()
        # Fields
        self._treatment_fields(kwargs)
        return kwargs

    def _treatment_fields(self, kwargs):
        self.ensure_one()
        lists_fields = ["id"] + self.field_ids.mapped("name")
        old_fields = kwargs.get("fields", [])
        if old_fields:
            kwargs["fields"] = list(set(old_fields) & set(lists_fields))
        else:
            kwargs["fields"] = lists_fields
        return kwargs

    def get_definition_properties(self):
        self.ensure_one()
        properties = {"id": {"type": "integer"}}
        for field in self.field_ids:
            _type, _format = convert_field_type_to_swagger(field.ttype)
            values = {
                "type": _type,
                "format": _format,
                "description": field.field_description or "",
            }
            self._update_values_ttype(field, values, definition=True)
            field_alias = self._get_field_name_alias(field)
            field_name = field.name if not field_alias else field_alias.alias_name
            properties.update({field_name: values})
        return properties

    # Post
    def _post_parameters(self):
        self.ensure_one()
        return self._post_properties() + [
            self._request_id_parameter(),
            self._context_parameter(_type="formData"),
        ]

    def _post_properties(self):
        self.ensure_one()
        properties = []
        for api_field in self.api_field_ids.filtered(lambda f: not f.default_value):
            field_name = api_field._get_field_name()
            _type, _format = convert_field_type_to_swagger(api_field.field_id.ttype)
            values = {
                "in": "formData",
                "name": field_name,
                "type": _type,
                "format": _format,
                "description": api_field.description or "",
                "required": api_field.required,
            }
            # Update values in terms of ttype
            self._update_values_ttype(api_field.field_id, values)
            properties.append(values)
        return properties

    def post_treatment_values(self, post_values):
        self.ensure_one()
        post_values = self._fields_alias_treatment(post_values)
        # Remove fields unspecified
        new_values = post_values.copy()
        api_fields = self.api_field_ids.mapped("field_name")
        for field in post_values.keys():
            if field not in api_fields:
                new_values.pop(field)
        # Add fields with default_value
        for field in self.api_field_ids.filtered(lambda f: f.default_value):
            new_values[field.field_name] = safe_eval.safe_eval(field.default_value)
        # Convert bool
        fields_boolean = self.api_field_ids.filtered(lambda f: f.field_id.ttype == "boolean").mapped("field_name")
        for field in fields_boolean:
            if field in post_values:
                new_values[field] = True if post_values.get(field) in ["1", "true", "True"] else False
        # Convert many2many & one2many
        fields_many2many = self.api_field_ids.filtered(lambda f: f.field_id.ttype in ["many2many", "one2many"]).mapped(
            "field_name"
        )
        for field in fields_many2many:
            if field in post_values:
                values = post_values.get(field)
                if isinstance(values, int):
                    values = [values]
                new_values[field] = values
        return new_values

    # Put
    def _put_parameters(self):
        self.ensure_one()
        parameters = [
            self._id_parameter(),
        ]
        return (
            parameters
            + self._post_properties()
            + [
                self._request_id_parameter(),
                self._context_parameter(_type="formData"),
            ]
        )

    # Delete
    def _delete_parameters(self):
        self.ensure_one()
        return [
            self._request_id_parameter(),
            self._id_parameter(),
            self._context_parameter(_type="formData"),
        ]

    # Put Custom function
    def _custom_parameters(self):
        self.ensure_one()
        parameters = self._custom_function_parameters() + [self._context_parameter(_type="formData")]
        if self.function_apply_on_record:
            parameters = [self._id_parameter()] + parameters
        return parameters

    def _custom_function_parameters(self):
        self.ensure_one()
        properties = []
        for function_parameter in self.function_parameter_ids.filtered(lambda f: not f.default_value):
            parameter_format = ""
            parameter_type = function_parameter.type
            if parameter_type == "float":
                parameter_type = "number"
                parameter_format = "float"
            values = {
                "name": function_parameter.name,
                "in": "formData",
                "description": function_parameter.description or "",
                "required": function_parameter.required,
                "type": parameter_type,
                "format": parameter_format,
            }
            if parameter_type == "array":
                values.update(items={"type": "string"})
            properties.append(values)
        return properties

    def custom_treatment_values(self, post_values):
        def _real_type_python(_type):
            return {
                "integer": int,
                "float": float,
                "boolean": bool,
                "string": str,
                "array": list,
                "object": dict,
            }.get(_type)

        self.ensure_one()
        new_values = {}
        for function_parameter in self.function_parameter_ids:
            # Convert fields to real type python
            if function_parameter.name in post_values:
                value = post_values.get(function_parameter.name)
                python_type = _real_type_python(function_parameter.type)
                if not isinstance(value, python_type):
                    # Try to convert
                    try:
                        new_value = python_type(value)
                        new_values[function_parameter.name] = new_value
                    except Exception as e:
                        # Delete value if it's not possible to convert
                        _logger.error(e)
                else:
                    new_values[function_parameter.name] = value
            # Add fields with default_value
            if function_parameter.default_value:
                new_values[function_parameter.name] = safe_eval.safe_eval(function_parameter.default_value)
        return new_values

    # Others function
    def _form_urlencoded_consumes(self):
        return ["application/x-www-form-urlencoded"]

    def _update_values_ttype(self, field, values, definition=False):
        # Manage field selection
        field_name = field.name
        if field.ttype == "selection":
            if definition:
                values.update({"type": "string"})
            else:
                selection_keys = list(
                    dict(self.env[self.model].fields_get([field_name])[field_name]["selection"]).keys()
                )
                values.update(
                    {
                        "items": {
                            "type": "string",
                            "enum": selection_keys,
                        }
                    }
                )
        # Manage many2many & one2many
        if field.ttype in ["many2many", "one2many"]:
            values.update(
                {
                    "items": {
                        "type": "integer",
                    }
                }
            )
        # Manage many2one
        if field.ttype == "many2one":
            if definition:
                values.update(
                    {
                        "type": "integer",
                        "description": "ID of related record",
                    }
                )
        # Manage dates
        if field.ttype == "date":
            description = values.get("description", "")
            description += "\n\n {}".format(_("Example: `YYYY-MM-DD`"))
            values.update({"description": description})
        if field.ttype == "datetime":
            description = values.get("description", "")
            description += "\n\n {}".format(_("Example: `YYYY-MM-DD'T'HH:MM:ss.SSSZ`"))
            values.update({"description": description})
        return values

    def _get_eval_context(self):
        """Prepare the context used when evaluating python code
        :returns: dict -- evaluation context given to safe_eval
        """
        return {
            "datetime": safe_eval.datetime,
            "dateutil": safe_eval.dateutil,
            "time": safe_eval.time,
            "uid": self.env.uid,
            "user": self.env.user,
        }

    def eval_domain(self, domain):
        self.ensure_one()
        return safe_eval.safe_eval(domain, self._get_eval_context())

    def open_self_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _(self._description),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
        }

    def action_open_field_alias(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Field Name Alias"),
            "res_model": "spp_api.field.alias",
            "domain": self._get_related_field_alias_domain(),
            "view_mode": "tree,form",
            "context": {
                "default_api_path_id": self.id,
                "scoped_alias": True,
                "create": False,
            },
        }

    def _get_related_field_alias_domain(self):
        self.ensure_one()
        return [
            "|",
            ("api_path_id", "=", self.id),
            "&",
            ("api_path_id", "=", False),
            ("model_id", "=", self.model_id.id),
        ]

    def _get_field_name_alias(self, field):
        self.ensure_one()
        field_alias = (
            self.env["spp_api.field.alias"]
            .sudo()
            .search(
                [
                    ("field_id", "=", field.id),
                    ("api_path_id", "=", self.id),
                ],
                limit=1,
            )
        )
        if not field_alias:
            field_alias = (
                self.env["spp_api.field.alias"]
                .sudo()
                .search(
                    [
                        ("field_id", "=", field.id),
                        ("global_alias", "=", True),
                    ],
                    limit=1,
                )
            )
        return field_alias

    def _get_response_treatment(self, response_data):
        if isinstance(response_data, dict):
            response_data = [response_data]
        self.ensure_one()
        field_aliases = self.env["spp_api.field.alias"].sudo().search(self._get_related_field_alias_domain())
        for element in response_data:
            self._format_datetime(element)
            self._adjust_null_value_fields(element)
            self._adjust_many2one_fields(element)
            for field_alias in field_aliases:
                if field_alias.field_id.name not in element.keys():
                    continue
                element[field_alias.alias_name] = element.pop(field_alias.field_id.name)
        return response_data

    def _fields_alias_treatment(self, post_values):
        res = {}
        # Fetch all related field aliases just once
        field_aliases = self.env["spp_api.field.alias"].sudo().search(self._get_related_field_alias_domain())

        # Create a mapping from alias_name to field_id.name for direct lookup
        alias_to_field_name_map = {alias.alias_name: alias.field_id.name for alias in field_aliases}

        for key, value in post_values.items():
            # Directly lookup the key in the mapping
            if key in alias_to_field_name_map:
                # If the alias exists, replace key with the corresponding field name
                res[alias_to_field_name_map[key]] = value
            else:
                # If no alias, use the original key
                res[key] = value

        return res

    @api.model
    def _format_datetime(self, element):
        for key in element:
            if not isinstance(element[key], date) or not isinstance(element[key], datetime):
                continue
            element[key] = datetime_format(element[key])

    def _adjust_null_value_fields(self, element):
        VARCHAR_TYPES = ["char", "text", "html", "selection", "reference"]
        NULL_TYPES = [
            "date",
            "datetime",
            "binary",
            "many2one",
            "many2one_reference",
            "integer",
            "float",
            "monetary",
        ]
        X_TO_MANY_TYPES = ["one2many", "many2many"]

        model_sudo = self.env[self.model].sudo()
        for key in element:
            if element[key]:
                continue
            field_type = model_sudo._fields[key].type
            if field_type == "boolean":
                continue
            if field_type in VARCHAR_TYPES:
                element[key] = ""
            if field_type in X_TO_MANY_TYPES:
                element[key] = []
            if field_type in NULL_TYPES:
                element[key] = None

    def _adjust_many2one_fields(self, element):
        model_sudo = self.env[self.model].sudo()
        for key in element:
            if model_sudo._fields[key].type not in ("many2one", "many2one_reference"):
                continue
            if element[key] and type(element[key]) in (list, tuple) and len(element[key]) == 2:
                element[key] = element[key][0]
