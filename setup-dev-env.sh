#!/bin/bash
# OpenSPP Development Environment Setup Script
# Supports: Ubuntu 20.04+, Debian 10+, macOS 10.15+
#
# This script automates the setup of a complete OpenSPP development environment
# including all dependencies, database configuration, and development tools.

set -e    # Exit on error if any command fails

# Color codes for output to make messages more readable
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Configuration Variables
# -----------------------------------------------------------------------------
# These variables can be customized before running the script.
# Command-line arguments will override these values.

# Core application versions
PYTHON_VERSION="3.10"
POSTGRES_VERSION="14"
NODE_VERSION="18"
ODOO_VERSION="15.0"

# OpenSPP repository branch
OPENSPP_BRANCH="main"

# Installation path
INSTALL_PATH="$HOME/openspp-dev"

# Database settings
DB_USER="$USER"
DB_PASSWORD="" # Leave empty for passwordless access (recommended for local dev)
DB_PROMPT="true" # Set to "false" to disable the database creation prompt

# -----------------------------------------------------------------------------

# Function to print colored informational messages

# Function to print colored informational messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to print colored error messages
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to print colored warning messages
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to detect the operating system and distribution
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown Debian/Ubuntu")
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            DISTRO=$(cat /etc/redhat-release)
        else
            OS="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS $(sw_vers -productVersion)"
    else
        OS="unknown"
    fi

    print_status "Detected OS: $OS ($DISTRO)"
}

# Function to check if a command exists in the system's PATH
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system-level dependencies for Debian/Ubuntu
install_debian_dependencies() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would update package lists with: sudo apt-get update"
        echo "[DRY RUN] Would install debian dependencies"
    else
        print_status "Updating package lists..."
        sudo apt-get update

        print_status "Installing system dependencies for Debian/Ubuntu..."
        sudo apt-get install -y \
            build-essential wget git python3-pip python3-dev python3-venv python3-wheel \
            libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libtiff5-dev libjpeg8-dev \
            libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev \
            libharfbuzz-dev libfribidi-dev libxcb1-dev libpq-dev libssl-dev libffi-dev \
            nodejs npm postgresql-$POSTGRES_VERSION postgresql-client-$POSTGRES_VERSION \
            postgresql-server-dev-$POSTGRES_VERSION
    fi
}

# Function to install system-level dependencies for macOS using Homebrew
install_macos_dependencies() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would install macOS dependencies with Homebrew"
    else
        if ! command_exists brew;
        then
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            eval "$(/opt/homebrew/bin/brew shellenv)" || eval "$(/usr/local/bin/brew shellenv)"
        fi

        print_status "Installing system dependencies for macOS..."
        brew install \
            python@$PYTHON_VERSION postgresql@$POSTGRES_VERSION node@$NODE_VERSION git wget \
            libxml2 libxslt libjpeg libpng freetype openssl

        print_status "Starting PostgreSQL service..."
        brew services start postgresql@$POSTGRES_VERSION || print_warning "PostgreSQL service might already be running or failed to start."
    fi
}

# Function to install system-level dependencies for Red Hat/Fedora
install_redhat_dependencies() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would update package lists with: sudo dnf check-update || sudo yum check-update"
        echo "[DRY RUN] Would install Red Hat/Fedora dependencies"
    else
        print_status "Updating package lists..."
        sudo dnf check-update || sudo yum check-update

        print_status "Installing system dependencies for Red Hat/Fedora..."
        sudo dnf install -y \
            make automake gcc gcc-c++ kernel-devel wget git python3-pip python3-devel python3-venv python3-wheel \
            libxml2-devel libxslt-devel libldap-devel libsasl-devel libtiff-devel libjpeg-devel \
            zlib-devel freetype-devel lcms2-devel libwebp-devel harfbuzz-devel fribidi-devel \
            libxcb-devel postgresql-devel openssl-devel libffi-devel \
            nodejs npm postgresql-server postgresql-contrib
    fi
}


