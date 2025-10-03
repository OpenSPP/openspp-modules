# CEL Domain Query Builder: Complete User Guide

**Target Audience**: Program managers, administrators, and non-developers who need to target beneficiaries for
social protection programs.

**Version**: 1.0 **Last Updated**: October 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basic Concepts](#basic-concepts)
4. [Writing Your First Query](#writing-your-first-query)
5. [Complete Function Reference](#complete-function-reference)
6. [Real-World Examples](#real-world-examples)
7. [Profile Reference](#profile-reference)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Introduction

### What is CEL Domain?

CEL Domain is a **query builder** that lets you filter registrants, groups, programs, and entitlements using
**simple, human-readable expressions** instead of complex database queries.

### Why use it?

- ✅ **No coding required**: Write expressions like `age_years(me.birthdate) < 5`
- ✅ **Instant preview**: See matching records immediately
- ✅ **Safe**: Can't break anything or expose data
- ✅ **Powerful**: Supports complex criteria for accurate targeting

### Who is this for?

- **Program Managers**: Define eligibility criteria for programs
- **M&E Officers**: Create reports and analyze beneficiary data
- **Administrators**: Filter and segment registry data
- **IT Staff**: Integrate with workflows and automations

---

## Getting Started

### Opening the Query Builder

1. Log in to OpenSPP/OpenG2P
2. Navigate to **Settings > CEL Domain > Rule Preview**
3. You'll see:
   - **Profile** dropdown (Registry/Individuals, Registry/Groups, etc.)
   - **Expression** field (where you write your query)
   - **Validate & Preview** button

### Your First Query: Children Under 5

Let's find all individuals under 5 years old:

```
1. Select Profile: "Registry / Individuals"
2. Enter Expression: age_years(me.birthdate) < 5
3. Click "Validate & Preview"
```

**Result**: You'll see a count of matching records and a preview of the first 50.

---

## Basic Concepts

### What is a "Profile"?

A **profile** tells CEL Domain what kind of data you're querying:

| Profile                | What it queries        | Example use case                    |
| ---------------------- | ---------------------- | ----------------------------------- |
| Registry / Individuals | Individual registrants | "Find all pregnant women"           |
| Registry / Groups      | Groups/households      | "Find female-headed households"     |
| Program Memberships    | Enrollments            | "Find who is enrolled in Program X" |
| Entitlements           | Benefits/payments      | "Find approved but unpaid benefits" |

### The "me" Symbol

`me` represents **the current record** being checked:

- In **Individuals** profile: `me` = an individual person
- In **Groups** profile: `me` = a group/household
- In **Enrollments** profile: `me` = an enrollment record

### Fields You Can Access

Use dot notation to access fields:

```cel
me.name          # Name of the person/group
me.birthdate     # Birth date
me.phone         # Phone number
me.gender        # Gender ("Male", "Female", etc.)
me.is_registrant # Whether they are a registrant
```

---

## Writing Your First Query

### Basic Comparisons

**Find individuals named "Sarah":**

```cel
me.name == "Sarah"
```

**Find individuals with phone numbers:**

```cel
me.phone != ""
```

**Find individuals born before 2000:**

```cel
me.birthdate < date("2000-01-01")
```

### Age Queries

**Children under 5:**

```cel
age_years(me.birthdate) < 5
```

**School-aged children (6-11 years):**

```cel
between(age_years(me.birthdate), 6, 11)
```

**Elderly (60+ years):**

```cel
age_years(me.birthdate) >= 60
```

### Combining Conditions

Use `and` to require **all** conditions:

**Elderly women:**

```cel
age_years(me.birthdate) >= 60 and me.gender == "Female"
```

Use `or` to allow **any** condition:

**Children or elderly:**

```cel
age_years(me.birthdate) < 5 or age_years(me.birthdate) >= 60
```

### Tag-Based Filtering

**Find pregnant women:**

```cel
has_tag("Pregnant")
```

**Find disabled individuals:**

```cel
has_tag("Disabled")
```

### Text Matching

**Find names starting with "Muhammad":**

```cel
startswith(me.name, "Muham")
```

**Find names containing "Ali":**

```cel
contains(me.name, "Ali")
```

---

## Complete Function Reference

### Date & Time Functions

| Function             | Description       | Example                             |
| -------------------- | ----------------- | ----------------------------------- |
| `today()`            | Current date      | `me.birthdate > today()`            |
| `now()`              | Current datetime  | `me.created_at < now()`             |
| `date("YYYY-MM-DD")` | Specific date     | `me.birthdate < date("2020-01-01")` |
| `days_ago(n)`        | Date n days ago   | `me.updated >= days_ago(30)`        |
| `months_ago(n)`      | Date n months ago | `me.birthdate > months_ago(6)`      |
| `years_ago(n)`       | Date n years ago  | `me.birthdate < years_ago(18)`      |

### Age Functions

| Function          | Description  | Example                       |
| ----------------- | ------------ | ----------------------------- |
| `age_years(date)` | Age in years | `age_years(me.birthdate) < 5` |

### Comparison Functions

| Function                 | Description | Example                                   |
| ------------------------ | ----------- | ----------------------------------------- |
| `between(val, min, max)` | Range check | `between(age_years(me.birthdate), 6, 11)` |

### Text Functions

| Function                      | Description      | Example                        |
| ----------------------------- | ---------------- | ------------------------------ |
| `startswith(field, "prefix")` | Starts with text | `startswith(me.name, "Ahmad")` |
| `contains(field, "text")`     | Contains text    | `contains(me.name, "Ali")`     |
| `has_tag("tag_name")`         | Has category tag | `has_tag("Pregnant")`          |

### Program Functions

| Function                  | Description         | Example                                 |
| ------------------------- | ------------------- | --------------------------------------- |
| `program("Program Name")` | Get program by name | `e.program == program("Cash Transfer")` |

### Membership Functions (Groups Profile Only)

| Function              | Description          | Example                 |
| --------------------- | -------------------- | ----------------------- |
| `head(m)`             | Is head of household | `head(m)`               |
| `has_role(m, "role")` | Has specific role    | `has_role(m, "Spouse")` |

### Collection Functions (Groups Profile Only)

| Function                         | Description                 | Example                                         |
| -------------------------------- | --------------------------- | ----------------------------------------------- |
| `members.exists(var, condition)` | At least one member matches | `members.exists(m, age_years(m.birthdate) < 5)` |
| `count(members, var, condition)` | Count matching members      | `count(members, m, head(m)) == 1`               |

### Metrics & Aggregators (Optional)

You can use platform metrics such as attendance percentages inside CEL when the `openspp_metrics` addon is
installed.

Using a metric directly

```cel
metric("education.attendance_pct", me, "2024-09") >= 85
```

Aggregating a metric over members (Groups profile)

- Average value:

```cel
avg_over(members, metric("education.attendance_pct", m, "2024-09")) >= 80
```

- Coverage (fraction of members with a value):

```cel
coverage_over(members, metric("education.attendance_pct", m, "2024-09")) >= 0.8
```

- All members satisfy a threshold:

```cel
all_over(members, metric("education.attendance_pct", m, "2024-09") >= 85)
```

Semantics

- Unknown values are excluded from numeric averages.
- `coverage_over` returns present/total (0..1).
- `all_over` treats missing as False (fail‑closed).
- Enforce minimum coverage when needed:

```cel
require_coverage(
  avg_over(members, metric("education.attendance_pct", m, "2024-09")),
  0.8
)
```

Cycle helpers

```cel
metric("education.attendance_pct", me, last_cycle(program("Education"))) >= 85
```

See EXTERNAL_METRICS_SPEC_V2.md for details.

---

## Real-World Examples

### Example 1: Early Childhood Program

**Goal**: Find households with children under 5

**Profile**: Registry / Groups

**Expression**:

```cel
members.exists(m, age_years(m.birthdate) < 5)
```

**Explanation**:

- `members.exists(...)` checks if any member matches
- `m` is a variable representing each member
- `age_years(m.birthdate) < 5` checks if member is under 5

---

### Example 2: Single Mother Support

**Goal**: Find female-headed households with young children

**Profile**: Registry / Groups

**Expression**:

```cel
count(members, m, head(m)) == 1 and
members.exists(m, head(m) and m.gender == "Female") and
members.exists(m, age_years(m.birthdate) < 5)
```

**Explanation**:

- `count(members, m, head(m)) == 1` ensures exactly one head
- `members.exists(m, head(m) and m.gender == "Female")` ensures head is female
- `members.exists(m, age_years(m.birthdate) < 5)` ensures has child under 5

---

### Example 3: Elderly Pension

**Goal**: Find individuals 60+ years old

**Profile**: Registry / Individuals

**Expression**:

```cel
age_years(me.birthdate) >= 60
```

**Explanation**: Simple age check for pension eligibility.

---

### Example 4: Maternal Health with Phone

**Goal**: Find pregnant women with phone numbers (for SMS reminders)

**Profile**: Registry / Individuals

**Expression**:

```cel
has_tag("Pregnant") and me.phone != ""
```

**Explanation**:

- `has_tag("Pregnant")` finds women tagged as pregnant
- `me.phone != ""` ensures they have a phone number

---

### Example 5: School Feeding Program

**Goal**: Find households with school-aged children (6-11 years)

**Profile**: Registry / Groups

**Expression**:

```cel
members.exists(m, between(age_years(m.birthdate), 6, 11))
```

**Explanation**:

- `between(age_years(m.birthdate), 6, 11)` checks age range 6-11
- At least one child must be in this range

---

### Example 6: Elderly Household with Phone

**Goal**: Find households with elderly members AND a phone number

**Profile**: Registry / Groups

**Expression**:

```cel
members.exists(m, age_years(m.birthdate) >= 60) and
members.exists(m, m.phone != "")
```

**Explanation**: Two separate checks:

1. Has at least one member 60+
2. Has at least one member with a phone

---

### Example 7: Multi-Children Vulnerability

**Goal**: Find households with 2 or more children under 5

**Profile**: Registry / Groups

**Expression**:

```cel
count(members, m, age_years(m.birthdate) < 5) >= 2
```

**Explanation**: `count()` returns the number of matching members, then check if >= 2.

---

### Example 8: Complex Vulnerability Index

**Goal**: Find vulnerable households (elderly OR disabled OR female-headed with children)

**Profile**: Registry / Groups

**Expression**:

```cel
members.exists(m, age_years(m.birthdate) >= 60 or has_tag("Disabled")) or
(count(members, m, head(m) and m.gender == "Female") >= 1 and
 members.exists(m, age_years(m.birthdate) < 5))
```

**Explanation**: Multiple vulnerability criteria combined with OR.

---

### Example 9: Program Enrollment Check

**Goal**: Find individuals enrolled in "Cash Transfer" program

**Profile**: Registry / Individuals

**Expression**:

```cel
enrollments.exists(e, e.program == program("Cash Transfer") and e.state == "enrolled")
```

**Explanation**:

- `enrollments.exists(...)` checks enrollment records
- `e.program == program("Cash Transfer")` matches program by name
- `e.state == "enrolled"` ensures active enrollment

---

### Example 10: Approved Unpaid Entitlements

**Goal**: Find benefits approved but not yet paid

**Profile**: Entitlements

**Expression**:

```cel
me.state == "approved" and me.payment_status == "notpaid"
```

**Explanation**: Filter entitlements by their state and payment status.

---

## Profile Reference

### Registry / Individuals Profile

**Root Model**: `res.partner` (individuals only)

**Available Symbols**:

- `me` - The individual registrant
- `groups` - Groups this individual belongs to
- `enrollments` - Program enrollments for this individual
- `entitlements` - Benefits received by this individual

**Common Fields**:

```cel
me.name          # Full name
me.birthdate     # Date of birth
me.phone         # Phone number
me.gender        # Gender
me.is_registrant # Boolean
```

**Example Queries**:

```cel
# Young children
age_years(me.birthdate) < 5

# Pregnant women with phones
has_tag("Pregnant") and me.phone != ""

# Women of reproductive age
me.gender == "Female" and between(age_years(me.birthdate), 15, 49)
```

---

### Registry / Groups Profile

**Root Model**: `res.partner` (groups/households only)

**Available Symbols**:

- `me` - The group/household
- `members` - Individuals in this group ⚠️ **Active members by default**
- `enrollments` - Program enrollments for this group
- `entitlements` - Benefits received by this group

**Important**: `members` automatically filters to **active memberships** (not ended). To include ended
members:

```cel
members.exists(m, m._link.is_ended or <your_condition>)
```

**Common Fields**:

```cel
me.name          # Group name
me.is_registrant # Boolean
me.is_group      # Boolean
```

**Member Fields** (accessed via `m.field`):

```cel
m.name           # Member's name
m.birthdate      # Member's birth date
m.gender         # Member's gender
m.phone          # Member's phone
m._link.is_ended # Whether membership has ended
m._link.kind     # Membership role/kind
```

**Example Queries**:

```cel
# Single female head with young child
count(members, m, head(m)) == 1 and
members.exists(m, head(m) and m.gender == "Female") and
members.exists(m, age_years(m.birthdate) < 5)

# Elderly couple household
count(members, m, age_years(m.birthdate) >= 60) >= 2

# Large family (5+ members)
count(members, m, true) >= 5
```

---

### Program Memberships Profile

**Root Model**: `g2p.program_membership`

**Available Symbols**:

- `me` - The enrollment record
- `registrant` - The enrolled person/group
- `program` - The program

**Common Fields**:

```cel
me.state            # Enrollment state: "draft", "enrolled", "exited"
me.enrollment_date  # When they enrolled
program.name        # Program name
registrant.name     # Beneficiary name
```

**Example Queries**:

```cel
# Active enrollments in specific program
me.state == "enrolled" and program.name == "Cash Transfer"

# Recent enrollments
me.enrollment_date >= days_ago(30)

# Exited members
me.state == "exited"
```

---

### Entitlements Profile

**Root Model**: `g2p.entitlement`

**Available Symbols**:

- `me` - The entitlement/benefit record
- `registrant` - The beneficiary
- `program` - The program

**Common Fields**:

```cel
me.state          # "draft", "approved", "paid", "cancelled"
me.payment_status # "notpaid", "paid", "failed"
me.valid_from     # Benefit start date
me.valid_until    # Benefit end date
me.amount         # Benefit amount
```

**Example Queries**:

```cel
# Approved but unpaid
me.state == "approved" and me.payment_status == "notpaid"

# Recent benefits (last 30 days)
me.valid_from >= days_ago(30)

# Failed payments needing retry
me.payment_status == "failed"
```

---

## Troubleshooting

### Error: "Syntax Error at position X"

**Problem**: Typo or missing parenthesis/quote

**Solution**: Check for:

- Matching parentheses: `age_years(me.birthdate < 5` ❌ → `age_years(me.birthdate) < 5` ✅
- Matching quotes: `me.name == "Sarah` ❌ → `me.name == "Sarah"` ✅

---

### Error: "Unknown symbol 'X'. Did you mean 'Y'?"

**Problem**: Typo in symbol name

**Example**: `memebrs.exists(...)` ❌ → Did you mean `members`? ✅

**Solution**: Check spelling and use the suggestion provided.

---

### Error: "Feature Not Supported: Negating complex expressions..."

**Problem**: Trying to use `not` with `exists()` or `count()`

**Example**: `not members.exists(m, age_years(m.birthdate) < 5)` ❌

**Solution**: Express the positive condition instead:

```cel
# Instead of "households WITHOUT children under 5"
# Find "households where all children are 5 or older"
count(members, m, age_years(m.birthdate) < 5) == 0
```

---

### Error: "Invalid field access"

**Problem**: Field doesn't exist on this model

**Example**: `me.district` when district_id doesn't exist

**Solution**:

1. Check field name spelling
2. Verify field exists in this profile
3. Contact admin to add custom field if needed

---

### No Results (but you expected some)

**Problem**: Query is too restrictive or has a logic error

**Debug Steps**:

1. **Simplify**: Break complex queries into parts

```cel
# Instead of this complex query:
members.exists(m, head(m) and m.gender == "Female" and age_years(m.birthdate) >= 60)

# Test each part separately:
members.exists(m, head(m))  # Any households with a head?
members.exists(m, m.gender == "Female")  # Any with female members?
members.exists(m, age_years(m.birthdate) >= 60)  # Any with elderly?
```

2. **Check for ended members**: Remember `members` only shows active by default!

```cel
# If you expect to see ended members, include them:
members.exists(m, m._link.is_ended or age_years(m.birthdate) < 5)
```

---

### Getting Unexpected Results

**Problem**: Query logic doesn't match your intent

**Common Mistakes**:

**1. AND vs OR confusion**

```cel
# ❌ WRONG: This means "female AND male" (impossible!)
members.exists(m, m.gender == "Female" and m.gender == "Male")

# ✅ RIGHT: This means "female OR male"
members.exists(m, m.gender == "Female" or m.gender == "Male")
```

**2. Count confusion**

```cel
# ❌ WRONG: "At least one head"
members.exists(m, head(m))

# ✅ RIGHT: "Exactly one head"
count(members, m, head(m)) == 1
```

**3. Active members only**

```cel
# ❌ PROBLEM: Only checks active members
members.exists(m, m.name == "John")

# ✅ SOLUTION: Include ended members if needed
members.exists(m, (m._link.is_ended or true) and m.name == "John")
```

---

## Best Practices

### 1. Start Simple, Then Add Conditions

✅ **Good approach**:

```cel
# Step 1: Find elderly
age_years(me.birthdate) >= 60

# Step 2: Add gender filter
age_years(me.birthdate) >= 60 and me.gender == "Female"

# Step 3: Add phone requirement
age_years(me.birthdate) >= 60 and me.gender == "Female" and me.phone != ""
```

❌ **Bad approach**: Writing the entire complex query at once without testing.

---

### 2. Use Clear, Descriptive Expressions

✅ **Good** (self-documenting):

```cel
members.exists(m, head(m) and age_years(m.birthdate) >= 60)
```

❌ **Bad** (unclear intent):

```cel
members.exists(m, has_role(m, "Head") and m.birthdate <= years_ago(60))
```

---

### 3. Test with Preview Before Using

Always click **"Validate & Preview"** to:

- Check syntax
- Verify logic
- See sample results
- Confirm record count

---

### 4. Document Complex Queries

When creating complex targeting rules:

```
# Program: Elderly Woman-Headed Household Support
# Eligibility: Female head, 60+, with at least one dependent child

members.exists(m, head(m) and m.gender == "Female" and age_years(m.birthdate) >= 60) and
count(members, m, age_years(m.birthdate) < 18) >= 1
```

---

### 5. Be Aware of Active Members Default

When working with Groups profile:

```cel
# ✅ This automatically excludes ended members
members.exists(m, age_years(m.birthdate) < 5)

# 🔧 To include ended members explicitly:
members.exists(m, m._link.is_ended or age_years(m.birthdate) < 5)
```

---

### 6. Use between() for Age Ranges

✅ **Good** (clear and concise):

```cel
between(age_years(me.birthdate), 6, 11)
```

❌ **Bad** (verbose):

```cel
age_years(me.birthdate) >= 6 and age_years(me.birthdate) <= 11
```

---

### 7. Leverage Tags for Custom Categories

Instead of complex field checks:

```cel
# ✅ Good (using tags)
has_tag("Vulnerable")

# ❌ Bad (hardcoding conditions)
age_years(me.birthdate) < 5 or age_years(me.birthdate) >= 60 or has_tag("Disabled") or ...
```

---

### 8. Save Common Queries as Templates

If you use the same eligibility criteria frequently, document them:

**Common Templates**:

```cel
# Young Children (under 5)
age_years(me.birthdate) < 5

# Elderly (60+)
age_years(me.birthdate) >= 60

# Woman-Headed Household
members.exists(m, head(m) and m.gender == "Female")

# Large Family (5+ members)
count(members, m, true) >= 5

# Has Phone Number
me.phone != ""
```

---

## Next Steps

### Want to Learn More?

- **Configuration**: See [README.md](./README.md) for YAML configuration
- **Technical Details**: See [CODE_REVIEW_REPORT.md](./CODE_REVIEW_REPORT.md)
- **Implementation**: See [YAML_CONFIGURATION_IMPLEMENTATION.md](./YAML_CONFIGURATION_IMPLEMENTATION.md)
- **External Metrics**: See [EXTERNAL_METRICS_SPEC_V2.md](./EXTERNAL_METRICS_SPEC_V2.md)

### Need Help?

- Check the [Troubleshooting](#troubleshooting) section
- Review [Real-World Examples](#real-world-examples)
- Contact your system administrator
- File issues at your project's issue tracker

---

## Appendix: Quick Reference

### Operators

| Operator | Meaning                | Example                              |
| -------- | ---------------------- | ------------------------------------ |
| `==`     | Equal                  | `me.gender == "Female"`              |
| `!=`     | Not equal              | `me.phone != ""`                     |
| `<`      | Less than              | `age_years(me.birthdate) < 5`        |
| `<=`     | Less than or equal     | `me.birthdate <= date("2020-01-01")` |
| `>`      | Greater than           | `age_years(me.birthdate) > 60`       |
| `>=`     | Greater than or equal  | `age_years(me.birthdate) >= 18`      |
| `and`    | Both conditions        | `condition1 and condition2`          |
| `or`     | Either condition       | `condition1 or condition2`           |
| `not`    | Negation (simple only) | `not (me.id == 123)`                 |

### Common Patterns

```cel
# Age checks
age_years(me.birthdate) < 5              # Under 5
age_years(me.birthdate) >= 60            # 60 or older
between(age_years(me.birthdate), 6, 11)  # Age range

# Text matching
startswith(me.name, "Ahmad")             # Name starts with
contains(me.name, "Ali")                 # Name contains

# Tags
has_tag("Pregnant")                      # Has specific tag

# Membership (Groups profile)
members.exists(m, head(m))                        # Has head
count(members, m, head(m)) == 1                   # Exactly one head
members.exists(m, age_years(m.birthdate) < 5)    # Has child under 5
count(members, m, true) >= 5                      # 5+ members

# Program checks (Individuals profile)
enrollments.exists(e, e.program == program("Cash Transfer"))  # Enrolled in program
```

---

**End of User Guide** | Version 1.0 | October 2025
