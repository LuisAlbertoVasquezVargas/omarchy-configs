
# 🜲 Omarchy Configs

Omarchy configs for **dual monitor setups with Dota 2 support and matchmaking enabled**.  
These are my personal system and UI configuration files, tuned for a fast, minimal workflow and reliable gaming experience on Omarchy OS.

---

## 🧭 Overview

Optimized for:
- Dual display (`DP-1` main + `HDMI-A-1` secondary)
- 6 workspaces distributed evenly across both monitors
- NVIDIA Vulkan environment for Dota 2 matchmaking stability
- Brave browser and Steam integration for daily use and gaming

---

## 🖥️ Dual Monitor Configuration

This replaces the default single-monitor Omarchy layout with a **two-display setup** and six workspace assignments.  
The main display (`DP-1`) runs at **2560×1440 @ 120 Hz**, and the secondary (`HDMI-A-1`) runs at **1366×768 @ 60 Hz**, positioned to the right.

```ini
# Filename: ~/.config/hypr/monitors.conf

monitor=DP-1,2560x1440@120,0x0,1
monitor=HDMI-A-1,1366x768@60,2560x0,1
````

Workspaces are explicitly mapped in the main Hyprland config:

```ini
# Filename: ~/.config/hypr/hyprland.conf

# Primary monitor (DP-1): workspaces 1–3
workspace=1,monitor:DP-1
workspace=2,monitor:DP-1
workspace=3,monitor:DP-1

# Secondary monitor (HDMI-A-1): workspaces 4–6
workspace=4,monitor:HDMI-A-1
workspace=5,monitor:HDMI-A-1
workspace=6,monitor:HDMI-A-1
```

---

## 🧩 Hyprland Highlights

* Modular structure sourcing Omarchy defaults and user overrides
* Explicit `monitors.conf` import for cleaner separation of display logic
* 6-workspace layout evenly split between both monitors
* Custom Logitech G300s mouse configuration (sensitivity 0.20, adaptive acceleration)

---

## 🧰 Waybar Setup

Includes:

* Workspace icons with active indicator
* System modules (network, audio, battery, CPU)
* Clock and update indicators centered

Config location:
`~/.config/waybar/config.jsonc`

---

## 🎮 Gaming Support

### Steam / Dota 2

If matchmaking fails or VAC can’t verify your machine, launch Dota 2 with:

```bash
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid -safe
```

### Essential Packages

```bash
sudo pacman -S steam
yay -S brave-bin
```

---

## 🧠 Quick Notes

* Check monitors: `hyprctl monitors`
* Relaunch Hyprland after changes (**Super + Esc → Relaunch**)
* Keep your configs versioned — this repo serves as your baseline backup.

---

**Author:** Luis Vásquez

