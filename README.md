# Timetable Widget

A tiny always-on-top Windows desktop widget that shows your current/next
lesson from the 12RD timetable, and tells you exactly what's on for the rest
of the day.

Notes on the data (`schedule_data.py`):
- Monday-Thursday are identical in Week A and Week B.
- Friday differs: Week A period 3 is Theory of Knowledge, Week B period 3 is
  Islamic Education.
- Friday's times are corrected from the printed timetable: Mentor time is
  07:40-07:50, each lesson is 50 minutes, break is 09:30-09:50, and the day
  ends at 11:30 (only 4 periods, no lunch/P5/P6).

## Running it

Requires Python 3.9+ (Tkinter is included with the standard Windows
installer from python.org — no extra packages needed).

```
python widget.py
```

On first run it asks once whether it's currently Week A or Week B; after
that it alternates automatically every calendar week. You can re-sync it at
any time (e.g. after a school holiday) by right-clicking the widget and
choosing "Set week to A" / "Set week to B".

The widget is frameless — drag it by its title bar to reposition (position
is remembered), right-click anywhere on it for the options menu (set week,
toggle always-on-top, refresh, exit), and click the × to close it.

## Building a standalone .exe

So you don't need Python installed to run it day-to-day:

```
build.bat
```

This uses PyInstaller to produce `dist\TimetableWidget.exe`. Copy that
wherever you like (e.g. `%APPDATA%\CalendarWidget\`).

## Running it automatically on login

1. Press `Win+R`, type `shell:startup`, hit Enter.
2. Copy a shortcut to `TimetableWidget.exe` (or `widget.py`) into that
   folder.

The widget will then open automatically every time you log in to Windows.

## Files

- `schedule_data.py` - the timetable itself (lessons + period times).
- `week_state.py` - remembers which week (A/B) is current and persists your
  chosen widget position, stored in `%APPDATA%\CalendarWidget\config.json`.
- `widget.py` - the Tkinter GUI.
- `build.bat` - packages the app into a standalone `.exe` with PyInstaller.
