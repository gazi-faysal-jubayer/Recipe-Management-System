#!/bin/bash

# Supabase Setup Script

set -e

echo "🗄️  Setting up Supabase database..."

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Installing Supabase CLI..."
    npm install -g supabase
fi

# Link to your project
echo "Please run: supabase link --project-ref your-project-ref"
echo ""
echo "Then run migrations:"
echo "1. supabase db push"
echo ""
echo "Or manually via SQL Editor:"
echo "1. Open Supabase Dashboard → SQL Editor"
echo "2. Run database/migrations/supabase/001_initial_schema.sql"
echo "3. Run database/migrations/supabase/002_add_rls_policies.sql"
echo "4. Run database/migrations/supabase/003_add_indexes.sql"
echo ""
echo "✅ Setup instructions displayed!"
