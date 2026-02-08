# CEL Domain Query Builder (Odoo 17)

Write simple CEL-like expressions to filter OpenSPP/OpenG2P records without knowing Odoo domains.

## Purpose

- **For non-developers**: Type human-readable expressions like `age_years(me.birthdate) < 5`
- **Get Odoo domains**: Automatic translation to native Odoo query language
- **Preview results**: See matching records instantly in the wizard
- **OpenSPP optimized**: Built for Groups, Members, Programs, and Entitlements

## Quick Start

1. Open **Settings > CEL Domain > Rule Preview**
2. Choose a profile (e.g., Registry/Groups)
3. Enter your expression
4. Click **Validate & Preview**
5. See matching records and copy the domain

## New In This Version

- Metrics integration via `openspp_metrics` addon. Use metrics in CEL:
  - `metric("household.size", me, "current") >= 2` (on Groups profile)
  - `metric("education.attendance_pct", me, "2024-09") >= 85` (on Individuals)
- Cycle helpers for OpenG2P cycles:
  - `cycle(program_name, cycle_name)`, `last_cycle(program_name)`, `first_cycle(program_name)`

## Configuration

### Three Configuration Layers

CEL Domain uses a **three-tier configuration system** (highest to lowest priority):

1. **System Parameters** (Runtime customization by admins)
2. **YAML File** (Deployment customization)
3. **Hardcoded Defaults** (Fallback)

### 1. System Parameters (Highest Priority)

Configure via **Settings > Technical > Parameters > System Parameters**

**Key format**: `cel_domain.profile.<profile_name>` **Value**: JSON object with profile configuration

Example:

```
Key: cel_domain.profile.registry_groups
Value: {"root_model": "res.partner", "base_domain": [["is_registrant", "=", true], ["is_group", "=", true]], "symbols": {...}}
```

### 2. YAML Configuration (Deployment Customization)

Edit `cel_domain/data/cel_symbols.template.yaml` to customize profiles.

**Location**: `odoo/custom/src/openspp_cel/cel_domain/data/cel_symbols.template.yaml`

**Example customizations**:

```yaml
# Add custom role names (e.g., for multilingual deployments)
registry_groups:
  roles:
    head: ["Head", "Household Head", "HoH", "Chef de ménage"]  # Add French

# Include ended members by default (instead of active-only)
registry_groups:
  symbols:
    members:
      default_domain: []  # Empty = no filter

# Add custom symbols
registry_individuals:
  symbols:
    district:
      relation: "many2one"
      field: "district_id"
      model: "spp.district"
```

**YAML merges with defaults**: You only need to specify what you want to override. Other settings are
inherited from hardcoded defaults.

### 3. Hardcoded Defaults (Fallback)

Built-in defaults in `cel_registry.py` ensure the system works out-of-the-box.

## Available Profiles

### Registry / Individuals

**Root model**: `res.partner` (registrants, non-groups)

**Symbols**:

- `me` - The individual registrant
- `groups` - Groups this individual belongs to
- `enrollments` - Program enrollments
- `entitlements` - Benefits received

**Example**:

```cel
age_years(me.birthdate) < 5 and has_tag("Pregnant")
```

### Registry / Groups (Households)

**Root model**: `res.partner` (groups/households)

**Symbols**:

- `me` - The group/household
- `members` - Individuals in this group (⚠️ **active members by default**)
- `enrollments` - Program enrollments
- `entitlements` - Benefits received

**Example**:

```cel
count(members, m, head(m)) == 1 and members.exists(m, age_years(m.birthdate) < 5)
```

**Important**: `members` automatically filters to active memberships (`is_ended=False`). To include ended
members:

```cel
members.exists(m, m._link.is_ended or age_years(m.birthdate) < 5)
```

### Program Memberships

**Root model**: `g2p.program_membership`

**Symbols**:

- `me` - The enrollment record
- `registrant` - The enrolled person/group
- `program` - The program

**Example**:

```cel
me.state == "enrolled" and program.name == "Cash Transfer"
```

### Entitlements

