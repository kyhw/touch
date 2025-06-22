#!/bin/bash

echo "🚀 Touch: Quick Start Setup"
echo "=========================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "   Please edit .env file with your AWS credentials"
fi

# Run setup test
echo "🧪 Running setup validation..."
python test_setup.py

echo ""
echo "✅ Setup complete!"
echo "📖 Next steps:"
echo "   1. Edit .env file with your AWS credentials"
echo "   2. Run: python cli.py --help"
echo "   3. Try: python cli.py video.mp4" 