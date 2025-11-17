# spp_event_spec_loader - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Program Specifications          Event Type Definitions         │
│  ┌──────────────────┐            ┌──────────────────┐           │
│  │ Tree View        │            │ Tree View        │           │
│  │ Form View        │            │ Form View        │           │
│  │ YAML Editor      │            │ Deployment UI    │           │
│  └──────────────────┘            └──────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  spp.program.spec                                      │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ • Parse YAML                                     │  │     │
│  │  │ • Validate syntax                                │  │     │
│  │  │ • Extract metadata                               │  │     │
│  │  │ • Extract event type definitions                 │  │     │
│  │  │ • Manage deployment workflow                     │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  spp.event.type.definition                             │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │ • Store field definitions (JSON)                 │  │     │
│  │  │ • Generate models (ir.model)                     │  │     │
│  │  │ • Generate views (ir.ui.view)                    │  │     │
│  │  │ • Track deployment status                        │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Generated Models (Dynamic)         Base Framework              │
│  ┌──────────────────────────┐      ┌──────────────────────┐     │
│  │ spp.event.education.*    │◄─────┤ spp.event.data       │     │
│  │ spp.event.compliance.*   │      │                      │     │
│  │ spp.event.health.*       │      │ • Event metadata     │     │
│  │ spp.event.custom.*       │      │ • Registrant link    │     │
│  └──────────────────────────┘      │ • State management   │     │
│                                    └──────────────────────┘     │
│  Generated Views (Dynamic)                                      │
│  ┌──────────────────────────┐                                   │
│  │ • Tree views             │                                   │
│  │ • Form views             │                                   │
│  │ • Actions                │                                   │
│  └──────────────────────────┘                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────┐
│ YAML File   │
│ (4Ps spec)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Step 1: Parse & Validate                    │
│ ┌─────────────────────────────────────────┐ │
│ │ yaml.safe_load(yaml_content)            │ │
│ │ ├─ Check syntax                         │ │
│ │ ├─ Validate structure                   │ │
│ │ └─ Extract sections                     │ │
│ └─────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Step 2: Extract Event Types                 │
│ ┌─────────────────────────────────────────┐ │
│ │ _extract_event_types_from_spec()        │ │
│ │                                         │ │
│ │ Source 1: external_systems              │ │
│ │ ├─ system.id + data_contract            │ │
│ │ └─ → spp.event.{domain}.{record_type}   │ │
│ │                                         │ │
│ │ Source 2: compliance.conditions         │ │
│ │ ├─ condition.id + description           │ │
│ │ └─ → spp.event.compliance.{id}          │ │
│ │                                         │ │
│ │ Source 3: event_types                   │ │
│ │ ├─ Custom definitions                   │ │
│ │ └─ → User-specified model name          │ │
│ └─────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Step 3: Create Event Type Definitions       │
│ ┌─────────────────────────────────────────┐ │
│ │ For each extracted event type:          │ │
│ │ ├─ Create spp.event.type.definition     │ │
│ │ ├─ Store field_definitions as JSON      │ │
│ │ ├─ Set source and source_ref            │ │
│ │ └─ Mark as draft                        │ │
│ └─────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Step 4: Deploy Models                       │
│ ┌─────────────────────────────────────────┐ │
│ │ _deploy_model()                         │ │
│ │ ├─ Create ir.model record               │ │
│ │ ├─ Add standard fields (x_name, etc)    │ │
│ │ ├─ Add custom fields from JSON          │ │
│ │ └─ Mark model_deployed = True           │ │
│ └─────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Step 5: Deploy Views                        │
│ ┌─────────────────────────────────────────┐ │
│ │ _deploy_views()                         │ │
│ │ ├─ Generate tree view XML               │ │
│ │ ├─ Generate form view XML               │ │
│ │ ├─ Create ir.ui.view records            │ │
│ │ └─ Mark view_deployed = True            │ │
│ └─────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────┐
│ Step 6: Integration                         │
│ ┌─────────────────────────────────────────┐ │
│ │ • Register with spp.event.data          │ │
│ │ • Available in event wizard             │ │
│ │ • Usable in registrant forms            │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Component Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│                    YAML Specification                            │
│  (Source of Truth - stored in spp.program.spec.yaml_content)     │
└────────┬─────────────────────────────────────────────────────────┘
         │
         │ parses into
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                  Event Type Definitions                          │
│              (spp.event.type.definition)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │
│  │ Education  │  │ Health     │  │ Compliance │  ...             │
│  │ Attendance │  │ Checkup    │  │ Verify     │                  │
│  └────┬───────┘  └────┬───────┘  └────┬───────┘                  │
│       │               │               │                          │
│       └───────────────┼───────────────┘                          │
│                       │                                          │
└───────────────────────┼──────────────────────────────────────────┘
                        │ generates
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Dynamic Models                                │
│  ┌──────────────────────────────────────────────────────┐        │
│  │ ir.model (Odoo Model Registry)                       │        │
│  │  ├─ spp.event.education.attendance                   │        │
│  │  ├─ spp.event.health.checkup                         │        │
│  │  └─ spp.event.compliance.verify                      │        │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐        │
│  │ ir.model.fields (Field Definitions)                  │        │
│  │  ├─ x_attendance_pct (float)                         │        │
│  │  ├─ x_school_id (char)                               │        │
│  │  └─ x_period (char)                                  │        │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐        │
│  │ ir.ui.view (View Definitions)                        │        │
│  │  ├─ Tree views                                       │        │
│  │  └─ Form views                                       │        │
│  └──────────────────────────────────────────────────────┘        │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          │ integrates with
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│              Base Event Data Framework                           │
│                  (spp_event_data)                                │
│  ┌──────────────────────────────────────────────────────┐        │
│  │ spp.event.data                                       │        │
│  │  ├─ model (Many2oneReference)                        │        │
│  │  ├─ res_id (Many2oneReference)                       │        │
│  │  ├─ partner_id (Many2one res.partner)                │        │
│  │  ├─ collection_date                                  │        │
│  │  ├─ state (active/inactive)                          │        │
│  │  └─ ... (other metadata)                             │        │
│  └──────────────────────────────────────────────────────┘        │
│                                                                  │
│  Provides:                                                       │
│  • Event history tracking                                        │
│  • Active/inactive state management                              │
│  • Registrant association                                        │
│  • Creation wizard framework                                     │
└──────────────────────────────────────────────────────────────────┘
```

## Class Diagram

```
┌─────────────────────────────────┐
│    spp.program.spec             │
├─────────────────────────────────┤
│ - name: Char                    │
│ - code: Char                    │
│ - yaml_content: Text            │
│ - spec_data: Text (computed)    │
│ - state: Selection              │
│ - event_type_ids: One2many      │
├─────────────────────────────────┤
│ + action_validate()             │
│ + action_deploy()               │
│ + _extract_event_types()        │
│ + _extract_fields_from_contract()
└─────────────┬───────────────────┘
              │ 1:N
              ▼
