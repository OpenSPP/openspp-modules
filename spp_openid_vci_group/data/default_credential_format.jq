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
        "id": (.partner.id | tostring),
        "name": (.partner.name // null),
        "email": (.partner.email // null),
        "phone": (.partner.phone // null),
        "addressLine1": .partner_address.street_address,
        "province": .partner_address.locality,
        "region": .partner_address.region,
        "postalCode": .partner_address.postal_code,
    }
}
