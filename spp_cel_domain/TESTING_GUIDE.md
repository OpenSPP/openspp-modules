# Testing Guide for CEL Domain

**Date**: 2025-10-01 **Purpose**: Document proper patterns for writing tests in the CEL Domain module

---

## Key Patterns for Test Data Creation

### 1. Gender Field (Many2One to gender.type)

**❌ WRONG** (Direct string assignment):

```python
Partner.create({
    "name": "Sarah",
    "gender": "Female",  # ERROR: invalid input syntax for type integer
})
```

**✅ CORRECT** (Many2One ID assignment):

```python
def setUp(self):
    super().setUp()

    # Get or create gender records
    Gender = self.env["gender.type"]

    self.gender_female = Gender.search([("value", "ilike", "female")], limit=1)
    if not self.gender_female:
        self.gender_female = Gender.create({"code": "F", "value": "Female"})

    self.gender_male = Gender.search([("value", "ilike", "male")], limit=1)
    if not self.gender_male:
        self.gender_male = Gender.create({"code": "M", "value": "Male"})

# Then use the ID in partner creation
Partner.create({
    "name": "Sarah",
    "gender": self.gender_female.id,  # ✅ Use .id
})
```

---

### 2. Membership Kind (Many2One to g2p.group.membership.kind)

**Pattern**:

```python
def setUp(self):
    # Try to use existing data reference
    try:
        self.kind_head = self.env.ref("g2p_registry_membership.group_membership_kind_head")
    except Exception:
        # Create if doesn't exist
        self.kind_head = self.env["g2p.group.membership.kind"].create({
            "name": "Head",
            "is_unique": True,
        })

    # Create other kinds as needed
    self.kind_spouse = self.env["g2p.group.membership.kind"].create({"name": "Spouse"})
    self.kind_child = self.env["g2p.group.membership.kind"].create({"name": "Child"})
```

---

### 3. Group Membership (Many2Many for kind)

**Pattern**:

```python
# Create membership with kind
self.env["g2p.group.membership"].create({
    "group": self.household.id,
    "individual": self.person.id,
    "kind": [(4, self.kind_head.id)],  # (4, id) = link to existing record
})

# Without kind
self.env["g2p.group.membership"].create({
    "group": self.household.id,
    "individual": self.child.id,
})
```

**Many2Many Commands**:

- `(4, id)` - Link to existing record
- `(6, 0, [ids])` - Replace all links with new list
- `(5, 0, 0)` - Unlink all

---

### 4. Category Tags (Many2Many)

**Pattern**:

```python
def setUp(self):
    Category = self.env["res.partner.category"]

    self.tag_pregnant = Category.create({"name": "Pregnant"})
    self.tag_disabled = Category.create({"name": "Disabled"})
    self.tag_elderly = Category.create({"name": "Elderly"})

# Assign tags to partner
Partner.create({
    "name": "Maria",
    "category_id": [(6, 0, [self.tag_pregnant.id])],  # ✅ Many2Many assignment
})
```

---

### 5. Database Limits to Avoid

**❌ WRONG** (PostgreSQL integer overflow):

```python
result = self._exec("me.id < 999999999999")  # Too large for integer type!
```

**✅ CORRECT** (Use reasonable values):

```python
result = self._exec("me.id < 99999")  # Within PostgreSQL integer range
```

---

## Complete Example: Creating Test Partners

