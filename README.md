# Star Saver

A colorful animated night sky for your terminal, written in Python.

The screen shows stars, occasional diagonal meteors, the current time in the top-right corner, and a random English IT message at the bottom. Press any key to exit.

Displayed messages from https://github.com/garuda-linux/startpage-v2/blob/main/src/app/jokes/jokes.ts

## Requirements

- Linux terminal
- Python 3.10 or newer
- Git

## Install

From a cloned checkout:

```sh
./install.sh
```

The installer creates an isolated environment in `$HOME/.local/share/star_saver` and installs the command as `$HOME/.local/bin/star_saver`. Add `$HOME/.local/bin` to your `PATH` if the installer tells you to.

To use another installation directory:

```sh
STAR_SAVER_INSTALL_DIR="$HOME/.local/share/star_saver-dev" ./install.sh
```

## Run

```sh
star_saver
```

Press any key to return to the shell. `Ctrl-C` is also handled safely.

## Uninstall

Run this from the same checkout:

```sh
./uninstall.sh
```

The uninstall script removes the wrapper and the selected installation directory.

## Development

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pytest
```