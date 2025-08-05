#!/bin/bash
# Development setup script for PyPevol

set -e

echo "🚀 Setting up PyPevol development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 0 ]]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing development dependencies..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Run initial checks
echo "🧪 Running initial checks..."
make ci-check

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run tests: make test"
echo "  3. Start documentation server: make docs-serve"
echo "  4. Format code: make format"
echo ""
echo "Useful commands:"
echo "  make help          - Show all available commands"
echo "  make ci-check      - Run all CI checks locally"
echo "  make docs-serve    - Serve documentation at http://localhost:8000"
echo ""
