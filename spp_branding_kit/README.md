# OpenSPP Branding Kit for Odoo 17

A comprehensive debranding and rebranding module for Odoo 17 that replaces all Odoo branding with OpenSPP
branding throughout the platform.

## Features

### Complete Debranding

- ✅ Removes "Powered by Odoo" messages from all interfaces
- ✅ Eliminates Odoo.com links and references
- ✅ Disables telemetry and external communications
- ✅ Removes enterprise promotion elements
- ✅ Hides app store and theme store links

### Custom Branding

- 🎨 Custom website footer with OpenSPP information
- 🎨 Branded login page with OpenSPP styling
- 🎨 Professional PDF reports with OpenSPP headers/footers
- 🎨 Customized backend interface with OpenSPP colors
- 🎨 Modified user menu with OpenSPP links
- 🎨 Custom email signatures and templates

### Technical Features

- 🔧 Follows Odoo best practices for upgrade safety
- 🔧 Uses proper inheritance mechanisms
- 🔧 Compatible with OCA debranding modules
- 🔧 Modular architecture for easy customization
- 🔧 No core code modifications

## Requirements

- Odoo 17 Community Edition
- Python 3.8+
- PostgreSQL 12+

### Recommended OCA Modules

For complete debranding, install these modules from the
[OCA/server-brand](https://github.com/OCA/server-brand) repository:

- `disable_odoo_online` (17.0.1.0.0)
- `portal_odoo_debranding` (17.0.1.0.0)
- `remove_odoo_enterprise` (17.0.1.0.1)

## Installation

### 1. Clone the Module

```bash
cd /path/to/your/custom-addons
git clone [repository-url] openspp_branding_kit
```

### 2. Install OCA Dependencies (Recommended)

```bash
cd /path/to/your/custom-addons
git clone --branch 17.0 https://github.com/OCA/server-brand.git
```

### 3. Update Odoo Configuration

Add the module paths to your `odoo.conf`:

```ini
[options]
addons_path = /path/to/openspp_branding_kit,/path/to/server-brand,/path/to/odoo/addons

# Recommended security settings
list_db = False
```

### 4. Install the Module

1. Restart your Odoo server
2. Go to Apps menu
3. Update Apps List
4. Search for "OpenSPP Branding Kit"
5. Click Install

## Configuration

The module automatically applies all branding changes upon installation. However, you can further customize:

### Company Information

- Navigate to Settings → Companies → Your Company
- Update company logo, address, and contact information

### Website Customization

- Use the website builder to further customize the footer
- Modify colors and styles through the Customize menu

### Email Templates

- Go to Settings → Technical → Email Templates
- Modify the OpenSPP notification templates as needed

### Report Customization

- Navigate to Settings → Technical → Reports
- Adjust paper formats and layouts

## Module Structure

```
openspp_branding_kit/
├── __manifest__.py          # Module metadata
├── __init__.py             # Module initialization
├── controllers/            # HTTP controllers
│   └── main.py            # Custom routes
├── data/                   # Data files
│   ├── debranding_data.xml
│   ├── ir_config_parameter.xml
│   └── res_company_data.xml
├── models/                 # Model overrides
│   ├── ir_http.py
│   └── res_users.py
├── security/              # Access control
│   └── ir.model.access.csv
├── static/                # Static assets
│   ├── description/       # Module description
│   └── src/              # CSS/JS assets
│       ├── js/           # JavaScript files
│       └── scss/         # SCSS stylesheets
└── views/                 # XML templates
    ├── backend_customization.xml
    ├── login_templates.xml
    ├── report_templates.xml
    ├── webclient_templates.xml
    └── website_templates.xml
```

## Customization Guide

### Changing Colors

Edit the SCSS variables in `static/src/scss/backend.scss`:

```scss
$openspp-primary: #2c3e50; // Main brand color
$openspp-secondary: #34495e; // Secondary color
$openspp-accent: #3498db; // Accent color
```

### Modifying Footer Content

Edit `views/website_templates.xml` to change footer text and links.

### Adding Custom Logos

1. Place your logo in `static/description/`
2. Update the path in `data/ir_config_parameter.xml`
3. Reference it in templates

## Troubleshooting

### Module Not Appearing

- Ensure the module path is in `addons_path`
- Check module permissions (should be readable)
- Update apps list with `--update=all` flag

### Branding Not Applied

- Clear browser cache
- Restart Odoo server
- Check for conflicting modules

### OCA Modules Not Working

- Verify you're using the 17.0 branch
- Check module dependencies are satisfied
- Review Odoo logs for errors

## Development

### Running Tests

```bash
./odoo-bin -c odoo.conf -d test_db --test-enable --stop-after-init -i openspp_branding_kit
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Considerations

This module includes security enhancements:

- Disables database manager in web interface
- Blocks telemetry to external servers
- Removes potentially sensitive information from UI
- Implements secure default configurations

## License

This module is licensed under LGPL-3. See LICENSE file for full details.

## Support

- **Website**: [https://openspp.org](https://openspp.org)
- **Documentation**: [https://openspp.org/documentation](https://openspp.org/documentation)
- **GitHub**: [https://github.com/openspp](https://github.com/openspp)
- **Community**: [https://openspp.org/community](https://openspp.org/community)

## Credits

### Authors

- OpenSPP Project Team

### Contributors

- See contributors list on GitHub

### Acknowledgments

- Odoo Community Association (OCA) for debranding modules
- OpenSPP community for testing and feedback

## Changelog

### Version 17.0.1.0.0 (Latest)

- Initial release for Odoo 17
- Complete debranding functionality
- OpenSPP branding implementation
- OCA module compatibility
- Security enhancements

---

© 2025 OpenSPP Project. All rights reserved.
