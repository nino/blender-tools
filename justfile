# Package the addon into a zip file for Blender installation
package:
    #!/usr/bin/env bash
    set -euo pipefail

    # Create a temporary directory for packaging
    TEMP_DIR=$(mktemp -d)
    ADDON_DIR="$TEMP_DIR/nino-tools"

    # Create addon directory
    mkdir -p "$ADDON_DIR"

    # Copy the addon file
    cp __init__.py "$ADDON_DIR/"

    # Create zip file
    cd "$TEMP_DIR"
    zip -r nino-tools.zip nino-tools

    # Move zip to project root
    mv nino-tools.zip {{justfile_directory()}}/

    # Clean up
    rm -rf "$TEMP_DIR"

    echo "✓ Created nino-tools.zip"
