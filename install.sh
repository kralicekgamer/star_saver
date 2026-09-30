#!/bin/sh
set -eu

PROJECT_NAME="star_saver"
INSTALL_DIR=${STAR_SAVER_INSTALL_DIR:-"$HOME/.local/share/$PROJECT_NAME"}
BIN_DIR=${STAR_SAVER_BIN_DIR:-"$HOME/.local/bin"}
REPO_URL=${STAR_SAVER_REPO_URL:-"https://github.com/kralicekgamer/star_saver/archive/refs/heads/main.tar.gz"}
REPO_DIR="$INSTALL_DIR/repo"
VENV_DIR="$INSTALL_DIR/.venv"
WRAPPER="$BIN_DIR/$PROJECT_NAME"

command -v python3 >/dev/null 2>&1 || {
    echo "star_saver: python3 is required" >&2
    exit 1
}
command -v curl >/dev/null 2>&1 || {
    echo "star_saver: curl is required" >&2
    exit 1
}
command -v tar >/dev/null 2>&1 || {
    echo "star_saver: tar is required" >&2
    exit 1
}

mkdir -p "$INSTALL_DIR" "$BIN_DIR"
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT INT TERM

curl -fsSL "$REPO_URL" -o "$TEMP_DIR/star_saver.tar.gz"
mkdir -p "$REPO_DIR"
tar -xzf "$TEMP_DIR/star_saver.tar.gz" -C "$TEMP_DIR"
EXTRACTED_DIR=$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d -print -quit)
if [ -z "$EXTRACTED_DIR" ]; then
    echo "star_saver: downloaded archive is empty" >&2
    exit 1
fi
rm -rf "$REPO_DIR"
mv "$EXTRACTED_DIR" "$REPO_DIR"

if [ ! -x "$VENV_DIR/bin/python" ]; then
    python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
"$VENV_DIR/bin/python" -m pip install --upgrade "$REPO_DIR"

cat > "$WRAPPER" <<EOF
#!/bin/sh
exec "$VENV_DIR/bin/star_saver" "\$@"
EOF
chmod +x "$WRAPPER"

echo "Installed star_saver to $WRAPPER"
case ":${PATH:-}:" in
    *:"$BIN_DIR":*) ;;
    *) echo "Add $BIN_DIR to PATH to run star_saver from any shell." ;;
esac