# Function to set up the Python virtual environment for OpenSPP
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    mkdir -p "$INSTALL_PATH"
    cd "$INSTALL_PATH"
    if ! command_exists "python${PYTHON_VERSION}"; then
        print_error "Python executable 'python${PYTHON_VERSION}' not found."
        print_error "Please ensure Python ${PYTHON_VERSION} is installed and available in your PATH."
        exit 1
    fi
    python"${PYTHON_VERSION}" -m venv venv
    source venv/bin/activate
    pip install --upgrade pip wheel setuptools
    print_status "Python virtual environment created and activated at $INSTALL_PATH/venv"
}

# Function to clone OpenSPP and Odoo repositories
clone_repositories() {
    print_status "Cloning Odoo and OpenSPP repositories..."
    cd "$INSTALL_PATH"

    if [ ! -d "odoo" ]; then
        print_status "Cloning Odoo ($ODOO_VERSION branch)..."
        git clone --depth 1 --branch "$ODOO_VERSION" https://github.com/odoo/odoo.git
    else
        print_warning "odoo directory already exists, skipping clone. Please update manually if needed."
    fi

    if [ ! -d "openspp-modules" ]; then
        print_status "Cloning OpenSPP modules ($OPENSPP_BRANCH branch)..."
        git clone --depth 1 --branch "$OPENSPP_BRANCH" https://github.com/OpenSPP/openspp-modules.git
    else
        print_warning "openspp-modules directory already exists, skipping clone. Please update manually if needed."
    fi

    if [ ! -d "openspp-docs" ]; then
        print_status "Cloning OpenSPP documentation..."
        git clone --depth 1 https://github.com/OpenSPP/openspp-docs.git
    else
        print_warning "openspp-docs directory already exists, skipping clone. Please update manually if needed."
    fi
}

# Function to install Python dependencies from requirements files
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    source "$INSTALL_PATH/venv/bin/activate"

    print_status "Installing Odoo requirements..."
    pip install -r "$INSTALL_PATH/odoo/requirements.txt"

    if [ -f "$INSTALL_PATH/openspp-modules/requirements.txt" ]; then
        print_status "Installing OpenSPP modules requirements..."
        pip install -r "$INSTALL_PATH/openspp-modules/requirements.txt"
    else
        print_warning "No requirements.txt found in openspp-modules, skipping specific OpenSPP Python dependencies."
    fi

    print_status "Installing Python development tools (pre-commit, black, flake8, etc.)..."
    pip install pre-commit black flake8 pylint pytest coverage
}

# Function to set up PostgreSQL database and users
setup_database() {
    print_status "Setting up PostgreSQL database and user..."

    if [ "$DB_PROMPT" == "true" ]; then
        read -p "This script will create the databases 'openspp_dev' and 'openspp_test'. Are you sure you want to continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]
        then
            print_warning "Database setup skipped."
            return
        fi
    fi

    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1;
    then
        print_status "Creating PostgreSQL user '$DB_USER'..."
        if [ -z "$DB_PASSWORD" ]; then
            sudo -u postgres createuser --createdb --superuser --replication "$DB_USER"
        else
            print_error "Password-based authentication is not supported by this script. Please leave DB_PASSWORD empty."
            exit 1
        fi
    else
        print_warning "PostgreSQL user '$DB_USER' already exists."
    fi

    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='openspp_dev'" | grep -q 1;
    then
        print_status "Creating development database 'openspp_dev'..."
        sudo -u postgres createdb -O "$DB_USER" openspp_dev
    else
        print_warning "Database 'openspp_dev' already exists."
    fi

    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='openspp_test'" | grep -q 1;
    then
        print_status "Creating test database 'openspp_test'..."
        sudo -u postgres createdb -O "$DB_USER" openspp_test
    else
        print_warning "Database 'openspp_test' already exists."
    fi

    print_status "PostgreSQL databases created: openspp_dev, openspp_test"
}

