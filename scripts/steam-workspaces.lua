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
o.window({
  class = "(?i)^(steam|steamwebhelper)?$",
  title = "(?i)^(Updating|Installing) Steam([.]*|…)$",
  xwayland = true,
}, { workspace = "1 silent" })

local function is_updater(window)
  local class = (window.class or ""):lower()
  if class == "steamupdater" then return true end
  -- The bootstrap UI can publish its title before its WM_CLASS.
  local title = (window.title or ""):lower():gsub("…$", ""):gsub("%.+$", "")
  return window.xwayland and (class == "" or class == "steam" or class == "steamwebhelper")
    and (title == "updating steam" or title == "installing steam")
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

hl.on("window.open", place)
hl.on("window.class", place)
hl.on("window.title", place)
hl.on("window.close", function(window)
  handled[window.address] = nil
end)

-- Do not adopt existing windows when config reloads during a game/session.
for _, window in ipairs(hl.get_windows()) do
  handled[window.address] = "existing"
end
