from datetime import datetime
from pathlib import Path
import random

from star_saver import (
    Meteor,
    build_frame,
    format_clock,
    generate_stars,
    load_messages,
    update_meteors,
)


def test_load_messages_ignores_blank_lines(tmp_path: Path) -> None:
    message_file = tmp_path / "messages.txt"
    message_file.write_text(" first \n\nsecond\n", encoding="utf-8")

    assert load_messages(message_file) == ["first", "second"]


def test_format_clock_uses_24_hour_minutes() -> None:
    assert format_clock(datetime(2026, 9, 29, 21, 47)) == "21:47"


def test_generate_stars_stays_inside_terminal() -> None:
    stars = generate_stars(40, 10, seed=7)

    assert stars
    assert all(0 <= star.x < 40 and 0 <= star.y < 10 for star in stars)


def test_meteor_advances_diagonally() -> None:
    meteor = Meteor(x=2, y=3)
    meteor.advance()

    assert meteor.x > 2
    assert meteor.y > 3
    assert meteor.age == 1


def test_meteor_can_travel_in_a_different_direction() -> None:
    meteor = Meteor(x=2, y=3, dx=-1.25, dy=-0.55)
    meteor.advance()

    assert meteor.x < 2
    assert meteor.y < 3


def test_update_meteors_removes_old_meteors() -> None:
    meteors = [Meteor(x=100, y=100, age=29)]

    update_meteors(meteors, width=20, height=10, generator=random.Random(0))

    assert meteors == []


def test_build_frame_contains_clock_and_message() -> None:
    frame = build_frame(30, 5, [], [], "hello", "21:47")

    assert "21:47" in frame.plain
    assert "hello" in frame.plain
