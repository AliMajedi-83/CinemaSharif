#!/bin/bash

# Exit script on any critical error
set -e

echo -e "\n🎬 Starting AP-Cinema Ultimate Setup...\n"

# 1. Navigate to the Django project directory
cd "$(dirname "$0")/ap-cinema"

# --- Section 1: OS Prerequisites (PostgreSQL) ---
echo "⚙️ Checking PostgreSQL installation..."
if ! command -v psql > /dev/null; then
    echo "⚠️ PostgreSQL is not installed. Requesting sudo privileges to install..."
    # Apply temporary proxy for apt if configured in the network
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
else
    echo "✅ PostgreSQL is already installed."
fi

# --- Section 2: Database Management (Resetting previous data) ---
echo -e "\n🗄️ Do you want to DROP the existing database and start fresh? (y/n)"
read -r -p "Answer: " reset_db

if [[ "$reset_db" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "🗑️ Dropping and recreating cinema_db..."
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS cinema_db;"
    sudo -u postgres psql -c "CREATE DATABASE cinema_db;"
    # Set postgres user password to match settings.py
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '123456';"
    echo "✅ Database completely reset."
else
    echo "⏭️ Keeping existing database."
    # Ensure database exists if not resetting
    sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'cinema_db'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE cinema_db;"
fi

# --- Section 3: Virtual Environment and Python Dependencies ---
if [ ! -d ".venv" ]; then
    echo -e "\n📦 Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "🔄 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
# No need for --break-system-packages in a virtual environment
# If proxy is needed, run the script like: HTTPS_PROXY="http://..." ./setup_cinema.sh
pip install -r requirements.txt

# --- Section 4: Configuration and Migrations ---
if [ ! -f ".env" ]; then
    echo -e "\n⚙️ Creating default .env file..."
    echo "SECRET_KEY=django-insecure-dev-key-12345" > .env
    echo "DEBUG=True" >> .env
fi

echo -e "\n🗄️ Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

# --- Section 5: Creating System Admin ---
echo -e "\n👤 Do you want to create a superuser for the admin panel? (y/n)"
read -r -p "Answer: " create_su

if [[ "$create_su" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo -e "\n🎉 Setup Complete! You are good to go."
echo "🚀 Run: bash ../run_cinema.sh"
