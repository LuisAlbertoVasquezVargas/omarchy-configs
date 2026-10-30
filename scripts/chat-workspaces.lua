-- Route newly opened web apps only when their destination is empty.
-- Workspace 10 is the workspace selected by Super+0.
local handled = {}
local targets = {
  { prefix = "brave-web.whatsapp.com__", workspace = 10 },
  { prefix = "brave-app.slack.com__", workspace = 9 },
  { prefix = "brave-discord.com__", workspace = 8 },
}

local function place(window)
  if not window.mapped or handled[window.address] then return end
  local class = (window.class or ""):lower()
  local target
  for _, app in ipairs(targets) do
    if class:sub(1, #app.prefix) == app.prefix then
      target = app.workspace
      break
    end
  end
  if not target then return end
  -- Decide once, including when occupied: later title changes must not move it.
  handled[window.address] = true
  for _, other in ipairs(hl.get_windows()) do
    if other.mapped and other.address ~= window.address
      and other.workspace and other.workspace.id == target then
      return
    end
  end
  hl.dispatch(hl.dsp.window.move({
    window = window, workspace = tostring(target), follow = false,
  }))
end

hl.on("window.open", place)
hl.on("window.class", place)
hl.on("window.close", function(window) handled[window.address] = nil end)

-- Reloading must not relocate existing windows.
for _, window in ipairs(hl.get_windows()) do
  handled[window.address] = true
end
