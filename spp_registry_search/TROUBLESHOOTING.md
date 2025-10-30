# Partner Custom Search - Troubleshooting Guide

## Common Issues and Solutions

### 1. RPC_ERROR: Odoo Server Error (FIXED)

**Problem:** Getting "RPC_ERROR: Odoo Server Error" in the console when searching, and no results appear even though records exist.

**Cause:** The Python `search_by_field` method was returning a recordset object instead of a list of IDs, which caused a serialization error when sending data to the frontend.

**Solution:** ✅ FIXED - The method now returns `self.search(domain).ids` instead of `self.search(domain)`.

**Code Change:**
```python
# BEFORE (Incorrect)
def search_by_field(self, field_name, search_value):
    ...
    return self.search(domain)  # ❌ Returns recordset

# AFTER (Correct)
def search_by_field(self, field_name, search_value):
    ...
    return self.search(domain).ids  # ✅ Returns list of IDs
```

---

### 2. No Search Fields in Dropdown

**Problem:** The search field dropdown is empty or shows no options.

**Possible Causes:**
1. No search field configurations created
2. All search fields are inactive
3. Default data not loaded

**Solutions:**

**A. Check if default data is loaded:**
```bash
# Upgrade the module with demo data
odoo-bin -u spp_base_common -d your_database
```

**B. Manually create search field configurations:**
1. Go to **Settings → Administration → Partner Search Fields**
2. Click **Create**
3. Add at least one field (e.g., Name, Email, Phone)
4. Ensure **Active** is checked

**C. Check via Python shell:**
```python
# In Odoo shell
search_fields = env['spp.partner.search.field'].search([('active', '=', True)])
print(f"Found {len(search_fields)} active search fields")
for field in search_fields:
    print(f"- {field.name}: {field.field_name}")
```

---

### 3. Field Not Appearing in Results

**Problem:** Searched field doesn't show in results even though it's configured.

**Solution:** The results display specific fields only. To add more fields:

**Edit:** `static/src/js/partner_search_view.js`
```javascript
// Line 67-71: Add your field here
this.state.results = await this.orm.searchRead(
    "res.partner",
    [["id", "in", results]],
    ["name", "email", "phone", "mobile", "city", "country_id", "YOUR_FIELD"]  // Add here
);
```

**Edit:** `static/src/xml/partner_search_view.xml`
```xml
<!-- Add a new column in the table -->
<th>Your Field Label</th>

<!-- Add the data cell in tbody -->
<td>
    <t t-esc="partner.your_field or '-'" />
</td>
```

---

### 4. Search Returns No Results (Even Though Records Exist)

**Problem:** Search returns no results even when you know matching records exist.

**Possible Causes:**

**A. Field not configured:**
```python
# Check if field is configured
field_config = env['spp.partner.search.field'].search([
    ('field_name', '=', 'name'),  # Replace with your field
    ('active', '=', True)
])
if not field_config:
    print("Field is not configured!")
```

**B. Field is inactive:**
1. Go to **Settings → Administration → Partner Search Fields**
2. Remove the "Active" filter in the search bar
3. Find your field and activate it

**C. Wrong search value format:**
- For numeric fields: Use exact numbers (e.g., `42`)
- For dates: Use format `YYYY-MM-DD` (e.g., `2025-10-30`)
- For text: Partial matching works (e.g., "john" finds "John Doe")

**D. No access rights:**
```python
# Check if you can read partners
partners = env['res.partner'].search([], limit=1)
if not partners:
    print("No partner access or no partners in database")
```

---

### 5. Permission Denied Errors

**Problem:** "Access Denied" or permission errors when trying to search or configure fields.

**Solution:** Check your security groups:

**For End Users (Searching):**
- Need: `read_registry` group or higher
- Path: Settings → Users & Companies → Users → Select user → Access Rights tab

**For Configuration:**
- Need: `write_registry` or `base.group_system` (Admin)
- Path: Same as above

**Check via Python:**
```python
# Check current user groups
user = env.user
groups = user.groups_id.mapped('name')
print("Your groups:", groups)
```

---

### 6. JavaScript Console Errors

**Problem:** JavaScript errors in browser console.

**Common Errors:**

**A. "Cannot read property of undefined"**
```javascript
// Check if results exist before accessing
if (results && results.length > 0) {
    // Safe to access
}
```

**B. "orm.call is not a function"**
- Clear browser cache
- Restart Odoo server
- Check that assets are loaded: `odoo-bin -u spp_base_common`

**C. Template not found**
- Ensure XML template is loaded in `__manifest__.py`
- Check template name matches: `spp_base_common.PartnerSearchAction`

---

### 7. Search Results Not Updating

**Problem:** Results don't update after clicking Search.

**Solutions:**

**A. Clear browser cache:**
```bash
# Clear Odoo assets
odoo-bin -u spp_base_common -d your_database --dev=all
```

