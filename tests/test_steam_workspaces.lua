-- Run from the repository root: lua tests/test_steam_workspaces.lua
local clients, moves, opened, events
-- Static rules are checked in Hyprland; these tests exercise event fallback.
o = { window = function() end }
hl = {
  on = function(event, callback)
    events[event] = callback
    if event == "window.open" then opened = callback end
  end,
  get_windows = function() return clients end,
  dsp = { window = { move = function(args) return args end } },
  dispatch = function(args)
    moves[#moves + 1] = args
    args.window.workspace.id = tonumber(args.workspace)
  end,
}

local function reset(existing)
  clients, moves, events = existing or {}, {}, {}
  dofile("scripts/steam-workspaces.lua")
end

local function window(class, workspace)
  return { class = class, workspace = { id = workspace }, mapped = true,
    address = tostring({}) }
end

local function open(class, workspace)
  local w = window(class, workspace)
  clients[#clients + 1] = w
  opened(w)
  return w
end

reset()
open("steam", 1)
open("steam", 4)
open("steam_app_570", 4)
assert(#moves == 3 and moves[1].workspace == "1")
assert(not moves[2].follow and moves[3].workspace == "2" and moves[3].follow)

for _, occupied in ipairs({ 1, 2 }) do
  reset({ window("foot", occupied) })
  local updater = open("SteamUpdater", 4)
  open("steam", 4)
  open("dota2", 4)
  assert(#moves == 1 and updater.workspace.id == 1 and not moves[1].follow,
    "updater must use workspace 1 even when the main session is blocked")
end

reset()
local updater = open("SteamUpdater", 4)
assert(#moves == 1 and updater.workspace.id == 1 and not moves[1].follow,
  "Steam bootstrap updater must move silently to workspace 1")
open("steam", 4)
open("steam_app_570", 4)
assert(#moves == 3 and moves[3].workspace == "2",
  "the updater must participate in the Steam/Dota session")

reset()
open("SteamUpdater", 4)
clients = {} -- Bootstrap exits before the main client opens.
open("steam", 4)
assert(#moves == 2 and moves[2].workspace == "1")

reset({ window("steam", 1) })
open("dota2", 4)
assert(#moves == 0, "reload must not adopt an unchecked existing session")
updater = open("SteamUpdater", 4)
assert(#moves == 1 and updater.workspace.id == 1 and not moves[1].follow,
  "new updater must use workspace 1 after a config reload during a session")

reset()
open("dota2", 2)
open("steamwebhelper", 4)
assert(#moves == 2 and moves[1].workspace == "2" and moves[2].workspace == "1")
open("foot", 1)
open("steam", 4)
assert(#moves == 2, "new unrelated occupants must stop routing")
clients = {}
open("steam", 4)
assert(#moves == 3, "a new empty session must recheck occupancy")
open("steam_app_730", 4)
open("brave-browser", 4)
assert(#moves == 3, "other games and apps must be unaffected")
reset()
local bootstrap = open("", 4)
assert(#moves == 0)
bootstrap.xwayland = true
bootstrap.title = "Updating Steam..."
events["window.title"](bootstrap)
assert(#moves == 1 and bootstrap.workspace.id == 1,
  "late updater title must route an initially unidentified window")
bootstrap.workspace.id = 5
bootstrap.class = "SteamUpdater"
events["window.class"](bootstrap)
assert(#moves == 1 and bootstrap.workspace.id == 5,
  "subsequent metadata changes must not undo manual placement")

reset({ window("foot", 2) })
bootstrap = open("", 4)
bootstrap.xwayland = true
bootstrap.title = "Installing Steam..."
events["window.title"](bootstrap)
assert(#moves == 1 and bootstrap.workspace.id == 1 and not moves[1].follow,
  "late updater title must use workspace 1 even when workspace 2 is occupied")
clients = { bootstrap }
events["window.title"](bootstrap)
assert(#moves == 1, "handled updater must not retry on title changes")

for _, class in ipairs({ "", "steam", "steamwebhelper" }) do
  reset({ window("foot", 1) })
  bootstrap = window(class, 4)
  bootstrap.xwayland = true
  bootstrap.title = "Updating Steam…"
  clients[#clients + 1] = bootstrap
  opened(bootstrap)
  assert(#moves == 1 and bootstrap.workspace.id == 1 and not moves[1].follow,
    "updater title must work with generic Steam classes and a Unicode ellipsis")
end

for _, event in ipairs({ "window.title", "window.class" }) do
  reset({ window("foot", 2) })
  bootstrap = open("steam", 4)
  assert(#moves == 0)
  bootstrap.xwayland = true
  if event == "window.title" then
    bootstrap.title = "Updating Steam..."
  else
    bootstrap.class = "SteamUpdater"
  end
  events[event](bootstrap)
  assert(#moves == 1 and bootstrap.workspace.id == 1,
    "late updater identity must override a blocked generic Steam placement")
  bootstrap.workspace.id = 5
  events[event](bootstrap)
  assert(#moves == 1 and bootstrap.workspace.id == 5,
    "later updater metadata must not undo a manual move")
end

reset({ window("foot", 2) })
local client = open("steam", 4)
clients = { client }
events["window.title"](client)
assert(#moves == 0, "blocked main client must not retry on title changes")

reset()
bootstrap = open("", 4)
bootstrap.class = "SteamUpdater"
events["window.class"](bootstrap)
assert(#moves == 1, "late WM_CLASS must trigger placement")

reset()
local browser = open("brave-browser", 4)
browser.title = "Updating Steam..."
browser.xwayland = true
events["window.title"](browser)
assert(#moves == 0, "browser titles must not match bootstrap fallback")
print("Steam workspace tests passed")
