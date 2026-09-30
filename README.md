# Star Saver

A colorful animated night sky for your terminal, written in Python.

The screen shows stars, occasional diagonal meteors, the current time in the top-right corner, and a random English IT message at the bottom. Press any key to exit.

Displayed messages from https://github.com/garuda-linux/startpage-v2/blob/main/src/app/jokes/jokes.ts

## Install

```sh
curl -s https://raw.githubusercontent.com/kralicekgamer/screen_saver/refs/heads/main/install.sh | bash
```

The installer creates an isolated environment in `$HOME/.local/share/star_saver` and installs the command as `$HOME/.local/bin/star_saver`. Add `$HOME/.local/bin` to your `PATH` if the installer tells you to.

## Run

```sh
star_saver
```

Press any key to return to the shell. `Ctrl-C` is also handled safely.

## Uninstall

```sh
curl -s https://raw.githubusercontent.com/kralicekgamer/screen_saver/refs/heads/main/uninstall.sh | bash
```

The uninstall script removes the wrapper and the installation directory.