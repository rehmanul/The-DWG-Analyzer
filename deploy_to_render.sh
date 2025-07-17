#!/bin/bash

echo "🚀 Deploying Enterprise Îlot Placement System to Render"
echo "======================================================"

# Check if git is configured
if ! git config --global user.email > /dev/null 2>&1; then
    echo "⚠️  Git user email not configured. Please run:"
    echo "   git config --global user.email 'your-email@example.com'"
    echo "   git config --global user.name 'Your Name'"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "📁 Initializing git repository..."
    git init
    echo "node_modules/" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo ".env" >> .gitignore
    echo "test_optimizer.py" >> .gitignore
fi

# Add all files to git
echo "📦 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Prepare for Render deployment - Enterprise Îlot Placement System"

# Check deployment files
echo "🔍 Verifying deployment files..."
files=("streamlit_app.py" "requirements.txt" "Dockerfile" "render.yaml" "Procfile" "runtime.txt" "RENDER_DEPLOYMENT_GUIDE.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
    fi
done

# Check core modules
echo "🔍 Verifying core modules..."
if [ -d "core" ]; then
    echo "✅ core/ - Found"
else
    echo "❌ core/ - Missing"
fi

if [ -d "src" ]; then
    echo "✅ src/ - Found"
else
    echo "❌ src/ - Missing"
fi

echo ""
echo "🎯 Next Steps for Render Deployment:"
echo "1. Push this repository to GitHub"
echo "2. Go to https://render.com and create an account"
echo "3. Connect your GitHub repository"
echo "4. Create a new Web Service"
echo "5. Configure with these settings:"
echo "   - Name: enterprise-ilot-placement-system"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: streamlit run streamlit_app.py --server.port \$PORT --server.address 0.0.0.0"
echo "   - Plan: Starter (Free tier available)"
echo ""
echo "📖 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "✨ Your Enterprise Îlot Placement System is ready for deployment!"