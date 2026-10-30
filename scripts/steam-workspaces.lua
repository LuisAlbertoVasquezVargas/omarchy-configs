-- Always open Steam's updater on workspace 1. Reserve workspaces 1 and 2 for
-- the main Steam / Dota session only when both are empty at session startup.
-- Loaded by ~/.config/hypr/hyprland.lua after the Steam geometry rules.
local enabled = false
local handled = {}

-- Apply placement before the first frame, rather than moving the updater only
-- after it has opened on the launcher's workspace.
o.window({ class = "(?i)^steamupdater$", xwayland = true }, {
  workspace = "1 silent",
})
-- The October 2026 xwin updater has no WM_CLASS and calls itself just Steam.
-- Match that precise combination before mapping, and keep the current focus.
o.window({ class = "^$", title = "(?i)^steam$", xwayland = true }, {
  workspace = "1 silent",
  no_initial_focus = true,
})
o.window({
  class = "(?i)^(steam|steamwebhelper)?$",
  title = "(?i)^\\s*(Updating|Installing) Steam([.]*|…)\\s*$",
  xwayland = true,
}, { workspace = "1 silent" })

local function is_updater(window)
  local class = (window.class or ""):lower()
  local initial_class = (window.initial_class or ""):lower()
  if class == "steamupdater" or initial_class == "steamupdater" then return true end
  if window.xwayland and class == "" and
    ((window.title or ""):lower() == "steam" or (window.initial_title or ""):lower() == "steam") then
    return true
  end
  local function updater_title(value)
    local title = (value or ""):lower():match("^%s*(.-)%s*$")
    title = title:gsub("…$", ""):gsub("%.+$", ""):match("^%s*(.-)%s*$")
    return title == "updating steam" or title == "installing steam"
  end
  -- Bootstrap metadata can arrive in stages, and its current title may change.
  return window.xwayland and (class == "" or class == "steam" or class == "steamwebhelper")
    and (updater_title(window.title) or updater_title(window.initial_title))
end

local function destination(window)
  local class = (window.class or ""):lower()
  if class == "steam_app_570" or class == "dota2" or class == "dota 2" then
    return 2
  end
  if class == "steam" or class == "steamwebhelper" or is_updater(window) then
    return 1
  end
end

local function place(window)
  if not window.mapped then return end
  local updater = is_updater(window)
  local previous = handled[window.address]
  -- A generic Steam window can identify itself as the updater later. Allow
  -- that one promotion, but never undo a manual move after updater placement.
  if previous and not (previous == "client" and updater) then return end
  local target = destination(window)
  if not target then return end
  handled[window.address] = updater and "updater" or "client"

  local other_related = false
  local occupied = false
  local unrelated = false
  for _, other in ipairs(hl.get_windows()) do
    -- window.open fires after mapping: ignore the window being placed.
    if other.mapped and other.address ~= window.address then
      local related = destination(other) ~= nil
      other_related = other_related or related
      local id = other.workspace and other.workspace.id
      if id == 1 or id == 2 then
        occupied = true
        unrelated = unrelated or not related
      end
    end
  end

  if not other_related then
    enabled = not occupied
  elseif unrelated then
    -- Stop routing if another application takes either workspace mid-session.
    enabled = false
  end

  if enabled or updater then
    hl.dispatch(hl.dsp.window.move({
      window = window,
      workspace = tostring(target),
      follow = target == 2,
    }))
  end
end

hl.on("window.open", function(window)
  place(window)
  -- Resolve again after mapping; do not retain a stale event snapshot.
  local address = window.address
  for _, delay in ipairs({ 100, 500, 1500, 3000 }) do
    hl.timer(function()
      local current = hl.get_window("address:" .. address)
      if current then place(current) end
    end, { timeout = delay, type = "oneshot" })
  end
end)
hl.on("window.class", place)
hl.on("window.title", place)
hl.on("window.close", function(window)
  handled[window.address] = nil
end)

-- Do not adopt existing windows when config reloads during a game/session.
for _, window in ipairs(hl.get_windows()) do
  handled[window.address] = "existing"
end
