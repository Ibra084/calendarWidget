# Timetable Widget

Shows your current/next lesson from the 12RD timetable at a glance. There
are two versions in this repo:

- **`Rainmeter/TimetableWidget/`** — a true desktop widget that sits on your
  desktop itself, behind your icons (like a classic Windows gadget). Needs
  [Rainmeter](https://www.rainmeter.net/) installed. **Use this one** if you
  want it living on the desktop.
- **`widget.py`** — a standalone Python/Tkinter app that floats always-on-top
  over other windows instead. No extra software to install beyond Python,
  but it's a normal floating window, not part of the desktop itself.

Notes on the data (shared by both versions):
- Monday-Thursday are identical in Week A and Week B.
- Friday differs: Week A period 3 is Theory of Knowledge, Week B period 3 is
  Islamic Education.
- Friday's times are corrected from the printed timetable: Mentor time is
  07:40-07:50, each lesson is 50 minutes, break is 09:30-09:50, and the day
  ends at 11:30 (only 4 periods, no lunch/P5/P6).

## Desktop widget (Rainmeter) — recommended

1. Install [Rainmeter](https://www.rainmeter.net/) (free) — download the
   installer and run it with defaults.
2. Copy the whole `Rainmeter\TimetableWidget` folder from this repo into
   `%USERPROFILE%\Documents\Rainmeter\Skins\`, so you end up with
   `Documents\Rainmeter\Skins\TimetableWidget\TimetableWidget.ini`.
3. Right-click the Rainmeter tray icon (bottom-right, near the clock) →
   **Manage**. In the Skins tab, select **TimetableWidget** on the left, then
   double-click **TimetableWidget.ini** on the right to load it.
4. It'll appear showing "Right-click this widget and choose 'Set Week A' or
   'Set Week B' to get started." Right-click the *widget itself* (not the
   tray icon) and pick whichever week it currently is. After that it
   alternates automatically every calendar week — re-sync any time the same
   way (e.g. after a school holiday).
5. It's set to sit **On Desktop** (behind your icons) by default. Since
   that means icons can visually overlap it, it's easiest to position it
   first: right-click → **Position** → **Bring to Front**, drag it (left-click
   and drag) to an empty patch of your desktop, then right-click → **Position**
   → **On Desktop** to send it back behind your icons.
6. It refreshes automatically every 20 seconds. To force an update, or to
   re-sync the week later, right-click the widget for the same options.

## Floating window (Python) — alternative

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

- `Rainmeter/TimetableWidget/TimetableWidget.ini` - the Rainmeter skin
  (window/background/menu settings).
- `Rainmeter/TimetableWidget/@Resources/schedule.lua` - the timetable data
  and current-lesson logic for the Rainmeter version, persists the
  chosen week to `@Resources/state.txt`.
- `schedule_data.py` - the timetable itself (lessons + period times), for
  the Python version.
- `week_state.py` - remembers which week (A/B) is current and persists your
  chosen widget position, stored in `%APPDATA%\CalendarWidget\config.json`,
  for the Python version.
- `widget.py` - the Tkinter GUI for the Python version.
- `build.bat` - packages the Python app into a standalone `.exe` with
  PyInstaller.
