#!/bin/bash
# Post-create command script for Microsoft Foundry Jumpstart dev container
# This script is executed after the dev container is created

set -e  # Exit on any error

echo "🚀 Running post-create setup for Microsoft Foundry Jumpstart devcontainer..."

# Configure Git settings
echo "📝 Configuring Git settings..."
git config --global core.autocrlf input
git config --global core.fileMode false

# Install Python development dependencies
echo "🐍 Installing Python development dependencies..."
if command -v uv >/dev/null 2>&1; then
    uv sync --group dev
else
    echo "  Warning: uv not found; skipping Python dev dependency install"
fi

# Ensure Bicep CLI is available through Azure CLI
echo "🧱 Ensuring Bicep CLI is available via Azure CLI..."
if command -v az >/dev/null 2>&1; then
    if az bicep install >/dev/null 2>&1; then
        echo "  Bicep CLI install/refresh succeeded"
    else
        echo "  Warning: Failed to install/refresh Bicep CLI via az bicep install"
    fi
else
    echo "  Warning: Azure CLI not found; cannot install Bicep CLI"
fi

# Ensure Node.js tools are properly sourced and available
echo "🔧 Setting up Node.js environment..."
# Source nvm to ensure it's available
if [ -s "${NVM_DIR}/nvm.sh" ]; then
    . "${NVM_DIR}/nvm.sh"
    echo "  NVM sourced successfully"
else
    echo "  Warning: NVM not found at ${NVM_DIR}/nvm.sh"
fi

# Verify installations
echo "✅ Verifying installations..."
echo "  Node.js version: $(node --version 2>/dev/null || echo 'Not found')"
echo "  NPM version: $(npm --version 2>/dev/null || echo 'Not found')"
echo "  NPX version: $(npx --version 2>/dev/null || echo 'Not found')"
echo "  NPX location: $(which npx 2>/dev/null || echo 'Not found')"
echo "  Python version: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "  Azure CLI version: $(az version --query '"azure-cli"' -o tsv 2>/dev/null || echo 'Not found')"
echo "  Azure Developer CLI version: $(azd version 2>/dev/null | head -n 1 || echo 'Not found')"
echo "  Bicep version: $(az bicep version 2>/dev/null || echo 'Not found')"

# Configure GitHub Copilot in the CLI alias (ghcs) for bash
echo "🤖 Configuring GitHub Copilot CLI alias..."
if command -v gh >/dev/null 2>&1; then
    # Ensure ~/.bashrc exists
    touch ~/.bashrc
    # Add alias if not already present
    if ! grep -q 'gh copilot alias -- bash' ~/.bashrc; then
        echo 'eval "$(gh copilot alias -- bash)"' >> ~/.bashrc
        echo "  Added ghcs alias to ~/.bashrc"
    else
        echo "  ghcs alias already present in ~/.bashrc"
    fi
    # Source it for current session (if we're in bash)
    if [ -n "$BASH_VERSION" ]; then
        # shellcheck source=/dev/null
        . ~/.bashrc
    fi
    echo "  gh version: $(gh --version | head -n 1)"
else
    echo "  Warning: GitHub CLI (gh) not found; skipping ghcs alias setup."
fi

echo "🎉 Post-create setup completed successfully!"