# Function to configure Odoo for OpenSPP development
configure_odoo() {
    print_status "Configuring Odoo for OpenSPP development..."
    cat > "$INSTALL_PATH/odoo.conf" << EOF
[options]
db_host = localhost
db_port = 5432
db_user = $DB_USER
db_password = False
addons_path = $INSTALL_PATH/openspp-modules,$INSTALL_PATH/odoo/addons
http_port = 8069
longpolling_port = 8072
dev_mode = reload,qweb,xml
log_level = info
log_handler = :INFO
workers = 0
limit_time_cpu = 600
limit_time_real = 1200
EOF
    print_status "Odoo configuration created at $INSTALL_PATH/odoo.conf"
}

# Function to initialize test data by installing base OpenSPP modules
initialize_test_data() {
    print_status "Initializing test data by installing base OpenSPP modules into 'openspp_dev' database..."
    source "$INSTALL_PATH/venv/bin/activate"
    cd "$INSTALL_PATH"
    python odoo/odoo-bin \
        --config=odoo.conf \
        -d openspp_dev \
        -i spp_base,spp_programs,spp_beneficiary,spp_eligibility,spp_entitlement \
        --stop-after-init
    print_status "Base OpenSPP modules installed in openspp_dev database."
}

# Function to set up pre-commit hooks for code quality
setup_precommit() {
    print_status "Setting up pre-commit hooks in openspp-modules repository..."
    cd "$INSTALL_PATH/openspp-modules"
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120', '--extend-ignore=E203,W503']
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF
    source "$INSTALL_PATH/venv/bin/activate"
    pre-commit install
    print_status "Pre-commit hooks configured for openspp-modules."
}

# Function to create helper scripts for starting and updating OpenSPP
create_helper_scripts() {
    print_status "Creating helper scripts (start_openspp.sh, update_openspp.sh)..."
    cat > "$INSTALL_PATH/start_openspp.sh" << EOF
#!/bin/bash
source "$INSTALL_PATH/venv/bin/activate"
cd "$INSTALL_PATH"
python odoo/odoo-bin -c odoo.conf
EOF
    chmod +x "$INSTALL_PATH/start_openspp.sh"

    cat > "$INSTALL_PATH/update_openspp.sh" << EOF
#!/bin/bash
source "$INSTALL_PATH/venv/bin/activate"
echo "Updating openspp-modules repository..."
cd "$INSTALL_PATH/openspp-modules"
git pull origin main
echo "Updating Odoo repository..."
cd "$INSTALL_PATH/odoo"
git pull origin $ODOO_VERSION
echo "Installing/updating Python dependencies..."
cd "$INSTALL_PATH"
pip install -r odoo/requirements.txt
if [ -f openspp-modules/requirements.txt ]; then
    pip install -r openspp-modules/requirements.txt
fi
echo "Updating OpenSPP modules in the 'openspp_dev' database..."
python odoo/odoo-bin -c odoo.conf -u all -d openspp_dev --stop-after-init
echo "OpenSPP development environment updated successfully!"
EOF
    chmod +x "$INSTALL_PATH/update_openspp.sh"
    print_status "Helper scripts created in $INSTALL_PATH."
}

