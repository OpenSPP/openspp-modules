# spp_event_spec_loader - User Interface Guide

## New Program Specification Form

### Header Actions

```
┌─────────────────────────────────────────────────────────────────┐
│ ○ Program Specification                               [×] [−] [□] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Validate] [Deploy Event Types] [Reset to Draft] [Export YAML] │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Draft     Validated     Deployed     Error                     │
│    ●                                                            │
└─────────────────────────────────────────────────────────────────┘
```

**Available Actions by State:**

| State     | Validate | Deploy | Reset | Export |
| --------- | -------- | ------ | ----- | ------ |
| Draft     | ✅       | ❌     | ❌    | ✅     |
| Validated | ❌       | ✅     | ✅    | ✅     |
| Deployed  | ❌       | ✅     | ✅    | ✅     |
| Error     | ✅       | ❌     | ✅    | ✅     |

**Available Actions by State:**

| State     | Validate | Deploy | Reset | Export |
| --------- | -------- | ------ | ----- | ------ |
| Draft     | ✅       | ❌     | ❌    | ✅     |
| Validated | ❌       | ✅     | ✅    | ✅     |
| Deployed  | ❌       | ✅     | ✅    | ✅     |
| Error     | ✅       | ❌     | ✅    | ✅     |

---

## Tab 1: YAML Specification (with Integrated Upload)

```
┌─────────────────────────────────────────────────────────────────┐
│  [YAML Specification] Program Metadata  Parsed Data  Errors     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Upload YAML File                                                │
│  [Choose File] No file chosen                                    │
│                                                                  │
│  ──────────────────── YAML Content ────────────────────────     │
│                                                                  │
│ 1  program:                                                      │
│ 2    name: "Pantawid Pamilyang Pilipino Program (4Ps)"         │
│ 3    objectives:                                                 │
│ 4      - "Reduce poverty by investing in children's health"     │
│ 5      - "Increase school enrollment and attendance"            │
│ 6    currency: "PHP"                                            │
│ 7    localization:                                              │
│ 8      languages: ["fil", "en"]                                 │
│ 9    implementing_agencies: ["DSWD", "DepEd", "DOH"]           │
│10                                                                │
│11  external_systems:                                            │
│12    - id: "DepEd"                                              │
│13      role: "evidence_provider"                                │
│14      domain: "education"                                       │
│15      data_contract:                                           │
│   ...                                                            │
│                                                                  │
│                                           [Syntax: YAML] [▼]    │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- ✅ File upload at top of page
- ✅ Full-width YAML editor (uses entire page width)
- ✅ Syntax highlighting (YAML mode)
- ✅ Line numbers
- ✅ Auto-indent
- ✅ Search/replace
- ✅ Auto-populated from uploaded file
- ✅ Can still manually edit after upload

---

## Tab 2: Program Metadata (Auto-extracted)

```
┌─────────────────────────────────────────────────────────────────┐
│  YAML Specification  [Program Metadata]  Parsed Data  Errors    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Program Objectives                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ • Reduce poverty by investing in children's health,        │ │
│  │   nutrition, and education                                 │ │
│  │ • Increase school enrollment and attendance                │ │
│  │ • Improve maternal/child health                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Implementing Agencies                                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DSWD (lead), DepEd, DOH, LGUs                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Currency            Languages                                   │
│  PHP                 fil, en                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Auto-extracted from YAML:**

- ✅ Objectives
- ✅ Implementing agencies
- ✅ Currency
- ✅ Languages
- ✅ Coverage information

---

## Tab 3: Parsed Data (JSON View - Full Width)

```
┌─────────────────────────────────────────────────────────────────┐
│  YAML Specification  Program Metadata  [Parsed Data]  Errors    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 1  {                                                             │
│ 2    "program": {                                                │
│ 3      "name": "Pantawid Pamilyang Pilipino Program (4Ps)",    │
│ 4      "objectives": [                                           │
│ 5        "Reduce poverty...",                                    │
│ 6        "Increase school enrollment..."                         │
│ 7      ],                                                        │
│ 8      "currency": "PHP",                                        │
│ 9      "localization": {                                         │
│10        "languages": ["fil", "en"]                              │
│11      }                                                         │
│12    },                                                          │
│13    "external_systems": [                                       │
│14      {                                                         │
│15        "id": "DepEd",                                          │
│   ...                                                            │
│                                                                  │
│  ← Full width JSON viewer, uses entire available space →        │
│                                                                  │
│                                           [Syntax: JSON] [▼]     │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**

- ✅ Full-width JSON viewer (uses entire page width)
- ✅ JSON representation of parsed YAML
- ✅ Syntax highlighting
- ✅ Formatted/indented
- ✅ Read-only
- ✅ Useful for debugging
- ✅ Better visibility for complex nested structures

---

## Smart Buttons

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│     ╔═══════════════╗                                           │
│     ║               ║                                           │
│     ║      7        ║                                           │
│     ║  Event Types  ║                                           │
│     ║               ║                                           │
│     ╚═══════════════╝                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Click to:**

- View all generated event types
- See deployment status
- Access event type definitions

---

## Workflow Visualization

### Upload Workflow

```
┌──────────────┐
│  User clicks │
│ "Choose File"│
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Select YAML file │
│ (4ps_program.yaml)│
└──────┬───────────┘
       │
       ▼
