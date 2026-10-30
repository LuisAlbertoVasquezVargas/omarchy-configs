local next_address = 0
local clients, moves, events
hl = {
  on = function(event, fn) events[event] = fn end,
  get_windows = function() return clients end,
  dsp = { window = { move = function(args) return args end } },
  dispatch = function(args)
    moves[#moves + 1] = args
    args.window.workspace.id = tonumber(args.workspace)
  end,
}
local function window(class, workspace)
  next_address = next_address + 1
  return { class = class, workspace = { id = workspace }, mapped = true, address = tostring(next_address) }
end
local function reset(existing)
  clients, moves, events = existing or {}, {}, {}
  dofile("scripts/chat-workspaces.lua")
end
for class, target in pairs({
  ["brave-web.whatsapp.com__-Default"] = 10,
  ["brave-app.slack.com__client-Default"] = 9,
  ["brave-discord.com__channels_@me-Profile_1"] = 8,
}) do
  reset()
  local app = window(class, 4)
  clients = { app }
  events["window.open"](app)
  assert(#moves == 1 and app.workspace.id == target and not moves[1].follow)
  app.workspace.id = 5
  events["window.class"](app)
  assert(#moves == 1, "manual move must be preserved")

  reset({ window("foot", target) })
  app = window(class, 4)
  clients[#clients + 1] = app
  events["window.open"](app)
  assert(#moves == 0, "occupied destination must block routing")
  clients = { app }
  events["window.class"](app)
  assert(#moves == 0, "blocked placement must not retry")

  reset()
  app = window("", 4)
  clients = { app }
  events["window.open"](app)
  app.class = class
  events["window.class"](app)
  assert(#moves == 1, "late identity must route app")

  reset({ app })
  events["window.class"](app)
  assert(#moves == 0, "reload must preserve existing windows")
end
reset()
local browser = window("brave-browser", 4)
browser.title = "WhatsApp Slack Discord"
clients = { browser }
events["window.open"](browser)
assert(#moves == 0, "browser tabs must stay unaffected")
print("Chat workspace tests passed")