**Root model**: `g2p.entitlement`

**Symbols**:

- `me` - The entitlement/benefit record
- `registrant` - The beneficiary
- `program` - The program

**Example**:

```cel
me.state == "approved" and me.payment_status == "notpaid"
```

## Supported Functions

### Date/Time Functions

- `today()` - Current date
- `now()` - Current datetime
- `days_ago(n)` - Date n days ago
- `months_ago(n)` - Date n months ago
- `years_ago(n)` - Date n years ago
- `date("YYYY-MM-DD")` - Parse date from string

### Age Calculations

- `age_years(birthdate)` - Age in years
- Example: `age_years(me.birthdate) < 5`

### Comparisons

- `between(value, min, max)` - Range check
- Example: `between(age_years(me.birthdate), 6, 11)`

### Text Matching

- `contains(field, "text")` - Case-insensitive substring match
- `has_tag("tag_name")` - Filter by partner category tag

### Program Lookups

- `program("Program Name")` - Resolve program by name

### Metrics

- `metric(name, subject, period_key)` - Compare against values from the metrics system. Requires
  `openspp_metrics` installed.
  - Subject is typically `me`.
  - Period key can be a free string (e.g., `"2024-09"`) or a cycle helper like `last_cycle("Cash Transfer")`.

### Membership Functions

- `head(m)` - True if member is head of household
- `has_role(m, "role_name")` - True if member has specified role

## Expression Examples

### Example 1: Children Under 5

```cel
age_years(me.birthdate) < 5
```

**Domain**: `[('birthdate', '>', today - 5 years)]`

### Example 2: Single-Headed Household with Young Child

```cel
count(members, m, head(m)) == 1 and members.exists(m, age_years(m.birthdate) < 5)
```

**Explanation**: Groups with exactly one head of household and at least one child under 5 (active members
only).

### Example 3: Elderly Woman-Headed Household

```cel
members.exists(m, head(m) and m.gender == "Female" and age_years(m.birthdate) >= 60)
```

### Example 4: Pregnant Women with Phone Numbers

```cel
me.phone != "" and has_tag("Pregnant")
```

### Example 5: School-Aged Children (6-11 years)

```cel
between(age_years(me.birthdate), 6, 11)
```

### Example 6: Enrolled in Specific Program

```cel
me.state == "enrolled" and program.name == "Cash Transfer"
```

### Example 7: Groups with at least 2 active members (metric)

```cel
metric("household.size", me, "current") >= 2
```

### Example 8: Attendance threshold over a month (metric)

```cel
metric("education.attendance_pct", me, "2024-09") >= 85
```

### Example 9: All members satisfy a condition (all_over)

```cel
all_over(members, metric("education.attendance_pct", m, "2024-09") >= 80)
```

All members must have attendance >= 80. Missing values fail-closed (treated as not satisfying the condition).

## Registry (CEL) Menus

Install the optional `cel_registry_search` addon to access ready-to-use list views with a CEL filter wizard:

- Registry (CEL) > Individuals
- Registry (CEL) > Groups

Both menus are visible to Registry Admin/Registrar and Settings/Administrator. If you see an AccessError
creating the wizard, make sure the module is installed and your user has one of those groups.

## Explain Panel

When validating an expression, the wizard shows:

- A Summary tab with the translated domain and a natural language explanation
- A Metrics Explain tab (when the expression uses metrics) with per-metric statistics: requested, cache hits,
  misses, fresh fetches and coverage

## Troubleshooting

- Tests: run `invoke test --modules=cel_domain --mode=update` (ensures DB and tags are correct). For per-file
  logs and a JUnit report, run `invoke test-junit`.
- If you see a symlink error when starting containers, stop first with `invoke stop` and rerun the command.

## Running tests (Doodba)

Run the whole suite (preferred during iteration):

```bash
invoke test --modules=cel_domain --mode=update
```

Run a single file:

```bash
docker compose run --rm odoo \
  odoo --test-enable --stop-after-init --workers=0 \
  -d devel -i cel_domain \
  --test-file /opt/odoo/auto/addons/cel_domain/tests/test_examples_groups_members.py \
  --log-handler=odoo.addons.spp_cel_domain:INFO
```

