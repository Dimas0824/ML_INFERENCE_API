#!/bin/bash

echo "🚀 Railway Deployment Setup Script"
echo "=================================="

# Check if files exist
echo ""
echo "📋 Checking required files..."

files=("railway.json" "nixpacks.toml" "requirements.txt" "Procfile" "app/main.py")
missing_files=()

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo ""
    echo "⚠️  Missing files detected. Please create them first."
    exit 1
fi

# Check Python version
echo ""
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')

if [[ "$python_version" == "3.12"* ]]; then
    echo "✅ Python 3.12.x detected"
elif [[ "$python_version" == "3.13"* ]]; then
    echo "⚠️  WARNING: Python 3.13 detected!"
    echo "   Railway will use Python 3.12 (specified in nixpacks.toml)"
else
    echo "⚠️  Python version: $python_version"
fi

# Validate railway.json
echo ""
echo "🔍 Validating railway.json..."
if command -v jq &> /dev/null; then
    jq empty railway.json 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ railway.json is valid JSON"
    else
        echo "❌ railway.json has syntax errors"
        exit 1
    fi
else
    echo "⚠️  jq not installed, skipping JSON validation"
fi

# Test local installation (optional)
echo ""
read -p "🧪 Test local installation? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    
    echo "Deactivating venv..."
    deactivate
fi

# Git check
echo ""
echo "📦 Git Status..."
if [ -d .git ]; then
    echo "✅ Git repository initialized"
    
    # Check if files are tracked
    untracked=$(git ls-files --others --exclude-standard | grep -E "railway.json|nixpacks.toml|requirements.txt|Procfile")
    if [ ! -z "$untracked" ]; then
        echo "⚠️  Untracked files found:"
        echo "$untracked"
        echo ""
        read -p "Add and commit files? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add railway.json nixpacks.toml requirements.txt Procfile
            git commit -m "Add Railway deployment configuration"
            echo "✅ Files committed"
        fi
    else
        echo "✅ All config files are tracked"
    fi
else
    echo "⚠️  Not a git repository"
    echo "   Run: git init && git add . && git commit -m 'Initial commit'"
fi

echo ""
echo "=================================="
echo "✅ Railway setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Push to GitHub: git push origin main"
echo "   2. Go to railway.app"
echo "   3. Create new project"
echo "   4. Connect your GitHub repo"
echo "   5. Railway will auto-detect and deploy!"
echo ""
echo "🔧 Environment Variables to set in Railway:"
echo "   - Add any API keys or secrets in Railway dashboard"
echo "   - PORT is automatically set by Railway"
echo ""