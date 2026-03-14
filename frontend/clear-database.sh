#!/usr/bin/env bash
set -euo pipefail

# Usage: ./clear-database.sh <phone_number>
# Example: ./clear-database.sh 5305747238
#          ./clear-database.sh +15305747238
#
# Removes a user from Supabase by phone number:
#   1. Deletes from public.users table
#   2. Deletes from Supabase Auth (auth.users)
#
# Requires: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars
# (service role key is in Supabase Dashboard → Settings → API → service_role secret)

if [ $# -lt 1 ]; then
  echo "Usage: ./clear-database.sh <phone_number>"
  echo "Example: ./clear-database.sh 5305747238"
  exit 1
fi

PHONE="$1"

# Normalize: add +1 prefix if not present
if [[ ! "$PHONE" == +* ]]; then
  PHONE="+1${PHONE}"
fi

# Load env vars from .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | grep -v '^\s*$' | xargs)
fi

# Check for required env vars — service role key needed for admin operations
SUPABASE_URL="${NEXT_PUBLIC_SUPABASE_URL:-${SUPABASE_URL:-}}"
SERVICE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"

if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" = "https://your-project.supabase.co" ]; then
  echo "Error: Set NEXT_PUBLIC_SUPABASE_URL in .env or export SUPABASE_URL"
  exit 1
fi

if [ -z "$SERVICE_KEY" ]; then
  echo "Error: Export SUPABASE_SERVICE_ROLE_KEY (find it in Supabase Dashboard → Settings → API)"
  echo ""
  echo "  export SUPABASE_SERVICE_ROLE_KEY='eyJ...'"
  echo "  ./clear-database.sh $1"
  exit 1
fi

echo "Looking up user with phone: $PHONE"

# Step 1: Find the user ID from Supabase Auth via admin API
USER_JSON=$(curl -s \
  -H "apikey: $SERVICE_KEY" \
  -H "Authorization: Bearer $SERVICE_KEY" \
  "${SUPABASE_URL}/auth/v1/admin/users?page=1&per_page=50")

USER_ID=$(echo "$USER_JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
users = data.get('users', data) if isinstance(data, dict) else data
for u in users:
    if u.get('phone') == '$PHONE':
        print(u['id'])
        break
" 2>/dev/null || true)

if [ -z "$USER_ID" ]; then
  echo "No user found with phone $PHONE"
  exit 0
fi

echo "Found user: $USER_ID"

# Step 2: Delete from public.users table
echo "Deleting from public.users..."
curl -s -o /dev/null -w "  HTTP %{http_code}\n" \
  -X DELETE \
  -H "apikey: $SERVICE_KEY" \
  -H "Authorization: Bearer $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  "${SUPABASE_URL}/rest/v1/users?id=eq.${USER_ID}"

# Step 3: Delete from Supabase Auth
echo "Deleting from auth.users..."
curl -s -o /dev/null -w "  HTTP %{http_code}\n" \
  -X DELETE \
  -H "apikey: $SERVICE_KEY" \
  -H "Authorization: Bearer $SERVICE_KEY" \
  "${SUPABASE_URL}/auth/v1/admin/users/${USER_ID}"

echo "Done. User $PHONE ($USER_ID) removed."
