#!/bin/bash
# Termux Installation Helper Script
# Run with: bash install_termux.sh

echo "=================================="
echo "Roblox Auto-Signup - Termux Setup"
echo "=================================="
echo ""

# Install packages individually to avoid conflicts
echo "[1/10] Installing playwright..."
pip install playwright --no-deps
pip install greenlet websockets pyee

echo "[2/10] Installing pyyaml..."
pip install pyyaml

echo "[3/10] Installing pydantic..."
pip install pydantic

echo "[4/10] Installing python-dotenv..."
pip install python-dotenv

echo "[5/10] Installing httpx..."
pip install httpx

echo "[6/10] Installing aiofiles..."
pip install aiofiles

echo "[7/10] Installing pymailtm..."
pip install pymailtm

echo "[8/10] Installing utilities..."
pip install pyperclip tqdm rich tenacity fake-useragent loguru

echo "[9/10] Installing Playwright browser..."
playwright install chromium

echo "[10/10] Testing installation..."
python test_installation.py

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit config.yaml: nano config.yaml"
echo "2. Add your NopeCHA API key"
echo "3. Run: python main.py"
