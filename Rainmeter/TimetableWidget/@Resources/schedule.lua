--[[
Timetable logic for 12RD. Ported from the standalone Python widget's
schedule_data.py / week_state.py so the Rainmeter skin has no external
dependencies beyond Rainmeter's bundled Lua.

Monday-Thursday are identical in Week A and Week B; only Friday period 3
differs. Friday's times are corrected from the printed timetable: Mentor
07:40-07:50, four 50-minute lessons, break 09:30-09:50, day ends 11:30.

This file is shared by three measures (header/week/status/list), each
configured with a different `Mode=` option in the .ini so they can be
styled independently while sharing one computation.

Only plain ASCII characters are used in any returned string: Rainmeter's
String meter renders text via GDI+ using the system codepage, and a
non-ASCII byte returned from Lua (even a valid UTF-8 sequence) reliably
comes out garbled (e.g. a middle-dot "\194\183" renders as "A-with-hat
dot" instead of "."). Stick to ASCII for anything shown on screen.
]]

local DAY_NAMES = {[1] = "Sunday", [2] = "Monday", [3] = "Tuesday", [4] = "Wednesday",
                   [5] = "Thursday", [6] = "Friday", [7] = "Saturday"}
local MONTH_NAMES = {"Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}

-- Lesson = {subject, class, teacher, room}; a missing key means free period.
local COMMON = {
  Monday = {
    Reg = {"Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"},
    P1 = {"English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"},
    P2 = {"Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"},
    P3 = {"Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"},
    P4 = {"French IB Ab Initio", "12AB/F3", "Miss Corcoran", "C1"},
    P5 = {"Physics IB HL", "124H2/P1", "Miss Collery", "S10"},
  },
  Tuesday = {
    Reg = {"Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"},
    P1 = {"Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"},
    P2 = {"Theory of Knowledge", "1206/Tk", "Mr Scott", "M3"},
    P3 = {"Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"},
    P4 = {"Islamic Education", "12B/IsIB", "Mr Akhtar", "C3"},
    P5 = {"Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"},
    P6 = {"English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"},
  },
  Wednesday = {
    Reg = {"Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"},
    P2 = {"Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"},
    P3 = {"Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"},
    P4 = {"French IB Ab Initio", "12AB/F3", "Miss Corcoran", "C1"},
    P5 = {"Physics IB HL", "124H2/P1", "Miss Collery", "S10"},
    P6 = {"Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"},
  },
  Thursday = {
    Reg = {"Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"},
    P1 = {"Maths IB Analysis HL", "12H2/M4", "Mr Flynn", "M25"},
    P2 = {"Games", "12-3B/Ga", "Mr Dunne", ""},
    P3 = {"Sixth Form", "12RD/Sf", "Mrs Guerrero", "SFCR"},
    P4 = {"Economics IB HL", "123M1/Eh", "Mr Dawson", "FC13"},
    P5 = {"Physics IB HL", "124H2/P1", "Miss Collery", "S10"},
    P6 = {"French IB Ab Initio", "12AB/F3", "Miss Corcoran", "C1"},
  },
}

local FRIDAY_A = {
  Reg = {"Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"},
  P1 = {"English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"},
  P2 = {"Physics IB HL", "124H2/P1", "Miss Collery", "S10"},
  P3 = {"Theory of Knowledge", "1206/Tk", "Mr Scott", "M3"},
  P4 = {"Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"},
}

local FRIDAY_B = {
  Reg = {"Mentor", "12RD/Mt", "Miss D'Annunzio", "S4"},
  P1 = {"English Lang and Lit IB SL", "12S4/E2", "Miss McMenamin", "M7"},
  P2 = {"Physics IB HL", "124H2/P1", "Miss Collery", "S10"},
  P3 = {"Islamic Education", "12B/IsIB", "Mr Akhtar", "C8"},
  P4 = {"Chemistry IB SL", "126H1/C1x", "Mrs Dela Cruz", "S6"},
}

-- Times in minutes since midnight.
local TIMES_STANDARD = {
  {code = "Reg", s = 460, e = 480}, {code = "P1", s = 480, e = 540},
  {code = "P2", s = 540, e = 600}, {code = "Break", s = 600, e = 620},
  {code = "P3", s = 620, e = 680}, {code = "P4", s = 680, e = 740},
  {code = "Lunch", s = 740, e = 800}, {code = "P5", s = 800, e = 860},
  {code = "P6", s = 860, e = 920},
}

local TIMES_FRIDAY = {
  {code = "Reg", s = 460, e = 470}, {code = "P1", s = 470, e = 520},
  {code = "P2", s = 520, e = 570}, {code = "Break", s = 570, e = 590},
  {code = "P3", s = 590, e = 640}, {code = "P4", s = 640, e = 690},
}

-- ---------- state (which week is "current", persisted to disk) ----------

local currPath = ""
local mode = "list"
local configured = false
local refWeek, refMondayY, refMondayM, refMondayD

local function statePath()
  return currPath .. "state.txt"
end

local function SaveState()
  local f = io.open(statePath(), "w")
  if f then
    f:write(string.format("%04d-%02d-%02d\n%s\n", refMondayY, refMondayM, refMondayD, refWeek))
    f:close()
  end
end

-- Re-read on every Update(), not just once: SetWeek() may have been called
-- via a *different* measure instance (they don't share Lua globals), so
-- each measure needs to pick the change up from disk on its next cycle.
local function LoadState()
  local f = io.open(statePath(), "r")
  if not f then return false end
  local dateLine = f:read("*l")
  local weekLine = f:read("*l")
  f:close()
  if not (dateLine and weekLine) then return false end
  local y, m, d = dateLine:match("(%d+)-(%d+)-(%d+)")
  if not y then return false end
  refMondayY, refMondayM, refMondayD = tonumber(y), tonumber(m), tonumber(d)
  refWeek = weekLine:gsub("%s+", "")
  return refWeek == "A" or refWeek == "B"
end

-- ---------- date helpers ----------

local function MondayOfTime(t)
  local dt = os.date("*t", t)
  local daysSinceMonday = (dt.wday == 1) and 6 or (dt.wday - 2)
  local mondayTime = t - daysSinceMonday * 86400
  local md = os.date("*t", mondayTime)
  return md.year, md.month, md.day, mondayTime
end

local function ComputeCurrentWeek(year, month, day)
  local t = os.time({year = year, month = month, day = day, hour = 12})
  local _, _, _, thisMonday = MondayOfTime(t)
  local refMonday = os.time({year = refMondayY, month = refMondayM, day = refMondayD, hour = 12})
  local diffDays = math.floor((thisMonday - refMonday) / 86400 + 0.5)
  local weeksDiff = math.floor(diffDays / 7)
  if weeksDiff % 2 == 0 then
    return refWeek
  end
  return (refWeek == "A") and "B" or "A"
end

local function MinToHHMM(totalMin)
  return string.format("%02d:%02d", math.floor(totalMin / 60), totalMin % 60)
end

-- ---------- schedule lookup ----------

local function GetDayPeriods(wday, weekLetter)
  local dayKey = DAY_NAMES[wday]
  local lessons, times
  if dayKey == "Friday" then
    lessons = (weekLetter == "A") and FRIDAY_A or FRIDAY_B
    times = TIMES_FRIDAY
  else
    lessons = COMMON[dayKey]
    times = TIMES_STANDARD
  end
  local result = {}
  for _, t in ipairs(times) do
    table.insert(result, {code = t.code, startMin = t.s, endMin = t.e, lesson = lessons[t.code]})
  end
  return result
end

local function LessonName(p)
  if p.lesson then return p.lesson[1] end
  if p.code == "Reg" then return "Mentor Time" end
  if p.code == "Break" then return "Break" end
  if p.code == "Lunch" then return "Lunch" end
  return "Free Period"
end

-- ASCII-only separator ("-"), never a unicode middle-dot: Rainmeter's
-- String meter garbles non-ASCII bytes returned from Lua (see file header).
local function LessonDetail(p)
  if not p.lesson then return "" end
  local teacher, room = p.lesson[3] or "", p.lesson[4] or ""
  local parts = {}
  if teacher ~= "" then table.insert(parts, teacher) end
  if room ~= "" then table.insert(parts, room) end
  if #parts == 0 then return "" end
  return "  (" .. table.concat(parts, " - ") .. ")"
end

local function BuildStatusLine(periods, nowMin, currentIdx)
  if currentIdx then
    local p = periods[currentIdx]
    return "Now: " .. LessonName(p) .. "  -  ends in " .. (p.endMin - nowMin) ..
        " min (" .. MinToHHMM(p.endMin) .. ")"
  end
  local first, last = periods[1], periods[#periods]
  if nowMin < first.startMin then
    return "School starts at " .. MinToHHMM(first.startMin) .. "  -  " .. LessonName(first)
  end
  if nowMin >= last.endMin then
    return "School day is over. See you tomorrow!"
  end
  for _, p in ipairs(periods) do
    if nowMin < p.startMin then
      return "Next: " .. LessonName(p) .. " at " .. MinToHHMM(p.startMin)
    end
  end
  return ""
end

local function NextSchoolDay(now)
  local daysAhead = (2 - now.wday) % 7
  if daysAhead == 0 then daysAhead = 7 end
  local nextTime = os.time({year = now.year, month = now.month, day = now.day, hour = 12}) + daysAhead * 86400
  return os.date("*t", nextTime)
end

-- ---------- Rainmeter entry points ----------

function Initialize()
  currPath = SKIN:GetVariable("CURRENTPATH")
  mode = string.lower(SELF:GetOption("Mode", "list"))
  configured = LoadState()
end

function SetWeek(letter)
  if letter ~= "A" and letter ~= "B" then return end
  local now = os.time()
  local y, m, d = MondayOfTime(now)
  refWeek, refMondayY, refMondayM, refMondayD = letter, y, m, d
  configured = true
  SaveState()
end

function Update()
  configured = LoadState() or configured

  if not configured then
    if mode == "list" then
      return 0, "Right-click this widget and choose\n'Set Week A' or 'Set Week B'\nto get started."
    end
    return 0, ""
  end

  local now = os.date("*t")
  local weekLetter = ComputeCurrentWeek(now.year, now.month, now.day)
  local dateStr = DAY_NAMES[now.wday] .. ", " .. now.day .. " " .. MONTH_NAMES[now.month] .. " " .. now.year

  if now.wday == 1 or now.wday == 7 then
    if mode == "header" then return 0, dateStr end
    if mode == "week" then return 0, "WEEK " .. weekLetter end
    if mode == "status" then return 0, "Weekend - no lessons today" end
    -- mode == "list": preview the next school day
    local nextDt = NextSchoolDay(now)
    local nextWeek = ComputeCurrentWeek(nextDt.year, nextDt.month, nextDt.day)
    local periods = GetDayPeriods(nextDt.wday, nextWeek)
    local first = periods[1]
    return 0, "Next up: " .. DAY_NAMES[nextDt.wday] .. " " .. nextDt.day .. " " .. MONTH_NAMES[nextDt.month] ..
        " (Week " .. nextWeek .. ")\nFirst: " .. LessonName(first) .. " at " .. MinToHHMM(first.startMin)
  end

  local periods = GetDayPeriods(now.wday, weekLetter)
  local nowMin = now.hour * 60 + now.min
  local currentIdx = nil
  for i, p in ipairs(periods) do
    if nowMin >= p.startMin and nowMin < p.endMin then
      currentIdx = i
      break
    end
  end

  if mode == "header" then return 0, dateStr end
  if mode == "week" then return 0, "WEEK " .. weekLetter end
  if mode == "status" then return 0, BuildStatusLine(periods, nowMin, currentIdx) end

  -- mode == "list"
  local lines = {}
  for i, p in ipairs(periods) do
    local marker = (i == currentIdx) and "* " or "   "
    table.insert(lines, marker .. MinToHHMM(p.startMin) .. "  " .. LessonName(p) .. LessonDetail(p))
  end
  return 0, table.concat(lines, "\n")
end
