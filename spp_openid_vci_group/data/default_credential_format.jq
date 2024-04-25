{
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        (.web_base_url + "/api/v1/vci/.well-known/contexts.json")
    ],
    "id": .vc_id,
    "type": ["VerifiableCredential", .issuer.credential_type],
    "issuer": .issuer.unique_issuer_id,
    "issuanceDate": .curr_datetime,
    "credentialSubject": {
        "vcVer": "VC-V1",
        "id": (.web_base_url  + "/api/v1/registry/individual/" + (.partner.id | tostring)),
        "name": [
            {
                "value": (.partner.name // null)
            }
        ],
        "phone": (.partner.phone // null),
        "addressLine1": (if .partner_address.street_address then [
            {
                "value": .partner_address.street_address
            }
        ] else null end),
        "province": (if .partner_address.locality then [
            {
                "value": .partner_address.locality
            }
        ] else null end),
        "region": (if .partner_address.region then [
            {
                "value": .partner_address.region
            }
        ] else null end),
        "postalCode": .partner_address.postal_code,
    }
}
