API_ENDPOINT = "/registry"
SYNC = "/sync"
SYNC_SEARCH_ENDPOINT = API_ENDPOINT + SYNC + "/search"
OAUTH2_ENDPOINT = "/oauth2/client/token"

OPERATION_MAPPING = {
    "eq": "=",
    "gt": ">",
    "lt": "<",
    "ge": ">=",
    "le": "<=",
    "in": "in",
}

FIELD_MAPPING = {
    "birthdate": "birthdate",
}

INDIVIDUAL = "SPP:RegistryType:Individual"

REG_TYPE_CHOICES = [INDIVIDUAL]

PREDICATE = "predicate"

ALLOWED_QUERY_TYPE = [PREDICATE]
