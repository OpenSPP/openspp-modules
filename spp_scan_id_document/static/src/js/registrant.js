odoo.define(function () {
    const initialise_url = "http://localhost:12222/initialise";
    const readdocument_url = "http://localhost:12222/readdocument";
    const shutdown_url = "http://localhost:12222/shutdown";

    function populate_field(data) {
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
    }

    document.getElementById("id_scan_button").onclick = function () {
        fetch(initialise_url, {
            method: "GET",
        }).then((initialise_response) => {
            initialise_response.json();
            fetch(readdocument_url, {
                method: "GET",
            })
                .then((read_response) => read_response.json())
                .then((response_json) => {
                    populate_field(response_json);
                    fetch(shutdown_url, {
                        method: "GET",
                    }).then((shutdown_response) => {
                        shutdown_response.json();
                        // Shutdown completed
                    });
                });
        });
    };
});
