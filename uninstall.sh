#!/bin/sh
set -eu

PROJECT_NAME="star_saver"
INSTALL_DIR=${STAR_SAVER_INSTALL_DIR:-"$HOME/.local/share/$PROJECT_NAME"}
BIN_DIR=${STAR_SAVER_BIN_DIR:-"$HOME/.local/bin"}
WRAPPER="$BIN_DIR/$PROJECT_NAME"

rm -f "$WRAPPER"
rm -rf "$INSTALL_DIR"

echo "Removed star_saver from $INSTALL_DIR"