┌─────────────────────┐
│ File is uploaded    │
│ @api.onchange fires │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────────┐
│ Binary decoded to UTF-8   │
│ yaml_content populated    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ User sees content in      │
│ "YAML Specification" tab  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────┐
│ Click "Validate"     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Metadata extracted   │
│ Event types found    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Click "Deploy"       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Models created       │
│ Views generated      │
│ Ready to use! ✓      │
└──────────────────────┘
```

### Export Workflow

```
┌──────────────────┐
│ User has deployed│
│  specification   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Click "Export    │
│      YAML"       │
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│ yaml_content encoded │
│ to binary            │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Download link created│
│ Browser downloads    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ File saved as        │
│ {code}.yaml          │
└──────────────────────┘
```

---

## Error States

### Invalid File Format

```
╔════════════════════════════════════╗
║ ⚠ File Read Error                 ║
╠════════════════════════════════════╣
║                                    ║
║ Could not read the uploaded file.  ║
║ Please ensure it's a valid text    ║
║ file.                              ║
║                                    ║
║ Error: 'utf-8' codec can't decode ║
║                                    ║
║              [OK]                  ║
╚════════════════════════════════════╝
```

### Invalid YAML Syntax

```
╔════════════════════════════════════╗
║ ⚠ Validation Error                ║
╠════════════════════════════════════╣
║                                    ║
║ Invalid YAML syntax:               ║
║                                    ║
║ while parsing a block mapping      ║
║ in "<unicode string>", line 5,     ║
║ column 1:                          ║
║   external_systems                 ║
║   ^                                ║
║                                    ║
║              [OK]                  ║
╚════════════════════════════════════╝
```

### No Content Provided

```
╔════════════════════════════════════╗
║ ⚠ Validation Error                ║
╠════════════════════════════════════╣
║                                    ║
║ Please provide YAML content        ║
║ either by uploading a file or      ║
║ entering it manually.              ║
║                                    ║
║              [OK]                  ║
╚════════════════════════════════════╝
```

---

## Mobile/Responsive View

The interface adapts for smaller screens:

```
┌──────────────────────────┐
│ ☰  Program Specification │
├──────────────────────────┤
│                          │
│ Name: 4Ps Program        │
│ Code: 4PS                │
│                          │
│ [Validate]               │
│ [Deploy Event Types]     │
│                          │
│ ▼ Upload YAML            │
│   [Choose File]          │
│                          │
│ ▼ YAML Specification     │
│   (Expandable)           │
│                          │
│ ▼ Program Metadata       │
│   (Expandable)           │
│                          │
│ [View Event Types (7)]   │
│                          │
└──────────────────────────┘
```

---

## Keyboard Shortcuts (in YAML editor)

| Shortcut    | Action                     |
| ----------- | -------------------------- |
| `Ctrl+F`    | Find                       |
| `Ctrl+H`    | Find & Replace             |
| `Ctrl+/`    | Toggle Comment             |
| `Ctrl+S`    | Save (triggers validation) |
| `Tab`       | Indent                     |
| `Shift+Tab` | Unindent                   |

---

## User Tips

### 💡 Tip 1: Quick Upload

Drag and drop is supported! Just drag your `.yaml` file onto the upload button.

### 💡 Tip 2: Edit After Upload

After uploading, you can still manually edit in the "YAML Specification" tab before validating.

### 💡 Tip 3: Export for Backup

Use "Export YAML" regularly to keep backups of your specifications in version control.

### 💡 Tip 4: Use Editor Features

The YAML editor supports search, replace, and syntax highlighting. Use them!

### 💡 Tip 5: Check Parsed Data

Always check the "Parsed Data" tab to ensure your YAML was parsed correctly.

---

## Comparison: Before vs After

### Before (No Upload)

```
1. Copy YAML from file
2. Paste into text area
3. Fix formatting issues
4. Validate
5. Deploy
```

**Time**: ~5-10 minutes **Error Rate**: High (formatting issues)

### After (With Upload)

```
1. Click "Choose File"
2. Select YAML file
3. Validate
4. Deploy
```

**Time**: ~1-2 minutes **Error Rate**: Low (file unchanged)

---

## Accessibility Features

✅ **Keyboard Navigation**: Full keyboard support ✅ **Screen Readers**: Proper ARIA labels ✅ **High
Contrast**: Works in accessibility mode ✅ **Focus Indicators**: Clear focus states ✅ **Error Messages**:
Descriptive and helpful

---

## Browser Compatibility

| Browser | Version | Status             |
| ------- | ------- | ------------------ |
| Chrome  | 90+     | ✅ Fully Supported |
| Firefox | 88+     | ✅ Fully Supported |
| Safari  | 14+     | ✅ Fully Supported |
| Edge    | 90+     | ✅ Fully Supported |

---

This UI guide shows all the new features and improvements for easy file upload and management of YAML program
specifications!
