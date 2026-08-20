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

## Brave

```bash
omarchy install browser brave
omarchy default browser brave
```

## WhatsApp

> **TODO:** Choose between Ferdium and Quattro's built-in WhatsApp web app.

## Slack

> **TODO:** Choose between Ferdium and a Quattro web app. Disable GPU acceleration persistently before using Slack through Ferdium.

## Zathura

```bash
omarchy pkg add zathura zathura-pdf-mupdf
xdg-mime default org.pwmt.zathura.desktop application/pdf
```

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

Path: `~/.config/hypr/hyprland.lua`

```lua
for workspace = 1, 7 do
  hl.workspace_rule({
    workspace = tostring(workspace),
    persistent = true,
  })
end
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
