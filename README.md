# Omarchy Desktop Config

Personal configuration for Omarchy Quattro.

## Target System

- CPU: AMD Ryzen 7 5700X
- GPU: NVIDIA GeForce RTX 5060 Ti
- Primary display: Samsung LS27DG30X, currently running at 1920x1080 at 60 Hz (`DP-1`)
- Secondary display: BenQ G610HDAL, 1366x768 at 59.79 Hz (`HDMI-A-1`; currently disconnected)

<!-- TODO: Describe additional hardware components. -->

## Clone This Repository

```bash
cd ~/Projects
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs.git
cd omarchy-configs
```

## Ghost Pastel Theme

Install and activate the Ghost Pastel community theme:

```bash
omarchy theme install https://github.com/row-huh/omarchy-ghost-pastel-theme
```

## Brave

Install Brave:

```bash
omarchy install browser brave
```

Then set Brave as the default browser:

```bash
omarchy default browser brave
```

### Setup

1. Open Brave and set it as the default browser.
2. Go to **Settings → Appearance → Theme** and select **Dark**.
3. Go to **Settings → Sync** and select **I have a Sync Code**.
4. On your smartphone:
   1. Open Brave.
   2. Go to **Settings → Sync**.
   3. Select **Add a new device**.
   4. Scan the QR code displayed on your desktop.
5. Wait for synchronization to complete, including bookmarks, passwords, history, tabs, and other data.
6. Go to **Settings → Search engine** and set:
   - **Normal:** Google
   - **Private:** Google
7. Go to **Settings → System** and disable **Use graphics acceleration when available**.

## Ghostty

> **TODO:** Although Ghostty was used on the previous Omarchy setup, test both Ghostty and Foot on Omarchy Quattro before choosing and documenting the default terminal.

## WhatsApp

Nothing to install. WhatsApp comes preinstalled as an Omarchy web app.

## Slack

Install Slack as an Omarchy web app:

```bash
omarchy webapp install "Slack" "https://app.slack.com/client" ""
```

The empty icon argument lets Omarchy download Slack's icon automatically. Open the app launcher with `Super + Space`, search for **Slack**, and sign in to the workspace. Allow notifications when Brave prompts for permission.

Because Brave is the configured default browser, Slack opens in a standalone Brave web-app window.

## Discord

Nothing to install. Discord comes preinstalled as an Omarchy web app. Open the app launcher with `Super + Space`, search for **Discord**, and sign in.

Because Brave is the configured default browser, Discord opens in a standalone Brave web-app window.

## Zathura

```bash
omarchy pkg add zathura zathura-pdf-mupdf
xdg-mime default org.pwmt.zathura.desktop application/pdf
```

## Neovim

Show hidden, filtered, and Git-ignored items in Neo-tree by default while keeping their filtered styling.

Path: `~/.config/nvim/lua/plugins/neo-tree.lua`

```lua
return {
  {
    "nvim-neo-tree/neo-tree.nvim",
    opts = {
      filesystem = {
        filtered_items = {
          visible = true,
        },
      },
    },
  },
}
```

Restart Neovim or reopen Neo-tree to apply the change.

## Steam

```bash
omarchy install gaming steam
```

### Steam scaling and window layout (1920x1080)

Keep both the GTK application scale and Hyprland monitor scale at `1` on the
1920x1080 Samsung display. This gives applications the correct base display scale, but
Steam also has its own Chromium UI scaling control that must be disabled below.

Path: `~/.config/hypr/monitors.lua`

```lua
local omarchy_gdk_scale = 1
local omarchy_monitor_scale = 1

hl.env("GDK_SCALE", tostring(omarchy_gdk_scale))
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = omarchy_monitor_scale })
```

Place the main client (1280x900) and Friends panel (520x900) side by side on the
primary Samsung display, with 40-pixel outer margins and a 40-pixel gap. These
sizes replace the smaller 920x560 and 386x560 layout used on the BenQ. This layout
is intended for the Samsung at 1920x1080 and scale 1.

Steam runs through XWayland and applies its own geometry late in startup. Static
window rules place both windows correctly at first, but the main window can
expand again after the client finishes loading. Keep the static rules for the
initial placement, then re-apply the geometry at several startup checkpoints.

Path: `~/.config/hypr/hyprland.lua`

