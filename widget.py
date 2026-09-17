"""A small always-on-top Windows desktop widget that shows the current
lesson from the 12RD timetable and alternates between Week A / Week B
automatically once you've told it which week it currently is.

Run with:  python widget.py
"""
import datetime
import tkinter as tk
from tkinter import font as tkfont

import schedule_data as sd
import week_state as ws

REFRESH_MS = 20_000  # how often to redraw / recheck the time

BG = "#1e1e2e"
PANEL_BG = "#282840"
TEXT = "#e8e8f0"
SUBTEXT = "#9a9ab0"
ACCENT = "#5b8dff"
CURRENT_BG = "#3a5fcc"
FREE_TEXT = "#6f6f85"


def parse_hm(s):
    h, m = s.split(":")
    return datetime.time(int(h), int(m))


class WeekPickerDialog(tk.Toplevel):
    """Blocking first-run dialog asking which week (A/B) it currently is."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Set up Calendar Widget")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.result = None

        tk.Label(
            self, text="Which timetable week is it right now?",
            bg=BG, fg=TEXT, font=("Segoe UI", 11), wraplength=260, justify="center",
        ).pack(padx=20, pady=(20, 10))

        tk.Label(
            self, text="The widget will alternate A/B automatically from here on.",
            bg=BG, fg=SUBTEXT, font=("Segoe UI", 9), wraplength=260, justify="center",
        ).pack(padx=20, pady=(0, 15))

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=(0, 20))

        for label in ("A", "B"):
            tk.Button(
                btn_frame, text=f"Week {label}", width=10,
                bg=ACCENT, fg="white", activebackground=CURRENT_BG,
                relief="flat", font=("Segoe UI", 10, "bold"),
                command=lambda w=label: self._choose(w),
            ).pack(side="left", padx=8)

        self.protocol("WM_DELETE_WINDOW", lambda: self._choose("A"))
        self.grab_set()
        self.transient(master)
        self.update_idletasks()
        # center on screen
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _choose(self, week_letter):
        self.result = week_letter
        self.destroy()


class CalendarWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Timetable")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=BG)

        self._always_on_top = True
        self._drag = {"x": 0, "y": 0}

        pos = ws.get_window_position()
        x, y = pos if pos else (self.winfo_screenwidth() - 320, 40)
        self.geometry(f"300x460+{x}+{y}")

        if not ws.is_configured():
            self.withdraw()
            picker = WeekPickerDialog(self)
            self.wait_window(picker)
            ws.set_current_week(picker.result or "A")
            self.deiconify()

        self._build_ui()
        self._build_context_menu()
        self.refresh()

    # ---------- UI construction ----------

    def _build_ui(self):
        title_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        small_font = tkfont.Font(family="Segoe UI", size=8)

        self.title_bar = tk.Frame(self, bg=PANEL_BG, height=34)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)

        tk.Label(
            self.title_bar, text="\U0001F4C5 Timetable", bg=PANEL_BG, fg=TEXT,
            font=title_font,
        ).pack(side="left", padx=10)

        self.week_badge = tk.Label(
            self.title_bar, text="", bg=ACCENT, fg="white",
            font=("Segoe UI", 9, "bold"), padx=8, pady=2,
        )
        self.week_badge.pack(side="left", padx=6)

        close_btn = tk.Label(
            self.title_bar, text="✕", bg=PANEL_BG, fg=SUBTEXT,
            font=("Segoe UI", 11), cursor="hand2",
        )
        close_btn.pack(side="right", padx=10)
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        for widget in (self.title_bar,):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)

        self.date_label = tk.Label(
            self, bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold"),
        )
        self.date_label.pack(fill="x", padx=12, pady=(10, 0))

        self.status_label = tk.Label(
            self, bg=BG, fg=ACCENT, font=("Segoe UI", 9),
            wraplength=270, justify="left",
        )
        self.status_label.pack(fill="x", padx=12, pady=(2, 8))

        self.periods_frame = tk.Frame(self, bg=BG)
        self.periods_frame.pack(fill="both", expand=True, padx=10)

        hint = tk.Label(
            self, text="Right-click for options", bg=BG, fg=SUBTEXT,
            font=small_font,
        )
        hint.pack(side="bottom", pady=(0, 6))

        self.bind("<Button-3>", self._show_context_menu)

    def _build_context_menu(self):
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Set week to A", command=lambda: self._set_week("A"))
        self.menu.add_command(label="Set week to B", command=lambda: self._set_week("B"))
        self.menu.add_separator()
        self.menu.add_command(label="Toggle always on top", command=self._toggle_topmost)
        self.menu.add_command(label="Refresh now", command=self.refresh)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.destroy)

    def _show_context_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _set_week(self, letter):
        ws.set_current_week(letter)
        self.refresh()

    def _toggle_topmost(self):
        self._always_on_top = not self._always_on_top
        self.attributes("-topmost", self._always_on_top)

    # ---------- dragging ----------

    def _start_drag(self, event):
        self._drag["x"] = event.x
        self._drag["y"] = event.y

    def _on_drag(self, event):
        x = self.winfo_x() + event.x - self._drag["x"]
        y = self.winfo_y() + event.y - self._drag["y"]
        self.geometry(f"+{x}+{y}")

    def _end_drag(self, _event):
        ws.set_window_position(self.winfo_x(), self.winfo_y())

    # ---------- data / rendering ----------

    def refresh(self):
        now = datetime.datetime.now()
        today = now.date()
        week_letter = ws.get_current_week(today) or "A"
        self.week_badge.configure(text=f"Week {week_letter}")

        day_name = today.strftime("%A")
        self.date_label.configure(text=f"{day_name}, {today.strftime('%d %b %Y')}")

        periods = sd.get_day_periods(day_name, week_letter)

        for child in self.periods_frame.winfo_children():
            child.destroy()

        if not periods:
            self.status_label.configure(text="It's the weekend – no lessons today.")
            self._render_weekend_preview(week_letter, today)
            self.after(REFRESH_MS, self.refresh)
            return

        current_time = now.time()
        current_index = None
        for i, p in enumerate(periods):
            if parse_hm(p["start"]) <= current_time < parse_hm(p["end"]):
                current_index = i
                break

        self._render_status(periods, current_time, current_index)
        self._render_periods(periods, current_index)

        self.after(REFRESH_MS, self.refresh)

    def _render_status(self, periods, current_time, current_index):
        if current_index is not None:
            p = periods[current_index]
            name = sd.period_display_name(p)
            end_t = parse_hm(p["end"])
            mins_left = self._minutes_between(current_time, end_t)
            self.status_label.configure(
                text=f"Now: {name} — ends in {mins_left} min ({p['end']})"
            )
            return

        if current_time < parse_hm(periods[0]["start"]):
            first = periods[0]
            self.status_label.configure(
                text=f"School starts at {first['start']} — {sd.period_display_name(first)}"
            )
            return

        if current_time >= parse_hm(periods[-1]["end"]):
            self.status_label.configure(text="School day is over. See you tomorrow!")
            return

        # In a gap between periods (shouldn't normally happen, but be safe)
        for p in periods:
            if current_time < parse_hm(p["start"]):
                mins = self._minutes_between(current_time, parse_hm(p["start"]))
                self.status_label.configure(
                    text=f"Next: {sd.period_display_name(p)} in {mins} min ({p['start']})"
                )
                return

    @staticmethod
    def _minutes_between(t1, t2):
        d1 = datetime.datetime.combine(datetime.date.today(), t1)
        d2 = datetime.datetime.combine(datetime.date.today(), t2)
        return max(0, int((d2 - d1).total_seconds() // 60))

    def _render_periods(self, periods, current_index):
        for i, p in enumerate(periods):
            is_current = i == current_index
            lesson = p["lesson"]
            name = sd.period_display_name(p)

            row_bg = CURRENT_BG if is_current else BG
            row = tk.Frame(self.periods_frame, bg=row_bg)
            row.pack(fill="x", pady=1)

            time_col = tk.Label(
                row, text=f"{p['start']}", bg=row_bg,
                fg=TEXT if is_current else SUBTEXT,
                font=("Segoe UI", 9), width=6, anchor="w",
            )
            time_col.pack(side="left", padx=(4, 0), pady=4)

            info_frame = tk.Frame(row, bg=row_bg)
            info_frame.pack(side="left", fill="x", expand=True, pady=4)

            name_color = TEXT if (lesson or is_current) else FREE_TEXT
            tk.Label(
                info_frame, text=name, bg=row_bg, fg=name_color,
                font=("Segoe UI", 9, "bold" if is_current else "normal"),
                anchor="w", justify="left", wraplength=170,
            ).pack(fill="x")

            if lesson:
                _, cls, teacher, room = lesson
                detail = " · ".join(x for x in (teacher, room) if x)
                tk.Label(
                    info_frame, text=detail, bg=row_bg,
                    fg=TEXT if is_current else SUBTEXT,
                    font=("Segoe UI", 8), anchor="w", justify="left",
                ).pack(fill="x")

    def _render_weekend_preview(self, week_letter, today):
        days_ahead = (0 - today.weekday()) % 7  # next Monday
        if days_ahead == 0:
            days_ahead = 7
        next_school_day = today + datetime.timedelta(days=days_ahead)
        next_week_letter = ws.get_current_week(next_school_day) or week_letter
        periods = sd.get_day_periods(next_school_day.strftime("%A"), next_week_letter)

        tk.Label(
            self.periods_frame,
            text=f"Next up: {next_school_day.strftime('%A %d %b')} (Week {next_week_letter})",
            bg=BG, fg=SUBTEXT, font=("Segoe UI", 9, "italic"),
            wraplength=270, justify="left",
        ).pack(anchor="w", pady=(8, 4))

        first_lesson = next((p for p in periods if p["lesson"]), None)
        if first_lesson:
            tk.Label(
                self.periods_frame,
                text=f"First lesson: {sd.period_display_name(first_lesson)} at {first_lesson['start']}",
                bg=BG, fg=TEXT, font=("Segoe UI", 9),
                wraplength=270, justify="left",
            ).pack(anchor="w")


if __name__ == "__main__":
    app = CalendarWidget()
    app.mainloop()
