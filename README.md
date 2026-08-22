# Flask-Cloudscape

> A Python Flask extension that brings the full power of the [AWS Cloudscape Design System](https://cloudscape.design/) into Flask + Jinja2 applications — no React required.

Cloudscape components are compiled into **Web Components** and served as bundled JS + CSS assets. You interact with them through **Jinja macros**, **Python component classes**, or raw `<cloudscape-*>` HTML tags.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Installation & Build](#installation--build)
- [Flask Integration](#flask-integration)
- [Usage Methods](#usage-methods)
  - [Method 1: Jinja Macros](#method-1-jinja-macros-recommended)
  - [Method 2: Python Component Classes](#method-2-python-component-classes)
  - [Method 2.5: Dynamic Jinja Rendering with cs_render](#method-25-dynamic-jinja-rendering-with-cs_render)
  - [Method 3: Raw HTML Tags](#method-3-raw-html-tags)
- [Layout Patterns](#layout-patterns)
- [Component Reference](#component-reference)
- [Asset Helpers](#asset-helpers)
- [Event Handling](#event-handling)
- [Base Templates](#base-templates)
- [Project Structure](#project-structure)
- [Rebuild After Changes](#rebuild-after-changes)

---

## Quick Start

```python
# app_init.py
from flask_cloudscape import Cloudscape

app = Flask(__name__)
cloudscape = Cloudscape(app)
```

```jinja
{# In any Jinja template #}
{% from "cloudscape/_macros.html" import cs_button, cs_alert %}

{{ cs_alert(type="success", header="Welcome", children="Flask-Cloudscape is ready!") }}
{{ cs_button(variant="primary", text="Get Started") }}
```

---

## Installation & Build

### Prerequisites
- Node.js ≥ 18
- npm ≥ 9
- Python ≥ 3.9

### First-Time Setup

```bash
# Build the Cloudscape adapter (from the components/ directory)
cd components/
npm install         # Install JS dependencies
./build.sh          # Compile TS → JS → Bundle into ../flask_cloudscape/static/
```

The build populates the standalone package:
```
flask_cloudscape/static/js/cloudscape-adapter.js   (~970 KB)
flask_cloudscape/static/css/cloudscape-adapter.css  (~1.2 MB)
```

### Quick Rebuild (Bundle Only)

```bash
cd components/
./build.sh --bundle   # Skip TS compilation, just re-bundle
```

---

## Flask Integration

### 1. Add to `sys.path` and import

```python
import sys, os

# Add the workspace root to path (where flask_cloudscape/ lives)
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from flask_cloudscape import Cloudscape
```

### 2. Initialize with your Flask app

```python
# Using init_app pattern
cloudscape = Cloudscape()
cloudscape.init_app(app)

# Or direct initialization
cloudscape = Cloudscape(app)
```

### What this does:
- Registers a `cloudscape` Blueprint that serves JS/CSS from `flask_cloudscape/static/`
- Makes Jinja2 templates from `flask_cloudscape/templates/` available
- Injects `cloudscape_css()`, `cloudscape_js()`, and `cloudscape_assets()` into all templates

---

## Usage Methods

### Method 1: Jinja Macros (Recommended)

Import the macros you need and call them like functions:

```jinja
{% from "cloudscape/_macros.html" import cs_button, cs_alert, cs_container, cs_end_container %}

{{ cs_alert(type="success", header="Saved!", children="Your changes have been saved.") }}

{{ cs_container(header_text="User Profile") }}
  <p>Container content goes here</p>
{{ cs_end_container() }}

{{ cs_button(variant="primary", text="Submit", id="submit-btn") }}
```

**Container-style components** use a start/end pattern:
```jinja
{{ cs_container(header_text="Settings") }}
  {# ... your content ... #}
{{ cs_end_container() }}

{{ cs_modal(header="Confirm", id="my-modal") }}
  <p>Are you sure?</p>
{{ cs_end_modal() }}
```

### Method 2: Python Component Classes

Use in routes to pass pre-rendered components to templates:

```python
from flask_cloudscape.components import Button, Alert, Container, StatusIndicator

@app.route("/dashboard")
def dashboard():
    save_btn = Button(variant="primary", text="Save Changes", id="save-btn")
    status = StatusIndicator(type="success", children="All systems operational")
    alert = Alert(type="info", header="Tip", children="Click save to apply changes.")
    
    return render_template("dashboard.html",
        save_btn=save_btn,
        status=status,
        alert=alert
    )
```

```jinja
{# dashboard.html #}
{{ alert }}
{{ status }}
{{ save_btn }}
```

Python classes auto-convert kwargs to HTML attributes:
- `snake_case` kwargs → `kebab-case` attributes
- `dict` / `list` values → JSON-serialized strings
- `True` → boolean attribute
- `False` / `None` → attribute omitted

All 95+ Cloudscape components are supported dynamically! For example, you can import and use:
`Wizard`, `TopNavigation`, `SideNavigation`, `AppLayout`, `ColumnLayout`, `SegmentedControl`, `ProgressBar`, `CodeEditor`, `S3ResourceSelector`, `Table`, `Cards`, etc.

### Method 2.5: Dynamic Jinja Rendering with `cs_render` (Highly Recommended)

If you don't want to import separate macros or define components in Python routes, you can use the global `cs_render` helper directly in any Jinja template to dynamically render **any** of the 95+ Cloudscape components:

```jinja
{# Render a simple progress bar #}
{{ cs_render("progress_bar", value=75, label="Upload progress") }}

{# Render a complex wizard component #}
{{ cs_render("wizard", id="setup-wizard", steps=[
    {"title": "Choose engine", "description": "Select DB engine"},
    {"title": "Configure details", "description": "Specify database name and credentials"}
]) }}

{# Render with child HTML elements #}
{{ cs_render("container", children="<p>Inside container</p>", header_text="General Settings") }}
```

### Method 3: Raw HTML Tags

For maximum flexibility, use `<cloudscape-*>` tags directly:

```html
<cloudscape-button variant="primary" id="my-btn">Click Me</cloudscape-button>

<cloudscape-alert type="info" header="Note">
  This is a raw Web Component.
</cloudscape-alert>

<cloudscape-select
  id="role-select"
  options='[{"label":"Admin","value":"admin"},{"label":"User","value":"user"}]'
  selected-option='{"label":"Admin","value":"admin"}'
></cloudscape-select>
```

---

## Layout Patterns

To help implement the standard [Cloudscape UX Patterns](https://cloudscape.design/patterns/), the package includes high-level layout macros in `cloudscape/_patterns.html` that automatically combine multiple atomic components.

Import them into your templates:
```jinja
{% from "cloudscape/_patterns.html" import cs_pattern_table_view, cs_pattern_detail_page, cs_pattern_form_page, cs_pattern_dashboard %}
```

### Table View Pattern
A complete table view with a title header, actions, a search/filter input, and pagination.

```jinja
{{ cs_pattern_table_view(
    title="Databases",
    description="Manage your relational database instances.",
    counter="(3)",
    items=[
      {"name": "db-production", "engine": "PostgreSQL 15"},
      {"name": "db-staging", "engine": "PostgreSQL 15"},
      {"name": "db-test", "engine": "SQLite 3"}
    ],
    column_definitions=[
      {"id": "name", "header": "Instance Name"},
      {"id": "engine", "header": "Database Engine"}
    ],
    current_page=1,
    total_pages=1,
    header_actions='<cloudscape-button variant="primary">Launch DB</cloudscape-button>'
) }}
```

### Details Page Pattern
Displays a resource's configuration details inside a structured key-value overview grid.

```jinja
{{ cs_pattern_detail_page(
    title="db-production",
    description="Main application production database.",
    attributes=[
      {"label": "Engine", "value": "PostgreSQL 15.2"},
      {"label": "Size", "value": "db.m5.large"},
      {"label": "Status", "value": '<cloudscape-status-indicator type="success">Available</cloudscape-status-indicator>'},
      {"label": "Endpoint", "value": "<code>prod-db.c123.us-west-2.rds.amazonaws.com</code>"}
    ],
    header_actions='<cloudscape-button>Modify</cloudscape-button>'
) }}
```

### Single Page Form Pattern
Wraps custom inputs inside a standard edit/create form layout with primary and link buttons.

```jinja
{% call cs_pattern_form_page(
    title="Create Database Instance",
    description="Configure RDS instance settings.",
    submit_label="Create",
    cancel_label="Cancel"
) %}
  {{ cs_form_field(label="DB Instance Identifier", description="Must be unique across your AWS account.") }}
    {{ cs_input(placeholder="database-1") }}
  {{ cs_end_form_field() }}
{% endcall %}
```

### Service Dashboard Pattern
Displays summary cards and key metric values.

```jinja
{{ cs_pattern_dashboard(
    title="System Overview",
    description="Realtime service status monitoring dashboard.",
    cards=[
      {"title": "Total Instances", "value": "12", "description": "8 active, 4 stopped"},
      {"title": "Pending Alarms", "value": "0", "description": "No active alerts"},
      {"title": "Monthly Cost", "value": "$420.50", "description": "Estimated RDS + EC2 spend"}
    ]
) }}
```

---

## Component Reference

### Alert
Displays a notification banner.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `type` | str | `"info"`, `"success"`, `"warning"`, `"error"` | Alert variant |
| `header` | str | | Alert title |
| `dismissible` | bool | | Allow dismissal |
| `children` | str | | Body content |

```jinja
{{ cs_alert(type="error", header="Error", children="Something went wrong.") }}
```

---

### Badge
Small label for counts or status.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `color` | str | `"blue"`, `"grey"`, `"green"`, `"red"` | Badge color |
| `children` | str | | Badge text |

```jinja
{{ cs_badge(color="red", children="3") }}
```

---

### Box
Text container with typographic variants.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `variant` | str | `"p"`, `"h1"`–`"h5"`, `"small"`, `"strong"` | Text style |
| `color` | str | `"default"`, `"text-label"`, `"text-body-secondary"` | Color |
| `text_align` | str | `"left"`, `"center"`, `"right"` | Alignment |

```jinja
{{ cs_box(variant="h2", children="Section Title") }}
```

---

### Button
Interactive button with variants.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `variant` | str | `"normal"`, `"primary"`, `"link"`, `"icon"` | Style |
| `text` | str | | Button label |
| `disabled` | bool | | Disable button |
| `loading` | bool | | Show spinner |
| `icon_name` | str | | Cloudscape icon |
| `href` | str | | Makes it a link |
| `id` | str | | DOM ID |

```jinja
{{ cs_button(variant="primary", text="Save", id="save-btn") }}
{{ cs_button(variant="link", text="Cancel") }}
{{ cs_button(variant="primary", text="Processing...", loading=true) }}
```

---

### Checkbox
Checkbox control.

| Parameter | Type | Description |
|-----------|------|-------------|
| `checked` | bool | Checked state |
| `disabled` | bool | Disable |
| `children` | str | Label text |

```jinja
{{ cs_checkbox(children="I agree to the terms", id="terms-chk") }}
```

---

### Container
Content panel with optional header.

| Parameter | Type | Description |
|-----------|------|-------------|
| `header_text` | str | Simple header text |
| `variant` | str | Container variant |

```jinja
{{ cs_container(header_text="Settings") }}
  <p>Content here</p>
{{ cs_end_container() }}
```

---

### ExpandableSection
Collapsible content area.

| Parameter | Type | Description |
|-----------|------|-------------|
| `header_text` | str | Section header |
| `expanded` | bool | Initially expanded |
| `variant` | str | Style variant |

```jinja
{{ cs_expandable_section(header_text="Advanced Options", expanded=false) }}
  <p>Hidden content</p>
{{ cs_end_expandable_section() }}
```

---

### FormField
Wrapper for form controls with label and validation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `label` | str | Field label |
| `description` | str | Help text |
| `error_text` | str | Error message |

```jinja
{{ cs_form_field(label="Email", description="We'll never share your email", error_text="") }}
  {{ cs_input(type="text", placeholder="user@example.com", id="email") }}
{{ cs_end_form_field() }}
```

---

### Header
Page or section heading.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `variant` | str | `"h1"`–`"h5"` | Heading level |
| `description` | str | | Subtitle text |
| `counter` | str | | Counter (e.g. "(10)") |
| `children` | str | | Heading text |

```jinja
{{ cs_header(variant="h1", description="Manage your team", children="Dashboard") }}
```

---

### Icon
Cloudscape icon.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `name` | str | `"settings"`, `"search"`, `"close"`, etc. | Icon name |
| `size` | str | `"small"`, `"medium"`, `"big"`, `"large"` | Size |

```jinja
{{ cs_icon(name="settings", size="medium") }}
```

---

### Input
Text input field.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `value` | str | | Current value |
| `placeholder` | str | | Placeholder |
| `type` | str | `"text"`, `"password"`, `"search"`, `"number"` | Input type |
| `disabled` | bool | | Disable |
| `id` | str | | DOM ID |

```jinja
{{ cs_input(placeholder="Search...", type="search", id="search-input") }}
```

---

### Link
Styled anchor link.

| Parameter | Type | Description |
|-----------|------|-------------|
| `href` | str | URL |
| `external` | bool | Opens in new tab |
| `variant` | str | `"primary"`, `"secondary"`, `"info"` |
| `children` | str | Link text |

```jinja
{{ cs_link(href="https://cloudscape.design", external=true, children="Cloudscape Docs") }}
```

---

### Modal
Dialog overlay.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `header` | str | | Modal title |
| `visible` | bool | | Show/hide |
| `size` | str | `"small"`, `"medium"`, `"large"`, `"max"` | Size |
| `close_label` | str | | Accessible close label |

```jinja
{{ cs_modal(header="Confirm Delete", size="small", id="delete-modal") }}
  <p>This action cannot be undone.</p>
  {{ cs_button(variant="primary", text="Delete", id="confirm-delete") }}
{{ cs_end_modal() }}
```

---

### Pagination
Page navigation control.

| Parameter | Type | Description |
|-----------|------|-------------|
| `current_page_index` | int | Current page (1-based) |
| `pages_count` | int | Total pages |

```jinja
{{ cs_pagination(current_page_index=1, pages_count=10, id="paginator") }}
```

---

### Select
Dropdown selector.

| Parameter | Type | Description |
|-----------|------|-------------|
| `options` | list | `[{"label": str, "value": str}, ...]` |
| `selected_option` | dict | `{"label": str, "value": str}` |
| `placeholder` | str | Placeholder text |

```jinja
{{ cs_select(
    options=[
      {"label": "Option A", "value": "a"},
      {"label": "Option B", "value": "b"}
    ],
    selected_option={"label": "Option A", "value": "a"},
    id="my-select"
) }}
```

---

### SpaceBetween
Layout spacer between children.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `direction` | str | `"vertical"`, `"horizontal"` | Direction |
| `size` | str | `"xxxs"` → `"xxl"` | Gap size |

```jinja
{{ cs_space_between(direction="horizontal", size="m") }}
  {{ cs_button(text="One") }}
  {{ cs_button(text="Two") }}
{{ cs_end_space_between() }}
```

---

### Spinner
Loading indicator.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `size` | str | `"normal"`, `"big"`, `"large"` | Size |

```jinja
{{ cs_spinner(size="large") }}
```

---

### StatusIndicator
Inline status with icon.

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `type` | str | `"success"`, `"error"`, `"warning"`, `"info"`, `"stopped"`, `"pending"`, `"in-progress"`, `"loading"` | Status |
| `children` | str | | Status text |

```jinja
{{ cs_status_indicator(type="success", children="Running") }}
```

---

### Table
Data table.

| Parameter | Type | Description |
|-----------|------|-------------|
| `items` | list | Row data |
| `column_definitions` | list | Column configs |
| `header` | str | Table header |
| `variant` | str | `"container"` or `"borderless"` |

```jinja
{{ cs_table(
    items=[{"name": "Alice", "role": "Admin"}, {"name": "Bob", "role": "User"}],
    column_definitions=[
      {"id": "name", "header": "Name"},
      {"id": "role", "header": "Role"}
    ],
    header="Team Members"
) }}
{{ cs_end_table() }}
```

---

### Tabs
Tabbed navigation.

| Parameter | Type | Description |
|-----------|------|-------------|
| `tabs` | list | `[{"id": str, "label": str, "content": str}]` |
| `active_tab_id` | str | Active tab ID |

```jinja
{{ cs_tabs(
    tabs=[
      {"id": "tab1", "label": "Overview", "content": "<p>Overview content</p>"},
      {"id": "tab2", "label": "Settings", "content": "<p>Settings content</p>"}
    ],
    active_tab_id="tab1"
) }}
```

---

### Toggle
On/off switch.

| Parameter | Type | Description |
|-----------|------|-------------|
| `checked` | bool | Toggle state |
| `disabled` | bool | Disable |
| `children` | str | Label text |

```jinja
{{ cs_toggle(children="Enable notifications", id="notif-toggle") }}
```

---

## Asset Helpers

After initializing the extension, these functions are available in **all** Jinja templates:

| Function | Output |
|----------|--------|
| `{{ cloudscape_css() }}` | `<link>` tag for the CSS bundle |
| `{{ cloudscape_js() }}` | `<script>` tag for the JS bundle |
| `{{ cloudscape_assets() }}` | Both CSS and JS tags |

---

## Event Handling

Cloudscape components dispatch standard DOM `CustomEvent`s. Listen for them with `addEventListener`:

```javascript
// Button click
document.getElementById('my-btn').addEventListener('click', (e) => {
  console.log('Button clicked!');
});

// Input change
document.getElementById('my-input').addEventListener('change', (e) => {
  console.log('New value:', e.detail.value);
});

// Select change
document.getElementById('my-select').addEventListener('change', (e) => {
  const option = e.detail.selectedOption;
  console.log('Selected:', option.label);
  // Update the attribute to re-render
  e.target.setAttribute('selected-option', JSON.stringify(option));
});

// Modal dismiss
document.getElementById('my-modal').addEventListener('dismiss', () => {
  document.getElementById('my-modal').removeAttribute('visible');
});

// Toggle change
document.getElementById('my-toggle').addEventListener('change', (e) => {
  console.log('Toggled:', e.detail.checked);
});
```

### Available Events

| Event | Components | `e.detail` |
|-------|-----------|------------|
| `click` | Button, Link | — |
| `change` | Input, Select, Checkbox, Toggle | `{value}`, `{selectedOption}`, `{checked}` |
| `dismiss` | Alert, Modal | — |
| `input` | Input, Textarea | `{value}` |
| `toggle` | ExpandableSection, Toggle | `{checked}` |
| `navigate` | Pagination, Link | `{currentPageIndex}` |
| `tabchange` | Tabs | `{activeTabId}` |

---

## Base Templates

### Option A: Extend the Cloudscape base

```jinja
{% extends "cloudscape/_base.html" %}

{% block title %}My Page{% endblock %}

{% block content %}
  {# Your Cloudscape content here #}
{% endblock %}
```

### Option B: Include assets in your existing base

```jinja
{# In your baseline.html or any template #}
{% block cloudscape_head %}
  {{ cloudscape_css() }}
{% endblock %}

{% block cloudscape_js %}
  {{ cloudscape_js() }}
{% endblock %}
```

### Option C: One-liner in any template

```jinja
{{ cloudscape_assets() }}
```

---

## Project Structure

```
code/                                   # Workspace root
├── flask_cloudscape/                   # ★ Standalone Python package
│   ├── __init__.py                     # Flask extension (Cloudscape class)
│   ├── components.py                   # Python component classes (24 components)
│   ├── README.md                       # ← You are here
│   ├── static/
│   │   ├── js/cloudscape-adapter.js    # Bundled JS (React + Cloudscape + adapter)
│   │   └── css/cloudscape-adapter.css  # Bundled CSS (design tokens + styles)
│   └── templates/cloudscape/
│       ├── _base.html                  # Base template with auto-loaded assets
│       └── _macros.html                # Jinja macros for all components
│
├── components/                         # Cloudscape React source (upstream)
│   ├── adapter.js                      # Web Component wrapper (React → Custom Elements)
│   ├── esbuild.config.mjs              # esbuild bundler configuration
│   ├── build.sh                        # One-command build script
│   ├── src/                            # Cloudscape React source
│   ├── lib/                            # Compiled React components
│   └── package.json
│
└── flask-app/                          # Flask application
    └── src/
        ├── app_init.py                 # Registers Cloudscape extension
        └── templates/
```

> **Key insight**: `flask_cloudscape/` is completely independent of `components/`.
> It only needs `components/` when **rebuilding** the JS/CSS bundles.
> At runtime, it's a self-contained Python package.

---

## Rebuild After Changes

If you modify `adapter.js` or update the Cloudscape source:

```bash
cd components/

# Full rebuild (recompile TypeScript + bundle)
./build.sh

# Quick rebuild (bundle only — use after editing adapter.js)
./build.sh --bundle
```

The build outputs to both:
- `../flask_cloudscape/static/` (standalone package assets)
- `../flask-app/src/static/` (backward compatibility)

---

## License

Cloudscape Design System is released under the [Apache 2.0 License](LICENSE).