┌─────────────────────────────────┐
│  spp.event.type.definition      │
├─────────────────────────────────┤
│ - name: Char                    │
│ - technical_name: Char          │
│ - description: Text             │
│ - program_spec_id: Many2one     │
│ - source: Selection             │
│ - field_definitions: Text(JSON) │
│ - state: Selection              │
│ - model_deployed: Boolean       │
│ - view_deployed: Boolean        │
├─────────────────────────────────┤
│ + action_deploy()               │
│ + _deploy_model()               │
│ + _deploy_views()               │
│ + _generate_tree_view_xml()     │
│ + _generate_form_view_xml()     │
└─────────────┬───────────────────┘
              │ creates
              ▼
┌─────────────────────────────────┐
│      ir.model (Odoo Core)       │
├─────────────────────────────────┤
│ - name: Char                    │
│ - model: Char                   │
│ - state: Selection              │
│ - field_id: One2many            │
└─────────────┬───────────────────┘
              │ 1:N
              ▼
┌─────────────────────────────────┐
│   ir.model.fields (Odoo Core)   │
├─────────────────────────────────┤
│ - name: Char                    │
│ - field_description: Char       │
│ - ttype: Selection              │
│ - state: Selection              │
└─────────────────────────────────┘

         creates          creates
              ▼               ▼