```python
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.tests import TransactionCase
from odoo.tests.common import tagged

@tagged("post_install", "-at_install", "cel_domain")
class TestIntegrationExample(TransactionCase):

    def setUp(self):
        super().setUp()

        # 1. Set up gender types
        Gender = self.env["gender.type"]
        self.gender_female = Gender.search([("value", "ilike", "female")], limit=1)
        if not self.gender_female:
            self.gender_female = Gender.create({"code": "F", "value": "Female"})

        self.gender_male = Gender.search([("value", "ilike", "male")], limit=1)
        if not self.gender_male:
            self.gender_male = Gender.create({"code": "M", "value": "Male"})

        # 2. Set up membership kinds
        try:
            self.kind_head = self.env.ref("g2p_registry_membership.group_membership_kind_head")
        except Exception:
            self.kind_head = self.env["g2p.group.membership.kind"].create({
                "name": "Head",
                "is_unique": True,
            })

        self.kind_child = self.env["g2p.group.membership.kind"].create({"name": "Child"})

        # 3. Create category tags
        Category = self.env["res.partner.category"]
        self.tag_pregnant = Category.create({"name": "Pregnant"})

        # 4. Create partners
        Partner = self.env["res.partner"]

        # Create household
        self.household = Partner.create({
            "name": "Test Household",
            "is_registrant": True,
            "is_group": True,
        })

        # Create mother
        self.mother = Partner.create({
            "name": "Sarah Johnson",
            "is_registrant": True,
            "is_group": False,
            "birthdate": date.today() - relativedelta(years=32),
            "gender": self.gender_female.id,  # ✅ Use .id
            "phone": "+1234567890",
            "category_id": [(6, 0, [self.tag_pregnant.id])],  # ✅ Many2Many
        })

        # Create child
        self.child = Partner.create({
            "name": "Emma Johnson",
            "is_registrant": True,
            "is_group": False,
            "birthdate": date.today() - relativedelta(years=3),
            "gender": self.gender_female.id,  # ✅ Use .id
        })

        # 5. Create memberships
        Membership = self.env["g2p.group.membership"]

        # Mother as head
        Membership.create({
            "group": self.household.id,
            "individual": self.mother.id,
            "kind": [(4, self.kind_head.id)],  # ✅ Link to kind
            "is_ended": False,
        })

        # Child as member
        Membership.create({
            "group": self.household.id,
            "individual": self.child.id,
            "kind": [(4, self.kind_child.id)],
            "is_ended": False,
        })

    def _exec(self, expr, profile="registry_groups"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

    def test_female_headed_household(self):
        """Test finding female-headed households."""
        expr = 'members.exists(m, head(m) and m.gender == "Female")'
        result = self._exec(expr)

        # Should match our household
        self.assertIn(self.household.id, result.get("ids", []))
        self.assertGreater(result.get("count"), 0)
```

---

## Common Pitfalls

### 1. ❌ Using String for Many2One Fields

```python
# WRONG
{"gender": "Female"}

# RIGHT
{"gender": self.gender_female.id}
```

### 2. ❌ Using Direct List for Many2Many

```python
# WRONG
{"category_id": [tag_id]}

# RIGHT
{"category_id": [(6, 0, [tag_id])]}
```

### 3. ❌ Forgetting to Create Referenced Records First

```python
# WRONG - kind_head doesn't exist yet
Membership.create({"kind": [(4, self.kind_head.id)]})

# RIGHT - create kind_head in setUp() first
```

### 4. ❌ Using Values Outside Database Limits

```python
# WRONG - PostgreSQL integer is limited to 2,147,483,647
{"id": 999999999999}

# RIGHT - use reasonable test values
{"id": 12345}
```

---

## Best Practices

1. **Always use setUp()** to create reference data (genders, kinds, tags)
2. **Search before create** for reference data that might already exist
3. **Use .id** for many2one assignments
4. **Use [(6, 0, [ids])]** for many2many assignments
5. **Use [(4, id)]** for linking to existing many2many records
6. **Create test data in logical order**: reference data → partners → relationships
7. **Use meaningful names** for test data (not "Partner 1", "Partner 2")
8. **Test reasonable data sizes** - avoid huge numbers or massive datasets in unit tests

---

## Reference: OpenSPP/OpenG2P Models

### res.partner

- `is_registrant` (boolean)
- `is_group` (boolean)
- `gender` (many2one to `gender.type`)
- `birthdate` (date)
- `phone` (char)
- `category_id` (many2many to `res.partner.category`)

### g2p.group.membership

- `group` (many2one to `res.partner`)
- `individual` (many2one to `res.partner`)
- `kind` (many2many to `g2p.group.membership.kind`)
- `is_ended` (boolean)
- `start_date` (date)
- `ended_date` (date)

### gender.type

- `code` (char) - e.g., "F", "M"
- `value` (char) - e.g., "Female", "Male"

### g2p.group.membership.kind

- `name` (char) - e.g., "Head", "Spouse", "Child"
- `is_unique` (boolean)

---

## See Also

- Existing test file: `test_examples_groups_members.py` (good reference)
- Odoo documentation: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html

---

**Last Updated**: October 1, 2025
