#!/usr/bin/env bash
set -e

echo "========================================================="
echo "   CSTAN - Citizen Safety and Travel Assistance Network"
echo "========================================================="
echo ""

# Check python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found."
    exit 1
fi

echo "[1/3] Checking dependencies..."
python3 -m pip install -r requirements.txt --quiet

if [ ! -f "cstan.db" ]; then
    echo "[2/3] Initializing and seeding demo database..."
    python3 seed_data.py
else
    echo "[2/3] Database found."
fi

echo "[3/3] Launching CSTAN application server on http://127.0.0.1:5000 ..."
echo ""
echo "========================================================="
echo "  Tourist Demo: tourist@cstan.org / password123"
echo "  Admin Demo:   admin@cstan.org   / admin123"
echo "========================================================="
echo ""

python3 app.py