# Function to verify the installation by checking key components
verify_installation() {
    print_status "Verifying installation..."
    local errors=0
    if command_exists python3 && [[ $(python3 --version) == *"$PYTHON_VERSION"* ]]; then print_status "✓ Python installed: $(python3 --version)"; else print_error "✗ Python not found or version mismatch. Expected ~$PYTHON_VERSION"; ((errors++)); fi
    if command_exists node && [[ $(node --version) == *"v$NODE_VERSION"* ]]; then print_status "✓ Node.js installed: $(node --version)"; else print_error "✗ Node.js not found or version mismatch. Expected ~$NODE_VERSION"; ((errors++)); fi
    if command_exists psql; then print_status "✓ PostgreSQL client installed: $(psql --version)"; else print_error "✗ PostgreSQL client not found"; ((errors++)); fi
    if command_exists git; then print_status "✓ Git installed: $(git --version)"; else print_error "✗ Git not found"; ((errors++)); fi
    if [ -f "$INSTALL_PATH/venv/bin/activate" ]; then print_status "✓ Virtual environment created"; else print_error "✗ Virtual environment not found at $INSTALL_PATH/venv"; ((errors++)); fi
    if [ -d "$INSTALL_PATH/openspp-modules" ] && [ -d "$INSTALL_PATH/odoo" ]; then print_status "✓ OpenSPP modules and Odoo repositories cloned"; else print_error "✗ OpenSPP modules or Odoo repository not found in $INSTALL_PATH"; ((errors++)); fi
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw openspp_dev; then print_status "✓ Database 'openspp_dev' exists"; else print_error "✗ Database 'openspp_dev' not found"; ((errors++)); fi
    if [ "$errors" -eq 0 ]; then print_status "✅ All checks passed! OpenSPP development environment is ready."; return 0; else print_error "❌ $errors checks failed. Please review the errors above and troubleshoot."; return 1; fi
}

# Function to display final instructions and next steps to the user
display_next_steps() {
    cat << EOF

${GREEN}🎉 OpenSPP Development Environment Setup Complete!${NC}

${YELLOW}Next steps:${NC}
1.  To start working, activate your virtual environment:
    ${GREEN}source $INSTALL_PATH/venv/bin/activate${NC}

2.  Start the OpenSPP development server:
    ${GREEN}$INSTALL_PATH/start_openspp.sh${NC}

3.  Access OpenSPP in your web browser at:
    ${GREEN}http://localhost:8069${NC}

4.  To update your development environment:
    ${GREEN}$INSTALL_PATH/update_openspp.sh${NC}

${YELLOW}Useful paths:${NC}
-   OpenSPP development root: ${GREEN}$INSTALL_PATH${NC}
-   OpenSPP modules repository: ${GREEN}$INSTALL_PATH/openspp-modules${NC}
-   Odoo configuration file: ${GREEN}$INSTALL_PATH/odoo.conf${NC}
-   Python virtual environment: ${GREEN}$INSTALL_PATH/venv${NC}
-   OpenSPP documentation repository: ${GREEN}$INSTALL_PATH/openspp-docs${NC}
EOF
}

# Main installation flow function
main() {
    echo "======================================"
    echo " OpenSPP Development Environment Setup"
    echo "======================================"
    echo
    print_warning "This script requires sudo privileges for system-wide installations."

    DRY_RUN=false
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --branch) OPENSPP_BRANCH="$2"; shift 2;;
            --python) PYTHON_VERSION="$2"; shift 2;;
            --odoo-version) ODOO_VERSION="$2"; shift 2;;
            --path) INSTALL_PATH="$2"; shift 2;;
            --dry-run) DRY_RUN=true; shift 1;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --branch BRANCH      OpenSPP modules branch to checkout (default: main)"
                echo "  --python VERSION     Python version to use (default: 3.10)"
                echo "  --odoo-version VERSION Odoo version to clone (default: 15.0)"
                echo "  --path PATH          Absolute path to install the environment (default: ~/openspp-dev)"
                echo "  --help               Show this help message"
                exit 0
                ;;
            *) print_error "Unknown option: $1"; exit 1;;
        esac
    done

    detect_os
    if [ "$OS" == "unknown" ]; then
        print_error "Unsupported OS: $DISTRO. This script only supports Debian/Ubuntu, Red Hat/Fedora, and macOS."
        print_status "For other systems, please follow the manual installation guide."
        exit 1
    fi

    case "$OS" in
        debian) install_debian_dependencies ;;
        redhat) install_redhat_dependencies ;;
        macos) install_macos_dependencies ;;
    esac
    setup_python_env
    clone_repositories
    install_python_dependencies
    setup_database
    configure_odoo
    initialize_test_data
    setup_precommit
    create_helper_scripts

    if verify_installation; then
        display_next_steps
    else
        print_error "Installation completed with errors. Please check the output above for details."
        exit 1
    fi
}

main "$@"