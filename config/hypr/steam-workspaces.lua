-- config/hypr/steam-workspaces.lua

do
  local enabled = false
  local handled = {}

  o.window({ class = "(?i)^steamupdater$", xwayland = true }, {
    workspace = "1 silent",
  })
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
    if previous and not (previous == "client" and updater) then return end
    local target = destination(window)
    if not target then return end
    handled[window.address] = updater and "updater" or "client"

    local other_related = false
    local occupied = false
    local unrelated = false
    for _, other in ipairs(hl.get_windows()) do
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

  for _, window in ipairs(hl.get_windows()) do
    handled[window.address] = "existing"
  end
end
