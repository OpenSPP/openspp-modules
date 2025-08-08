# OpenSPP Development Environment Setup (Bash Script)

This guide explains how to use an automated Bash script to set up a complete OpenSPP development environment on **Ubuntu/Debian**, **Red Hat/Fedora**, or **macOS** systems.

---

## 📦 What This Script Does

The script automates:

- OS detection (Ubuntu/Debian, Red Hat/Fedora, macOS)
- Installation of system dependencies
- Setup of a Python virtual environment
- Installation of PostgreSQL and creation of databases
- Cloning of OpenSPP and Odoo repositories
- Installation of Python and Node.js dependencies
- Configuration of Odoo
- Initialization of test data
- Pre-commit hook setup
- Creation of helper scripts for development

---

## Prerequisites

Before running the setup script, ensure you have:

- A supported operating system:
  - Ubuntu 20.04 or later
  - Debian 10 or later
  - Fedora 36 or later
  - macOS 10.15 or later
  - Windows 10/11 with WSL2 (see [Windows Setup](#windows-setup-using-wsl2))
- Administrative (`sudo`) access
- At least 4GB of RAM
- At least 10GB of free disk space
- A stable internet connection

---

## 🚀 Quick Start

### Linux/macOS/Windows (WSL2)

1.Download the setup script:

```bash
wget https://raw.githubusercontent.com/OpenSPP/openspp-modules/main/setup-dev-env.sh
```

2.Make the setup script executable:

```bash
chmod +x setup-dev-env.sh
```

3.(Optional) Customize the installation by editing the configuration variables at the top of the `setup-dev-env.sh` file.

4.Run the script:

```bash
./setup-dev-env.sh
```

### Windows Setup (Using WSL2)

1.Install WSL2 with a Debian-based distribution like Ubuntu:

```powershell
wsl --install -d Ubuntu-22.04
```

2.Open the Ubuntu terminal and follow the Linux/macOS instructions above.

---

## Customizing the Installation

You can customize the installation by editing the configuration variables at the top of the `setup-dev-env.sh` script before running it. This allows you to change the following settings:

-`PYTHON_VERSION`: The version of Python to use (e.g., `3.10`).
-`POSTGRES_VERSION`: The version of PostgreSQL to use (e.g., `14`).
-`NODE_VERSION`: The version of Node.js to use (e.g., `18`).
-`DB_USER`: The username for the PostgreSQL database (default: your system username).
-`DB_PROMPT`: Whether to prompt before creating the databases (default: `true`).

---

## Script Options

The setup script supports the following options:

-`--branch BRANCH`: Specify the OpenSPP branch to checkout (default: `main`)
-`--python VERSION`: Specify the Python version to use (default: `3.10`)
-`--odoo-version VERSION`: Specify the Odoo version to clone (default: `15.0`)
-`--path PATH`: Set a custom absolute path for the installation (default: `~/openspp-dev`)
-`--help`: Display the help message

**Examples:**

```bash
# Use a specific branch
./setup-dev-env.sh --branch develop

# Use Python 3.11 and Odoo 16.0
./setup-dev-env.sh --python 3.11 --odoo-version 16.0

# Install in a custom directory
./setup-dev-env.sh --path /opt/openspp
```

---

## What Gets Installed

### System Dependencies

-Python 3.10 (default) and development headers
-PostgreSQL 14
-Node.js 18
-Git
-Libraries for image processing, XML, and cryptography

### Python Packages

-Odoo 15.0 requirements
-OpenSPP requirements
-Development tools (`black`, `flake8`, `pre-commit`, `pytest`)

### Directory Structure

The script creates the following directory structure inside your chosen installation path (e.g., `~/openspp-dev`):

```bash
/path/to/openspp-dev/
├── venv/                 # Python virtual environment
├── odoo/                 # Odoo source code
├── openspp-modules/      # OpenSPP modules repository
├── openspp-docs/         # OpenSPP documentation
├── odoo.conf             # Odoo configuration
├── start_openspp.sh      # Helper script to start the server
└── update_openspp.sh     # Helper script to update the environment
```

---

## Post-Installation Steps

### Activate Virtual Environment

Before running any commands, activate the virtual environment:

```bash
source ~/openspp-dev/venv/bin/activate
# If you used a custom path:
# source /your/custom/path/venv/bin/activate
```

### Start the Development Server

Use the helper script to start Odoo:

```bash
~/openspp-dev/start_openspp.sh
```

### Access OpenSPP

-Open your web browser to [http://localhost:8069](http://localhost:8069)
-The script initializes the database, so you can log in with the default credentials (admin/admin) or manage databases from the web interface.

### Install OpenSPP Modules

1.Log in as `admin`.
2.Navigate to **Apps**.
3.In the search bar, remove the default "Apps" filter.
4.Search for `spp` and install the modules you need.

---

## Updating Your Environment

To pull the latest code and update dependencies, run the `update_openspp.sh` script:

```bash
~/openspp-dev/update_openspp.sh
```

This script will:
-Pull the latest changes for Odoo and the OpenSPP modules.
-Install any new Python dependencies.
-Update the installed modules in your development database.

---

## Troubleshooting

### PostgreSQL Connection Error

If Odoo can't connect to the database, ensure the PostgreSQL service is running:

```bash
# On Linux (systemd)
sudo systemctl status postgresql
sudo systemctl restart postgresql

# On Linux (init.d)
sudo /etc/init.d/postgresql status
sudo /etc/init.d/postgresql restart

# On macOS (Homebrew)
brew services list
brew services restart postgresql@14
```

The script creates a PostgreSQL user matching the `DB_USER` variable in the `setup-dev-env.sh` file. If you have a different PostgreSQL setup, you may need to edit `~/openspp-dev/odoo.conf` and adjust the `db_user` and `db_password` settings.

### Module Import Errors

If you see `ModuleNotFoundError`, ensure your virtual environment is active and try reinstalling the dependencies:

```bash
source ~/openspp-dev/venv/bin/activate
pip install -r ~/openspp-dev/odoo/requirements.txt
pip install -r ~/openspp-dev/openspp-modules/requirements.txt
```

### Incorrect Python or Node.js Version

If the `verify_installation` step fails with a version mismatch error, ensure that the correct versions of Python and Node.js are installed and available in your system's PATH. You can check the versions using the following commands:

```bash
python3 --version
node --version
```

If the wrong versions are installed, you may need to uninstall them and reinstall the correct versions. You can also use a version manager like `pyenv` for Python or `nvm` for Node.js to manage multiple versions on your system.

---

## Additional Resources

-[OpenSPP Documentation](https://docs.openspp.org)
-[OpenSPP GitHub Repository](https://github.com/OpenSPP/openspp-modules)
-[Odoo Developer Documentation](https://www.odoo.com/documentation/15.0/developer.html)

---

## Getting Help

-**GitHub Issues:** [OpenSPP Issues](https://github.com/OpenSPP/openspp-modules/issues)
-**Community Forum:** [OpenSPP Community](https://community.openspp.org) (Link to be updated)
-**Discord:** [OpenSPP on Discord](https://discord.gg/openspp) (Link to be updated)
