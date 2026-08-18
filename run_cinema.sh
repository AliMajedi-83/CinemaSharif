#!/bin/bash

echo "🚀 Starting AP-Cinema Project..."

# 1. Navigate to the Django project directory
cd "$(dirname "$0")/ap-cinema"

# 2. Activate virtual environment (if it exists)
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# 3. Kill any process running on port 8000 from a previous session
fuser -k 8000/tcp 2>/dev/null

# 4. Open browsers in the background (after a 2-second delay for the server to load)
(
    sleep 2
    xdg-open "http://127.0.0.1:8000/" 2>/dev/null
    xdg-open "http://127.0.0.1:8000/dashboard/" 2>/dev/null
) &

# 5. Run the server in the foreground (to view logs)
echo "✅ Server is running. Press Ctrl+C to stop."
python3 manage.py runserver