┌──────────────────┐  ┌──────────────────┐
│   ir.ui.view     │  │  ir.actions...   │
│   (Tree/Form)    │  │  (Window)        │
└──────────────────┘  └──────────────────┘
```

## Sequence Diagram: Deploy Event Types

```
User         ProgramSpec      EventTypeDef      IrModel      IrView
 │                │                 │              │           │
 │  Validate      │                 │              │           │
 ├───────────────>│                 │              │           │
 │                │                 │              │           │
 │                │ Parse YAML      │              │           │
 │                ├────────────┐    │              │           │
 │                │            │    │              │           │
 │                │<───────────┘    │              │           │
 │                │                 │              │           │
 │  Deploy        │                 │              │           │
 ├───────────────>│                 │              │           │
 │                │                 │              │           │
 │                │ Extract Events  │              │           │
 │                ├────────────┐    │              │           │
 │                │            │    │              │           │
 │                │<───────────┘    │              │           │
 │                │                 │              │           │
 │                │ Create EventType│              │           │
 │                ├────────────────>│              │           │
 │                │                 │              │           │
 │                │                 │ Deploy       │           │
 │                │                 ├─────────┐    │           │
 │                │                 │         │    │           │
 │                │                 │ Create Model │           │
 │                │                 ├──────────────>           │
 │                │                 │              │           │
 │                │                 │ Create Fields│           │
 │                │                 ├──────────────>           │
 │                │                 │              │           │
 │                │                 │         Create Views     │
 │                │                 ├─────────────────────────>│
 │                │                 │              │           │
 │                │                 │<──────────────────────────
 │                │                 │              │           │
 │                │                 │ Deployed     │           │
 │                │                 ├<────────┘    │           │
 │                │<────────────────│              │           │
 │                │                 │              │           │
 │  Success       │                 │              │           │
 │<───────────────│                 │              │           │
 │                │                 │              │           │
```

## Technology Stack

```
┌─────────────────────────────────────────────┐
│          Frontend Layer                     │
│  • Odoo Web Client (JavaScript)             │
│  • QWeb Templates                           │
│  • ACE Editor (YAML syntax highlighting)    │
└─────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────┐
│       Application Layer                     │
│  • Python 3.8+                              │
│  • Odoo 17 Framework                        │
│  • ORM (Object-Relational Mapping)          │
└─────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────┐
│         Business Logic                      │
│  • PyYAML (YAML parsing)                    │
│  • JSON (field definition storage)          │
│  • XML (view generation)                    │
│  • Dynamic model creation (ir.model)        │
└─────────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────┐
│          Data Layer                         │
│  • PostgreSQL Database                      │
│  • Odoo ORM                                 │
│  • Dynamic table creation                   │
└─────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────┐
│              User Roles                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Admin   │  │Registrar │  │   User   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │            │
└───────┼─────────────┼──────────────┼────────────┘
        │             │              │
        ▼             ▼              ▼
┌─────────────────────────────────────────────────┐
│          Access Control Layer                   │
│  ┌─────────────────────────────────────────┐    │
│  │ ir.model.access (CSV)                   │    │
│  │  ├─ spp_program_spec_admin (CRUD)       │    │
│  │  ├─ spp_program_spec_registrar (R)      │    │
│  │  └─ spp_program_spec_user (R events)    │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ Record Rules (if needed)                │    │
│  │  • Restrict by region                   │    │
│  │  • Restrict by program                  │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## Deployment Architecture

```
Development → Validation → Deployment → Production

┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Write      │   │   Validate   │   │    Deploy    │   │  Production  │
│   YAML       │──>│   Syntax &   │──>│   Models &   │──>│   Event      │
│   Spec       │   │   Structure  │   │   Views      │   │   Tracking   │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
     │                    │                   │                   │
     │                    │                   │                   │
  Version             Metadata            Dynamic              Active
  Control             Extraction          Creation             Usage
```

## Performance Considerations

```
┌─────────────────────────────────────────────────────────┐
│                Performance Profile                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  YAML Parsing:              ~100ms for 500-line spec    │
│  Model Creation:            ~500ms per model            │
│  View Generation:           ~200ms per view             │
│  Total Deployment:          ~2-5 seconds for 5 types    │
│                                                         │
│  Runtime Performance:                                   │
│  • Dynamic models perform like standard models          │
│  • No significant overhead after deployment             │
│  • Views are cached normally                            │
│                                                         │
│  Recommended Limits:                                    │
│  • Event types per program: 10-20                       │
│  • Fields per event type: 10-15                         │
│  • Total dynamic models: < 100                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Extension Points

```
┌─────────────────────────────────────────────────────────┐
│              Module Extension Points                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Custom Field Types                                  │
│     └─ Extend _extract_fields_from_data_contract()      │
│                                                         │
│  2. Custom View Templates                               │
│     └─ Override _generate_form_view_xml()               │
│                                                         │
│  3. Custom Event Sources                                │
│     └─ Extend _extract_event_types_from_spec()          │
│                                                         │
│  4. Post-Deployment Hooks                               │
│     └─ Override action_deploy() in inherited model      │
│                                                         │
│  5. Custom Validation Rules                             │
│     └─ Override action_validate()                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

This architecture enables: ✓ **Separation of Concerns**: YAML specs separate from implementation ✓
**Scalability**: Handle multiple programs independently ✓ **Maintainability**: Update via configuration, not
code ✓ **Flexibility**: Easy to extend and customize ✓ **Traceability**: Full audit trail of deployments
