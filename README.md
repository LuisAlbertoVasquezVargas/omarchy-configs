# Omarchy Desktop Config

Personal configuration for Omarchy Quattro.

## Target System

- CPU: AMD Ryzen 7 5700X
- GPU: NVIDIA GeForce RTX 3060 Ti

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

The theme is installed under `~/.config/omarchy/themes/ghost-pastel`. Switch back to it later with:

```bash
omarchy theme set "Ghost Pastel"
```

## Brave

```bash
omarchy install browser brave
omarchy default browser brave
```

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

## Compact Window Layout

Path: `~/.config/hypr/looknfeel.lua`

```lua
hl.config({
  general = {
    gaps_in = 0,
    gaps_out = 0,
    border_size = 0,
  },
})
```

## Seven Workspaces

Configure Hyprland to use only workspaces 1-7 across both desktop monitors. When both displays are connected, workspaces 1-4 belong to `DP-1` and workspaces 5-7 belong to `HDMI-A-1`, matching the previous desktop layout. When only one display is connected, it receives all seven workspaces.

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

for workspace = 1, 7 do
  local rule = {
    workspace = tostring(workspace),
    persistent = true,
  }

  if secondary_monitor and workspace >= 5 then
    rule.monitor = secondary_monitor
    if workspace == 5 then
      rule.default = true
    end
  elseif primary_monitor then
    rule.monitor = primary_monitor
    if workspace == 1 then
      rule.default = true
    end
  end

  hl.workspace_rule(rule)
end
```

Run `hyprctl reload` after connecting or disconnecting a display so the monitor assignments are reevaluated.

### Disable workspace 8-10 shortcuts

Omarchy provides numeric bindings for workspaces 1-10 by default. Disable switching to or moving windows to workspaces 8-10.

Path: `~/.config/hypr/bindings.lua`

```lua
-- Limit numeric workspace bindings to the seven persistent workspaces.
for workspace = 8, 10 do
  local key = "code:" .. tostring(workspace + 9)

  hl.unbind("SUPER + " .. key)
  hl.unbind("SUPER + SHIFT + " .. key)
  hl.unbind("SUPER + SHIFT + ALT + " .. key)
end
```

### Reload and validate Hyprland

```bash
hyprctl reload
hyprctl configerrors
```

`hyprctl configerrors` should return no output.

### Remove an existing workspace 8

If a workspace above 7 was already created, check whether it contains any windows:

```bash
hyprctl -j clients | jq \
  '[.[] | select(.workspace.id > 7 and .workspace.id <= 10) |
  {address, class, title, workspace: .workspace.id}]'
```

Move each listed window to workspace 7, replacing the example address with the address reported by the previous command:

```bash
hyprctl dispatch \
  'hl.dsp.window.move({ workspace = "7", follow = false, window = "address:0xWINDOW_ADDRESS" })'
```

Window addresses change between sessions and must not be hardcoded.

Activate workspace 7 on `HDMI-A-1` and reload:

```bash
hyprctl dispatch 'hl.dsp.focus({ workspace = "7" })'
hyprctl reload
```

### Verify the result

```bash
hyprctl -j workspaces | jq \
  'sort_by(.id) | map({id, monitor, windows})'
```

The workspace IDs should be exactly 1-7, with workspaces 1-4 on `DP-1` and 5-7 on `HDMI-A-1`.

Confirm that no bindings for workspaces 8-10 remain:

```bash
hyprctl -j binds | jq \
  '[.[] |
  select((.description // "") |
  test("workspace (8|9|10)$"; "i")) |
  .description]'
```

The expected result is:

```text
[]
```

## Experimental: Codex Workspace Shortcut

Path: `~/.config/hypr/bindings.lua`

```lua
local function codex_workspace(key, workspace, path)
  local rules = { workspace = workspace .. " silent" }

  o.bind(key, "Codex + terminal (workspace " .. workspace .. ")", hl.dsp.focus({ workspace = workspace }))
  o.bind(key, nil, hl.dsp.exec_cmd(o.launch('xdg-terminal-exec --dir="' .. path .. '" codex -C "' .. path .. '"'), rules))
  o.bind(key, nil, hl.dsp.exec_cmd(o.launch('xdg-terminal-exec --dir="' .. path .. '"'), rules))
end

codex_workspace("SUPER + Prior", "2", os.getenv("HOME") .. "/Projects/MOVER-research-materials") -- Page Up / Re Pág
codex_workspace("SUPER + Next", "3", os.getenv("HOME") .. "/Projects/shopping-list-ui") -- Page Down / Av Pág
```

## Experimental: NVIDIA GPU Driver Update

Update Omarchy, the kernel, and NVIDIA packages together:

```bash
omarchy update
omarchy system reboot
nvidia-smi
```

## Apply Configs

> **TODO:** Adapt `scripts/apply_configs.py` for Omarchy Quattro.
