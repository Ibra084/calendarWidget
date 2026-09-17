"""Timetable data for Jumeirah English Speaking School - 12RD.

Lessons are identical on Monday-Thursday for Week A and Week B; the only
difference between the two weeks is period 3 on Friday. Times below reflect
the corrected Friday schedule (Mentor time 07:40-07:50, four 50-minute
lessons, a 20-minute break, day ends 11:30) rather than the times printed on
the original timetable PDF, which were wrong for Friday.

A lesson entry is a tuple: (subject, class_code, teacher, room).
`None` means a free period / nothing scheduled for that slot.
"""

COMMON_DAYS = {
    "Monday": {
        "Reg": ("Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"),
        "P1": ("English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"),
        "P2": ("Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"),
        "P3": ("Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"),
        "P4": ("French IB Ab Initio", "12AB/F3", "Miss Corcoran", "C1"),
        "P5": ("Physics IB HL", "124H2/P1", "Miss Collery", "S10"),
        "P6": None,
    },
    "Tuesday": {
        "Reg": ("Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"),
        "P1": ("Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"),
        "P2": ("Theory of Knowledge", "1206/Tk", "Mr Scott", "M3"),
        "P3": ("Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"),
        "P4": ("Islamic Education", "12B/IsIB", "Mr Akhtar", "C3"),
        "P5": ("Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"),
        "P6": ("English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"),
    },
    "Wednesday": {
        "Reg": ("Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"),
        "P1": None,
        "P2": ("Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"),
        "P3": ("Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"),
        "P4": ("French IB Ab Initio", "12AB/F3", "Miss Corcoran", "C1"),
        "P5": ("Physics IB HL", "124H2/P1", "Miss Collery", "S10"),
        "P6": ("Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"),
    },
    "Thursday": {
        "Reg": ("Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"),
        "P1": ("Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"),
        "P2": ("Games", "12-3B/Ga", "Mr Dunne", ""),
        "P3": ("Sixth Form", "12RD/Sf", "Mrs Guerrero", "SFCR"),
        "P4": ("Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"),
        "P5": ("Physics IB HL", "124H2/P1", "Miss Collery", "S10"),
        "P6": ("French IB Ab Initio", "12AB/F3", "Miss Corcoran", "C1"),
    },
}

FRIDAY_A = {
    "Reg": ("Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"),
    "P1": ("English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"),
    "P2": ("Physics IB HL", "124H2/P1", "Miss Collery", "S10"),
    "P3": ("Theory of Knowledge", "1206/Tk", "Mr Scott", "M3"),
    "P4": ("Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"),
}

FRIDAY_B = {
    "Reg": ("Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"),
    "P1": ("English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"),
    "P2": ("Physics IB HL", "124H2/P1", "Miss Collery", "S10"),
    "P3": ("Islamic Education", "12B/IsIB", "Mr Akhtar", "C8"),
    "P4": ("Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"),
}

SCHEDULE = {
    "A": {**COMMON_DAYS, "Friday": FRIDAY_A},
    "B": {**COMMON_DAYS, "Friday": FRIDAY_B},
}

# (period_code, start "HH:MM", end "HH:MM")
PERIOD_TIMES_STANDARD = [
    ("Reg", "07:40", "08:00"),
    ("P1", "08:00", "09:00"),
    ("P2", "09:00", "10:00"),
    ("Break", "10:00", "10:20"),
    ("P3", "10:20", "11:20"),
    ("P4", "11:20", "12:20"),
    ("Lunch", "12:20", "13:20"),
    ("P5", "13:20", "14:20"),
    ("P6", "14:20", "15:20"),
]

PERIOD_TIMES_FRIDAY = [
    ("Reg", "07:40", "07:50"),
    ("P1", "07:50", "08:40"),
    ("P2", "08:40", "09:30"),
    ("Break", "09:30", "09:50"),
    ("P3", "09:50", "10:40"),
    ("P4", "10:40", "11:30"),
]

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

LABELS = {
    "Reg": "Mentor Time",
    "Break": "Break",
    "Lunch": "Lunch",
}


def get_day_periods(day, week_letter):
    """Return an ordered list of period dicts for a given day + week ('A'/'B').

    Each dict has: code, start, end, lesson (tuple or None).
    Returns [] if `day` is not a school day (e.g. Saturday/Sunday).
    """
    if day not in DAYS_ORDER:
        return []
    times = PERIOD_TIMES_FRIDAY if day == "Friday" else PERIOD_TIMES_STANDARD
    lessons = SCHEDULE[week_letter][day]
    periods = []
    for code, start, end in times:
        periods.append({
            "code": code,
            "start": start,
            "end": end,
            "lesson": lessons.get(code),
        })
    return periods


def period_display_name(period):
    """Human-friendly name for a period dict, e.g. 'Maths IB Analysis HL' or 'Break'."""
    lesson = period["lesson"]
    if lesson is not None:
        return lesson[0]
    return LABELS.get(period["code"], "Free Period")
