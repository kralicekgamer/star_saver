#!/bin/sh
set -eu

PROJECT_NAME="star_saver"
INSTALL_DIR=${STAR_SAVER_INSTALL_DIR:-"$HOME/.local/share/$PROJECT_NAME"}
BIN_DIR=${STAR_SAVER_BIN_DIR:-"$HOME/.local/bin"}
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR="$INSTALL_DIR/repo"
VENV_DIR="$INSTALL_DIR/.venv"
WRAPPER="$BIN_DIR/$PROJECT_NAME"

command -v python3 >/dev/null 2>&1 || {
    echo "star_saver: python3 is required" >&2
    exit 1
}

mkdir -p "$INSTALL_DIR" "$BIN_DIR"
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"

for file in pyproject.toml star_saver.py messages.txt; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        echo "star_saver: missing $file" >&2
        exit 1
    fi
    cp "$SCRIPT_DIR/$file" "$REPO_DIR/$file"
done

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