```lua
-- Keep Steam's floating windows comfortable on the 1920x1080 Samsung display.
-- Steam applies its own X11 geometry late in startup, so set the initial rules
-- and then re-apply them at a few checkpoints while the client finishes loading.
o.window({ class = "^steam$", title = "^Steam$", xwayland = true }, {
  move = { 40, 103 },
  size = { 1280, 900 },
})
o.window({ class = "^steam$", title = "^Friends List$", xwayland = true }, {
  move = { 1360, 103 },
  size = { 520, 900 },
})

local steam_window_geometries = {
  ["Steam"] = { x = 40, y = 103, width = 1280, height = 900 },
  ["Friends List"] = { x = 1360, y = 103, width = 520, height = 900 },
}
local steam_geometry_delays = { 1000, 5000, 15000, 30000 }

local function enforce_steam_geometry(address, initial_title, geometry)
  local window = hl.get_window("address:" .. address)

  if not window or window.class ~= "steam" or window.initial_title ~= initial_title then
    return
  end

  hl.dispatch(hl.dsp.window.resize({
    x = geometry.width,
    y = geometry.height,
    relative = false,
    window = window,
  }))
  hl.dispatch(hl.dsp.window.move({
    x = geometry.x,
    y = geometry.y,
    relative = false,
    window = window,
  }))
end

hl.on("window.open", function(window)
  local initial_title = window.initial_title or window.title
  local geometry = steam_window_geometries[initial_title]

  if window.class ~= "steam" or not window.xwayland or not geometry then
    return
  end

  local address = window.address

  for _, delay_ms in ipairs(steam_geometry_delays) do
    hl.timer(function()
      enforce_steam_geometry(address, initial_title, geometry)
    end, { timeout = delay_ms, type = "oneshot" })
  end
end)
```

The delayed callbacks use Hyprland's `window.open` event and one-shot timers.
Each callback resolves the original window address again before changing it,
so closing Steam during startup safely turns the remaining callbacks into
no-ops.

Reload and validate Hyprland:

```bash
hyprctl reload
hyprctl configerrors
```

If the desktop session was started before changing `GDK_SCALE`, save any open
work and relaunch the Omarchy session (or log out and back in) so newly launched
applications inherit `GDK_SCALE=1`.

Steam can still double the contents inside its correctly sized XWayland windows.
Disable Steam's separate automatic DPI scaling:

1. Open **Steam → Settings → Interface**.
2. Turn off **Scale text and icons to match monitor settings (requires restart)**.
3. Accept Steam's restart prompt.

On the tested August 2026 client, `STEAM_FORCE_DESKTOPUI_SCALING=1` and
`-forcedesktopscaling 1.0` were ignored. Turning off the Interface option changed
Steam's Chromium display from `683x384, scale=2` to `1366x768, scale=1`.

Verify Steam's internal UI scale from its Chromium log:

```bash
rg 'Display\[[0-9]+\].*scale=' \
  ~/.local/share/Steam/logs/webhelper_gpu.txt | tail -n 1
```

On the Samsung, the latest line should report `bounds=[0,0 1920x1080]` and `scale=1`.

Verify that both windows use the expected geometry:

```bash
hyprctl clients -j | jq \
  '[.[] | select(.class == "steam" and
    (.title == "Steam" or .title == "Friends List")) |
    {at, size, title}]'
```

Wait at least 30 seconds after launching Steam, then verify that the main window
reports `1280x900` at `[40, 103]` and Friends List reports `520x900` at
`[1360, 103]`.

Dota 2 launch options:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid
```

## Clock Format

Migrates the previous Waybar clock format to Omarchy Shell.

Path: `~/.config/omarchy/shell.json`

```json
{
  "id": "omarchy.clock",
  "format": "dd MMM ddd · 'W'ww · HH:mm",
  "formatAlt": "dd MMM ddd · 'W'ww · HH:mm",
  "verticalFormat": "HH\n—\nmm"
}
```

## Compact Window Layout and Focus Border

Path: `~/.config/hypr/looknfeel.lua`

```lua
local function load_current_theme_colors()
  local colors = {}
  local home = os.getenv("HOME")

  if not home then
    return colors
  end

  local file = io.open(home .. "/.local/state/omarchy/current/theme/colors.toml", "r")

  if not file then
    return colors
  end

  for line in file:lines() do
    local name, value = line:match('^%s*([%w_]+)%s*=%s*"([^"]+)"')

    if name then
      colors[name] = value
    end
  end

  file:close()
  return colors
end

