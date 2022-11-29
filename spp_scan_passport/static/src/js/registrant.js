function httpCall(suffix = "") {
    const Http = new XMLHttpRequest();
    const url = "http://localhost:12222/";
    Http.open("GET", url + suffix, false);
    Http.send(null);
    return Http.responseText;
}

function scanPassport() {
    console.log("initializing........");
    httpCall("initialise");

    const data = JSON.parse(httpCall("readdocument"));
    const gender_index_dict = {
        "": "0",
        Female: "1",
        Male: "2",
        Other: "3",
    };
    let gender = data.gender;
    if (!(gender in gender_index_dict)) {
        gender = "";
    }

    document.querySelector("input[name='family_name']").value = data.family_name;
    document.querySelector("input[name='given_name']").value = data.given_name;
    document.querySelector("input[name='birthdate']").value = data.birth_date;
    document.querySelector("select[name='gender']").selectedIndex = gender_index_dict[gender];

    $('input[name="family_name"]').trigger("change");
    $('input[name="given_name"]').trigger("change");
    $('input[name="birthdate"]').trigger("change");
    $('select[name="gender"]').trigger("change");

    console.log("shutting down........");
    httpCall("shutdown");
}
