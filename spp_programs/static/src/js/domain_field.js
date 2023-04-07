odoo.define("spp_programs.domain", function (require) {
    const {FieldDomain} = require("web.basic_fields");
    var Domain = require("web.Domain");

    FieldDomain.include({
        _target_type_prefilter_domain: function () {
            var value = this.value || "[]";
            var value_domain = Domain.prototype.stringToArray(value, this.record.evalContext);
            var added_domain = [];
            if (this.record.evalContext.target_type === "group") {
                added_domain = [
                    ["is_group", "=", true],
                    ["is_registrant", "=", true],
                ];
            } else {
                added_domain = [
                    ["is_group", "=", false],
                    ["is_registrant", "=", true],
                ];
            }
            if (added_domain) {
                value_domain.push.apply(value_domain, added_domain);
            }
            return value_domain;
        },
        _fetchCount(force = false) {
            // Changes is only for program wizard
            if (this.record.evalContext.active_model === "g2p.program.create.wizard") {
                if (!this._domainModel) {
                    this._isValidForModel = true;
                    this.nbRecords = 0;
                    return Promise.resolve();
                }

                // Do not re-fetch the count if nothing has changed
                const value = this.value || "[]";
                const key = `${this._domainModel}/${value}`;
                if (!force && this.lastCountFetchKey === key) {
                    return this.lastCountFetchProm;
                }
                this.lastCountFetchKey = key;

                this.nbRecords = null;

                const context = this.record.getContext({fieldName: this.name});

                var value_domain = this._target_type_prefilter_domain();

                this.lastCountFetchProm = new Promise((resolve) => {
                    this._rpc(
                        {
                            model: this._domainModel,
                            method: "search_count",
                            args: [value_domain],
                            context: context,
                        },
                        {shadow: true}
                    )
                        .then((nbRecords) => {
                            this._isValidForModel = true;
                            this.nbRecords = nbRecords;
                            resolve();
                        })
                        .guardedCatch((reason) => {
                            reason.event.preventDefault();
                            this._isValidForModel = false;
                            this.nbRecords = 0;
                            resolve();
                        });
                });
                return this.lastCountFetchProm;
            }
            return this._super.apply(this, arguments);
        },
        _onShowSelectionButtonClick: function (e) {
            e.preventDefault();
            // Changes is only for program wizard
            if (this.record.evalContext.active_model === "g2p.program.create.wizard") {
                var value_domain = this._target_type_prefilter_domain();
                this.value = Domain.prototype.arrayToString(value_domain);
            }
            this._super.apply(this, arguments);
        },
    });
});
