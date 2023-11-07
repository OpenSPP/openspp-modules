ID_TYPE = "id_type"
BIRTHDATE_RANGE = "birthdate_range"

ID_TYPE_VALUE = "idtype-value"
PREDICATE = "predicate"

ID_TYPE_BRN = "BRN"
ID_TYPE_DRN = "DRN"
ID_TYPE_MRN = "MRN"
ID_TYPE_CRVS_ID = "OPENCRVS_RECORD_ID"
ID_TYPE_NID = "NID"

QUERY_TYPE_MAPPING = {ID_TYPE: ID_TYPE_VALUE, BIRTHDATE_RANGE: PREDICATE}

ID_TYPE_LABEL = "ID Type"
BIRTHDATE_RANGE_LABEL = "Birthdate Range"

FILTER_TYPE_CHOICES = [
    (ID_TYPE, ID_TYPE_LABEL),
    (BIRTHDATE_RANGE, BIRTHDATE_RANGE_LABEL),
]

ID_TYPE_CHOICES = [
    (ID_TYPE_BRN, "Birthday Registration Number"),
    (ID_TYPE_NID, "National ID"),
    (ID_TYPE_DRN, "Death Registration Number"),
    (ID_TYPE_MRN, "Marriage Registration Number"),
    (ID_TYPE_CRVS_ID, "CRVS Record ID"),
]