Artifacts: `test-reports/cel_domain.log` and `test-reports/cel_domain.junit.xml` are created by `invoke test`.

### Example 7: Approved But Unpaid Entitlements

```cel
me.state == "approved" and me.payment_status == "notpaid" and me.valid_from >= days_ago(30)
```

### Example 8: Two or More Children Under 5

```cel
count(members, m, age_years(m.birthdate) < 5) >= 2
```

## Important Notes

### Active Members Default

By default, `members.exists()` only queries **active memberships** (`is_ended=False`). This is usually what
you want.

To include ended members explicitly:

```cel
members.exists(m, m._link.is_ended or <your_condition>)
```

To change the default globally, edit the YAML configuration:

```yaml
registry_groups:
  symbols:
    members:
      default_domain: [] # Empty = include all members
```

### Membership Link Fields

Access membership-specific fields via `m._link`:

- `m._link.is_ended` - Whether membership has ended
- `m._link.start_date` - When membership started
- `m._link.ended_date` - When membership ended
- `m._link.kind` - Membership roles/kinds

### Error Handling

The wizard provides helpful error messages:

- **Syntax errors**: Position and suggestion
- **Unknown symbols**: "Did you mean 'members'?"
- **Type errors**: Clear explanation of what went wrong

## Testing

### Run All Tests

```bash
# From project root
invoke test --modules=cel_domain

# Or with update mode
invoke test --modules=cel_domain --mode=update
```

### Run Specific Tests

```bash
# Test YAML configuration
invoke test --modules=cel_domain --test-tags test_yaml_configuration

# Test has_tag function
invoke test --modules=cel_domain --test-tags test_missing_has_tag_function
```

## Administration Guide

### Customizing for Your Deployment

**Option 1**: Edit YAML file (recommended for deployment-wide changes)

1. Edit `cel_domain/data/cel_symbols.template.yaml`
2. Restart Odoo or update the module

**Option 2**: Use system parameters (recommended for runtime changes)

1. Go to **Settings > Technical > Parameters > System Parameters**
2. Create new parameter: `cel_domain.profile.<profile_name>`
3. Set value as JSON configuration
4. Changes take effect immediately

### Adding Custom Symbols

Example: Add a custom `district` symbol for individuals

**In YAML**:

```yaml
registry_individuals:
  symbols:
    district:
      relation: "many2one"
      field: "district_id"
      model: "spp.district"
```

**Usage**:

```cel
me.district == "North District"
```

### Adding Custom Roles

Example: Add custom role names for your country

**In YAML**:

```yaml
registry_groups:
  roles:
    head: ["Head", "Household Head", "HoH", "Chef de ménage", "رئيس الأسرة"]
    spouse: ["Spouse", "Partner", "Époux", "شريك"]
    child: ["Child", "Enfant", "طفل"]
```

## Troubleshooting

### "Profile not found"

- Check spelling of profile name
- Verify YAML file exists and is valid
- Check system parameters for typos

### "Unknown symbol 'X'"

- Check available symbols for your profile in YAML
- Use wizard's profile selector to see available symbols
- Check for typos (wizard provides suggestions)

### YAML not loading

- Ensure PyYAML is installed (should be in Odoo)
- Check YAML file syntax with online validator
- Look for errors in Odoo logs: `[CEL Registry]`

### Active members only (can't see ended members)

This is by design! Use `m._link.is_ended` explicitly:

```cel
members.exists(m, m._link.is_ended or <condition>)
```

## Limitations

- **NOT with complex subqueries**: Cannot negate `exists()` or `count()` (performance constraint)
- **String escapes**: Limited support for escaped quotes in strings
- **No macros**: Single expression only, no multi-line or reusable macros

## License

LGPL-3

## Support

For issues or questions:

- Check this README first
- Review YAML configuration examples
- Check Odoo logs for `[CEL Registry]` messages
- File issues at your project's issue tracker