**B. Check browser console for errors**
- Press F12 → Console tab
- Look for red error messages

**C. Verify JavaScript is loaded:**
```javascript
// In browser console
odoo.__DEBUG__.services["@web/core/registry"].category("actions").getAll()
// Should show "partner_search_action"
```

---

### 8. Search Field Configuration Not Saving

**Problem:** Cannot save new search field configurations.

**Possible Causes:**

**A. Missing field_id:**
- The field_id is no longer required, but should be set
- Select a valid partner field from the dropdown

**B. Duplicate field:**
- Each field can only be configured once per company
- Delete the existing configuration or use a different field

**C. Invalid field type:**
- Only certain field types are supported
- Check the model's `_check_field_type` constraint

---

### 9. Searching by Many2one Fields Not Working

**Problem:** Searching by relational fields (e.g., country) doesn't work.

**Explanation:** Many2one searches use the related record's name:

```python
# Correct search
domain = [(field_name + ".name", "ilike", search_value)]

# Example: Searching country by name
search_value = "USA"
# Searches: [("country_id.name", "ilike", "USA")]
```

**Tip:** Type the name of the related record, not its ID.

---

### 10. Module Won't Upgrade

**Problem:** Module fails to upgrade with errors.

**Solutions:**

**A. Check dependencies:**
```bash
# Ensure dependencies are installed
odoo-bin -u spp_base_common,base,g2p_registry_base -d your_database
```

**B. Check for SQL errors:**
```bash
# Look in Odoo logs for detailed error messages
tail -f /var/log/odoo/odoo-server.log
```

**C. Rebuild assets:**
```bash
# Force asset rebuild
odoo-bin -u spp_base_common -d your_database --dev=all
```

---

## Debugging Tools

### Python Shell Commands

```bash
# Access Odoo shell
odoo-bin shell -d your_database
```

```python
# Test search functionality
env['res.partner'].search_by_field('name', 'test')

# Check search fields
fields = env['spp.partner.search.field'].search([])
for f in fields:
    print(f"{f.name}: {f.field_name} (Active: {f.active})")

# Test get_searchable_fields
searchable = env['res.partner'].get_searchable_fields()
print(searchable)

# Create test search field
env['spp.partner.search.field'].create({
    'name': 'Test Field',
    'field_id': env.ref('base.field_res_partner__name').id,
    'active': True,
    'sequence': 100,
})
```

### Browser Console Commands

```javascript
// Check if action is registered
odoo.__DEBUG__.services["@web/core/registry"].category("actions").get("partner_search_action")

// Test ORM call directly
const orm = odoo.__DEBUG__.services["web.orm"];
await orm.call("res.partner", "get_searchable_fields", [])

// Test search
await orm.call("res.partner", "search_by_field", ["name", "test"])
```

---

## Performance Optimization

### For Large Databases

If you have thousands of partners and search is slow:

1. **Add database indexes:**
```sql
-- Add index on frequently searched fields
CREATE INDEX idx_partner_name ON res_partner(name);
CREATE INDEX idx_partner_email ON res_partner(email);
```

2. **Limit search fields:**
- Only activate fields that are commonly searched
- Deactivate rarely used fields

3. **Add pagination:**
- Modify JavaScript to load results in batches
- Use `limit` and `offset` in search

---

## Getting Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Check browser console for errors (F12)
3. ✅ Check Odoo server logs
4. ✅ Verify module is upgraded: `odoo-bin -u spp_base_common`
5. ✅ Try in a different browser
6. ✅ Test with admin user

### What to Include When Reporting Issues

```
1. Odoo version: 17.0
2. Module version: 17.0.1.3.0
3. Error message: (full error from console/logs)
4. Steps to reproduce:
   - Go to Registry → Partner Search
   - Select field: Name
   - Enter value: test
   - Click Search
   - Error occurs
5. Browser: Chrome/Firefox/Safari (version)
6. User role: Admin/Read Registry/Write Registry
```

---

## Logs Location

**Odoo Server Logs:**
- Linux: `/var/log/odoo/odoo-server.log`
- Docker: `docker logs <container_name>`
- Development: Terminal output

**Browser Console:**
- Press F12 → Console tab

**Odoo Debug Mode:**
```
# Add to URL
?debug=1

# Enable developer mode
Settings → Activate developer mode
```

---

## Quick Fixes Checklist

When something isn't working, try these in order:

- [ ] Refresh the browser page (Ctrl+F5 / Cmd+Shift+R)
- [ ] Clear browser cache
- [ ] Restart Odoo server
- [ ] Upgrade the module: `odoo-bin -u spp_base_common`
- [ ] Check user permissions
- [ ] Check browser console for errors
- [ ] Check Odoo logs for errors
- [ ] Test with admin user
- [ ] Test in incognito/private window
- [ ] Rebuild assets: `--dev=all` flag

---

**Last Updated:** October 30, 2025  
**Module Version:** 17.0.1.3.0

