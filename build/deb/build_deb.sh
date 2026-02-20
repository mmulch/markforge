#!/usr/bin/env bash
# build_deb.sh – Build markforge_1.0.0_all.deb
# Run from the project root:  bash build/deb/build_deb.sh
# Or from build/deb:          bash build_deb.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PKG_NAME="markforge"
PKG_VERSION="1.0.0"
PKG_DIR="${SCRIPT_DIR}/${PKG_NAME}_${PKG_VERSION}_all"

echo "==> Building ${PKG_NAME}_${PKG_VERSION}_all.deb"
echo "    Project root : $PROJECT_ROOT"
echo "    Staging dir  : $PKG_DIR"

# ---------------------------------------------------------------------------
# Clean staging tree
# ---------------------------------------------------------------------------
rm -rf "$PKG_DIR"

# ---------------------------------------------------------------------------
# Directory skeleton
# ---------------------------------------------------------------------------
install -d "$PKG_DIR/DEBIAN"
install -d "$PKG_DIR/usr/bin"
install -d "$PKG_DIR/usr/share/${PKG_NAME}/src"
install -d "$PKG_DIR/usr/share/applications"
install -d "$PKG_DIR/usr/share/icons/hicolor/scalable/apps"
install -d "$PKG_DIR/usr/share/doc/${PKG_NAME}"

# ---------------------------------------------------------------------------
# Application sources
# ---------------------------------------------------------------------------
cp "$PROJECT_ROOT"/src/*.py "$PKG_DIR/usr/share/${PKG_NAME}/src/"

# ---------------------------------------------------------------------------
# Launcher script  /usr/bin/markforge
# ---------------------------------------------------------------------------
cat > "$PKG_DIR/usr/bin/markforge" <<'LAUNCHER'
#!/bin/sh
exec python3 /usr/share/markforge/src/main.py "$@"
LAUNCHER
chmod 0755 "$PKG_DIR/usr/bin/markforge"

# ---------------------------------------------------------------------------
# Icon
# ---------------------------------------------------------------------------
cp "$PROJECT_ROOT/assets/markforge.svg" \
   "$PKG_DIR/usr/share/icons/hicolor/scalable/apps/markforge.svg"

# ---------------------------------------------------------------------------
# Desktop entry
# ---------------------------------------------------------------------------
cp "$SCRIPT_DIR/markforge.desktop" "$PKG_DIR/usr/share/applications/"

# ---------------------------------------------------------------------------
# Debian changelog (gzipped)
# ---------------------------------------------------------------------------
gzip -9 -c "$SCRIPT_DIR/changelog" \
  > "$PKG_DIR/usr/share/doc/${PKG_NAME}/changelog.Debian.gz"

# ---------------------------------------------------------------------------
# Copyright
# ---------------------------------------------------------------------------
cp "$SCRIPT_DIR/copyright" "$PKG_DIR/usr/share/doc/${PKG_NAME}/copyright"

# ---------------------------------------------------------------------------
# DEBIAN/control
# ---------------------------------------------------------------------------
cat > "$PKG_DIR/DEBIAN/control" <<EOF
Package: ${PKG_NAME}
Version: ${PKG_VERSION}
Architecture: all
Maintainer: Markforge Contributors <markforge@example.com>
Depends: python3 (>= 3.11),
         python3-pyqt6 (>= 6.4),
         python3-pyqt6.qtwebengine,
         python3-markdown,
         python3-pygments
Section: editors
Priority: optional
Homepage: https://github.com/your-org/markforge
Description: Markdown editor with live preview
 Markforge is a PyQt6-based Markdown editor featuring a live HTML preview
 powered by QtWebEngine, syntax highlighting via Pygments, and support for
 multiple languages.
EOF

# ---------------------------------------------------------------------------
# DEBIAN/postinst
# ---------------------------------------------------------------------------
cp "$SCRIPT_DIR/postinst" "$PKG_DIR/DEBIAN/postinst"
chmod 0755 "$PKG_DIR/DEBIAN/postinst"

# ---------------------------------------------------------------------------
# DEBIAN/postrm
# ---------------------------------------------------------------------------
cp "$SCRIPT_DIR/postrm" "$PKG_DIR/DEBIAN/postrm"
chmod 0755 "$PKG_DIR/DEBIAN/postrm"

# ---------------------------------------------------------------------------
# Fix permissions
# ---------------------------------------------------------------------------
find "$PKG_DIR" -type d -exec chmod 0755 {} \;
find "$PKG_DIR/usr" -type f -exec chmod 0644 {} \;
chmod 0755 "$PKG_DIR/usr/bin/markforge"

# ---------------------------------------------------------------------------
# Build the package
# ---------------------------------------------------------------------------
dpkg-deb --build --root-owner-group "$PKG_DIR"

DEB_FILE="${SCRIPT_DIR}/${PKG_NAME}_${PKG_VERSION}_all.deb"
echo ""
echo "==> Package built: $DEB_FILE"
echo "    Install with:  sudo dpkg -i $DEB_FILE"
echo "    Fix deps with: sudo apt-get install -f"