local function to_hypr_color(value)
  if not value then
    return nil
  end

  local hex = value:match("^#(%x+)$")

  if hex and #hex == 6 then
    return "rgb(" .. hex .. ")"
  elseif hex and #hex == 8 then
    return "rgba(" .. hex .. ")"
  end

  return value
end

local theme_colors = load_current_theme_colors()
local active_border_color = to_hypr_color(theme_colors.color6 or theme_colors.accent)
local inactive_border_color = to_hypr_color(theme_colors.background)
local general = {
  gaps_in = 0,
  gaps_out = 0,
  border_size = 3,
}
local config = { general = general }

if active_border_color and inactive_border_color then
  general.col = {
    active_border = active_border_color,
    inactive_border = inactive_border_color,
  }

  config.group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  }
end

hl.config(config)
```

This keeps the zero-gap layout while adding a 3-pixel border that makes the
focused window easy to identify. The focused border uses the current Omarchy
theme's `color6`, falling back to `accent`, while inactive borders use the
theme's `background`. The same colors are applied to grouped windows.

Colors are read from `~/.local/state/omarchy/current/theme/colors.toml` whenever
Hyprland reloads, so changing themes also changes the borders without a
theme-specific override. If the required colors are unavailable, the compact
layout and border width still apply while Omarchy's generated border colors are
left unchanged.

Reload and validate the configuration:

```bash
hyprctl reload
hyprctl configerrors
```

`hyprctl configerrors` should return no output.

## Ten Workspaces

Keep workspaces 1-10 persistent with Omarchy's default numeric shortcuts enabled.
This follows the laptop setup: when both desktop monitors are connected, workspace
7 belongs to the secondary BenQ (`HDMI-A-1`), and workspaces 1-6 and 8-10 belong to
the primary Samsung (`DP-1`). When only one monitor is connected, it receives all
ten workspaces.

### Create the persistent workspaces

Path: `~/.config/hypr/hyprland.lua`

```lua
local connected_monitors = {}
local fallback_monitor

for _, monitor in ipairs(hl.get_monitors()) do
  connected_monitors[monitor.name] = true
  fallback_monitor = fallback_monitor or monitor.name
end

local primary_monitor = connected_monitors["DP-1"] and "DP-1" or fallback_monitor
local secondary_monitor = connected_monitors["HDMI-A-1"] and "HDMI-A-1" or nil

if secondary_monitor == primary_monitor then
  secondary_monitor = nil
end

for workspace = 1, 10 do
  local rule = {
    workspace = tostring(workspace),
    persistent = true,
  }

  if secondary_monitor and workspace == 7 then
    rule.monitor = secondary_monitor
    rule.default = true
  elseif primary_monitor then
    rule.monitor = primary_monitor
    if workspace == 1 then
      rule.default = true
    end
  end

  hl.workspace_rule(rule)
end
```

Replace the previous seven-workspace block with this one. In
`~/.config/hypr/bindings.lua`, remove the old loop that calls `hl.unbind` for
workspaces 8-10 so Omarchy's default shortcuts remain enabled:

- `Super + 1` through `Super + 9`, and `Super + 0`: switch to workspaces 1-10.
- Add `Shift`: move the focused window to that workspace and follow it.
- Add `Shift + Alt`: move the focused window without following it.

### Reload and validate Hyprland

Run these after applying the configuration or connecting/disconnecting a monitor
so the monitor assignments are reevaluated:

```bash
hyprctl reload
hyprctl configerrors
```

`hyprctl configerrors` should return no output.

### Verify the result

```bash
hyprctl -j workspaces | jq \
  'sort_by(.id) | map({id, monitor, windows, ispersistent})'
```

The workspace IDs should be exactly 1-10, all persistent. With both displays
connected, only workspace 7 should be on `HDMI-A-1`; the rest should be on `DP-1`.
With only the Samsung connected, all ten should be on `DP-1`.

Check that switching, moving, and silently moving shortcuts are present for all
ten workspaces:

```bash
hyprctl -j binds | jq \
  '[.[] | select((.description // "") |
    test("^(Switch to|Move window to|Move window silently to) workspace ([1-9]|10)$")) |
    .description]'
```

The result should contain 30 bindings: three actions for each workspace.

## Experimental: NVIDIA GPU Driver Update

Update Omarchy, the kernel, and NVIDIA packages together:

```bash
omarchy update
omarchy system reboot
nvidia-smi
```

## Apply Configs

> **TODO:** Adapt `scripts/apply_configs.py` for Omarchy Quattro.
