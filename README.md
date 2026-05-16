# Dynamic View Active

**Toggle `ir.ui.view` and `ir.ui.menu` records directly from your Configuration Settings — no XML or developer mode required.**

---

## Overview

`dynamic_view_active` is a lightweight Odoo 19 technical module that allows developers to **declaratively control the `active` state of views and menu items** through the standard **Settings** interface.

By adding two custom field attributes (`view_metadata` and `menu_metadata`) to any `Boolean` field on `res.config.settings`, you can wire a simple on/off toggle in the UI to enable or disable any `ir.ui.view` or `ir.ui.menu` record by its XML ID — for a single record or a batch at once.

- **Author:** Meqh  
- **GitHub:** [https://github.com/meqhh/dynamic_view_active](https://github.com/meqhh/dynamic_view_active)  
- **Version:** 19.0 (I only tested with Odoo 19.0 and I don't tested with other versions. you could test it and tell me if it works with other versions)
- **License:** Unlicense (Public Domain)  

---

## Features

| Feature | Details |
|---|---|
| Toggle a single view | Point `view_metadata` at one XML ID |
| Toggle multiple views | Pass a list of XML IDs to `view_metadata` |
| Toggle a single menu item | Point `menu_metadata` at one XML ID |
| Toggle multiple menu items | Pass a list of XML IDs to `menu_metadata` |
| Defaults to `True` on first install | On `_register_hook`, any unset parameter is seeded as `'True'` |
| Safe resolution | Uses `raise_if_not_found=False`; invalid XML IDs are silently skipped |
| Standard Settings pattern | Fully compatible with Odoo's `get_values` / `set_values` config cycle |

---

## Installation

1. Copy (or clone) this module into your Odoo addons path:

   ```bash
   git clone https://github.com/meqhh/dynamic_view_active.git /path/to/your/addons/dynamic_view_active
   ```

2. Restart the Odoo server.

3. Go to **Apps → Update Apps List**, then install **Dynamic View Active**.

> **Dependency:** only `base` — no extra modules required.

---

## Usage

### 1. Inherit `res.config.settings` in your own module

```python
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Toggle a single view
    enable_my_custom_view = fields.Boolean(
        string="Show My Custom View",
        config_parameter='my_module.enable_my_custom_view',
        view_metadata='my_module.view_my_custom_form',
    )

    # Toggle multiple views at once
    enable_extra_columns = fields.Boolean(
        string="Enable Extra Columns",
        config_parameter='my_module.enable_extra_columns',
        view_metadata=[
            'my_module.view_extra_col_tree',
            'my_module.view_extra_col_form',
        ],
    )

    # Toggle a single menu item
    show_advanced_menu = fields.Boolean(
        string="Show Advanced Menu",
        config_parameter='my_module.show_advanced_menu',
        menu_metadata='my_module.menu_advanced_section',
    )

    # Toggle multiple menu items at once
    show_reports_menus = fields.Boolean(
        string="Show Report Menus",
        config_parameter='my_module.show_reports_menus',
        menu_metadata=[
            'my_module.menu_report_a',
            'my_module.menu_report_b',
        ],
    )
```

### 2. Expose the field in the Settings view

```xml
<record id="res_config_settings_view_form" model="ir.ui.view">
    <field name="name">res.config.settings.view.form.inherit.my_module</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="base_setup.action_general_configuration"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@id='other_configuration']" position="inside">
            <div class="col-12 col-lg-6 o_setting_box">
                <div class="o_setting_left_pane">
                    <field name="enable_my_custom_view"/>
                </div>
                <div class="o_setting_right_pane">
                    <label for="enable_my_custom_view"/>
                    <div class="text-muted">
                        Activates or deactivates My Custom View.
                    </div>
                </div>
            </div>
        </xpath>
    </field>
</record>
```

### 3. Save Settings

After saving the Settings form, the module will call `_set_view_active` and/or `_set_menuitem_active` automatically, writing the boolean value directly to the `active` field of the resolved records.

---

## How It Works

### Custom Field Attributes

The module registers two custom field parameters via `_valid_field_parameter`:

| Attribute | Type | Accepted Value |
|---|---|---|
| `view_metadata` | `str` or `list[str]` | XML ID(s) of `ir.ui.view` records |
| `menu_metadata` | `str` or `list[str]` | XML ID(s) of `ir.ui.menu` records |

### Lifecycle

```
Server Start
    └── _register_hook()
            └── For each Boolean field with config_parameter or menu_metadata:
                    └── If ir.config_parameter has no value yet → seed 'True'

Settings Page Load
    └── get_values()
            └── Reads ir.config_parameter for each tagged Boolean
            └── Returns {'field_name': True/False, ...}

Settings Save
    └── set_values()
            ├── _set_view_active(value, field)
            │       └── Resolves XML ID(s) → sets ir.ui.view.active = value
            └── _set_menuitem_active(value, field)
                    └── Resolves XML ID(s) → sets ir.ui.menu.active = value
```

---

## File Structure

```
dynamic_view_active/
├── __init__.py
├── __manifest__.py
├── LICENSE
├── models/
│   ├── __init__.py
│   └── res_config.py      # Core logic: ResConfigSettings extension
└── README.md
```

---

## Notes & Best Practices

- **`config_parameter` is required** on every field you declare alongside `view_metadata` or `menu_metadata`. It is used as the key for `ir.config_parameter` to persist the toggle state across server restarts.
- **Default is `True`:** On first install, any parameter that has never been set is automatically initialized to `'True'`, keeping existing views/menus active until explicitly disabled.
- **Invalid XML IDs are skipped silently** (`raise_if_not_found=False`), so a missing XML ID will not crash the settings save.
- **Both attributes can coexist** on a single field — one toggle can simultaneously control a view and a menu item.

---

## License

This project is released into the **public domain** under the [Unlicense](https://unlicense.org). You are free to copy, modify, and distribute it for any purpose without restriction.
