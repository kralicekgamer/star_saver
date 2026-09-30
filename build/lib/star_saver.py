"""Animated terminal night sky screensaver."""

from __future__ import annotations

import os
import random
import select
import shutil
import sys
import termios
import time
import tty
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

from rich.live import Live
from rich.text import Text

FPS = 24
STAR_DENSITY = 0.02
METEOR_CHANCE = 0.018
MAX_METEORS = 2
SOURCE_MESSAGE_FILE = Path(__file__).with_name("messages.txt")
INSTALLED_MESSAGE_FILE = Path(sys.prefix) / "messages.txt"
STAR_STYLES = ("bright_white", "bright_cyan", "bright_blue", "bright_yellow")
METEOR_DIRECTIONS = (
    (-1.25, -0.55),
    (-1.25, 0.55),
    (1.25, -0.55),
    (1.25, 0.55),
    (-0.85, -0.85),
    (-0.85, 0.85),
    (0.85, -0.85),
    (0.85, 0.85),
)


@dataclass(frozen=True)
class Star:
    x: int
    y: int
    glyph: str
    style: str


@dataclass
class Meteor:
    x: float
    y: float
    age: int = 0
    style: str = "bright_white"
    dx: float = 1.25
    dy: float = 0.55

    def advance(self) -> None:
        self.x += self.dx
        self.y += self.dy
        self.age += 1


def load_messages(path: Path | None = None) -> list[str]:
    """Load non-empty messages from a UTF-8 text file."""
    if path is None:
        path = SOURCE_MESSAGE_FILE if SOURCE_MESSAGE_FILE.is_file() else INSTALLED_MESSAGE_FILE
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def format_clock(now: datetime | None = None) -> str:
    """Return the clock in the requested 24-hour format."""
    return (now or datetime.now()).strftime("%H:%M")


def generate_stars(width: int, height: int, seed: int | None = None) -> list[Star]:
    """Generate a stable set of stars inside the usable terminal area."""
    if width < 1 or height < 1:
        return []

    generator = random.Random(seed)
    count = max(1, int(width * height * STAR_DENSITY))
    glyphs = (".", "*", "+", "·")
    return [
        Star(
            x=generator.randrange(width),
            y=generator.randrange(height),
            glyph=generator.choice(glyphs),
            style=generator.choice(STAR_STYLES),
        )
        for _ in range(count)
    ]


def update_meteors(
    meteors: list[Meteor], width: int, height: int, generator: random.Random
) -> None:
    """Advance active meteors and occasionally add a new one."""
    for meteor in meteors:
        meteor.advance()

    meteors[:] = [
        meteor
        for meteor in meteors
        if (
            -8 <= meteor.x < width + 8
            and -8 <= meteor.y < height + 8
            and meteor.age < 30
        )
    ]

    if len(meteors) < MAX_METEORS and generator.random() < METEOR_CHANCE:
        dx, dy = generator.choice(METEOR_DIRECTIONS)
        meteors.append(
            Meteor(
                x=generator.uniform(0, max(0, width - 1)),
                y=generator.uniform(0, max(0, height - 1)),
                style=generator.choice(("bright_white", "bright_cyan", "bright_yellow")),
                dx=dx,
                dy=dy,
            )
        )


def _draw_cell(line: Text, position: int, value: str, style: str | None = None) -> None:
    if 0 <= position < len(line.plain):
        line.plain = line.plain[:position] + value + line.plain[position + 1 :]
        if style:
            line.stylize(style, position, position + len(value))


def build_frame(
    width: int,
    height: int,
    stars: list[Star],
    meteors: list[Meteor],
    message: str,
    clock: str,
) -> Text:
    """Compose one terminal frame from the current animation state."""
    if width < 1 or height < 1:
        return Text()

    lines = [Text(" " * width) for _ in range(height)]
    for star in stars:
        if 0 <= star.y < height:
            _draw_cell(lines[star.y], star.x, star.glyph, star.style)

    for meteor in meteors:
        head_x, head_y = round(meteor.x), round(meteor.y)
        for tail in range(6, -1, -1):
            x = head_x - round(tail * meteor.dx)
            y = head_y - round(tail * meteor.dy)
            if 0 <= y < height and 0 <= x < width:
                style = meteor.style if tail < 2 else "dim " + meteor.style
                _draw_cell(lines[y], x, "." if tail else "*", style)

    clock_start = max(0, width - len(clock))
    _draw_cell(lines[0], clock_start, clock, "bold bright_white")

    message_start = max(0, (width - len(message)) // 2)
    _draw_cell(lines[-1], message_start, message[:width], "italic bright_cyan")

    return Text("\n").join(lines)


@contextmanager
def raw_terminal() -> Iterator[None]:
    """Temporarily put stdin into non-blocking raw mode."""
    if not sys.stdin.isatty():
        raise RuntimeError("star_saver requires an interactive terminal")

    file_descriptor = sys.stdin.fileno()
    original = termios.tcgetattr(file_descriptor)
    try:
        tty.setcbreak(file_descriptor)
        yield
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, original)


def key_pressed() -> bool:
    """Return whether a key is waiting without blocking the animation."""
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if ready:
        os.read(sys.stdin.fileno(), 1)
        return True
    return False


def run() -> None:
    """Run the screensaver until the user presses any key."""
    messages = load_messages()
    if not messages:
        message_file = SOURCE_MESSAGE_FILE if SOURCE_MESSAGE_FILE.is_file() else INSTALLED_MESSAGE_FILE
        raise RuntimeError(f"no messages found in {message_file}")

    generator = random.Random()
    message = generator.choice(messages)
    stars: list[Star] = []
    meteors: list[Meteor] = []
    dimensions: tuple[int, int] | None = None

    with raw_terminal(), Live(screen=True, refresh_per_second=FPS, transient=True) as live:
        while True:
            terminal_size = shutil.get_terminal_size((80, 24))
            width, height = terminal_size.columns, terminal_size.lines
            if dimensions != (width, height):
                dimensions = (width, height)
                stars = generate_stars(width, max(1, height - 1), generator.randrange(1_000_000))

            update_meteors(meteors, width, max(1, height - 1), generator)
            live.update(
                build_frame(
                    width,
                    height,
                    stars,
                    meteors,
                    message,
                    format_clock(),
                ),
                refresh=True,
            )
            if key_pressed():
                break
            time.sleep(1 / FPS)


def main() -> None:
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        pass
    except RuntimeError as error:
        print(f"star_saver: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
