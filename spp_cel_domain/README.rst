CEL Domain Query Builder
========================

This addon lets analysts write short CEL-like expressions to filter records
and preview results. It is tailored for OpenSPP/OpenG2P data models
(Registry Individuals/Groups via memberships, Program Memberships, Entitlements).

Highlights

- Wizard to validate an expression, show the resulting domain and a short
  explanation, and preview matching records.
- Profiles for common roots (Individuals, Groups, Program Memberships, Entitlements).
- Safe execution: no eval, all filters compiled to ORM domains and subqueries.

Usage

Open: Settings » CEL Domain » Rule Preview. Choose a profile and target model,
paste an expression, then click "Validate & Preview".

Examples (Groups profile)

* Single-headed household with a child under 5::

    count(members, m, head(m) and not m._link.is_ended) == 1
    and members.exists(m, age_years(m.birthdate) < 5 and not m._link.is_ended)

* Elderly woman–headed household::

    members.exists(m, head(m) and m.gender == "Female"
                   and age_years(m.birthdate) >= 60 and not m._link.is_ended)

