
# 🜲 Omarchy Configs

Omarchy configs for **dual monitor setups with Dota 2 support and matchmaking enabled**.  
These are my personal system and UI configuration files, tuned for a fast, minimal workflow and reliable gaming experience on Omarchy OS.

---

## 🧭 Overview

Optimized for:
- Dual display (`DP-1` main + `HDMI-A-1` secondary)
- Clean workspace distribution across both monitors
- NVIDIA Vulkan setup for Dota 2 matchmaking stability
- LATAM keyboard layout with Caps as Compose key
- Brave browser and Steam integration for daily use and gaming

---

## 🖥️ Dual Monitor Configuration

This replaces the default single-monitor Omarchy layout with a **two-display setup**, where the main screen (DP-1) runs at 2560×1440 @ 120 Hz and the secondary (HDMI-A-1) runs at 1366×768 @ 60 Hz, positioned to the right.

```ini
# Filename: ~/.config/hypr/hyprland.conf

monitor=DP-1,2560x1440@120,0x0,1
monitor=HDMI-A-1,1366x768@60,2560x0,1
````

---

## 🧩 Hyprland Highlights

* Workspaces 1–4 bound to **DP-1**
* Workspaces 5–8 bound to **HDMI-A-1**
* Persistent dual-monitor layout for consistent window placement
* LATAM keyboard layout, Caps = Compose key

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
* Most display/input changes require relaunching Hyprland.
* Keep your configs versioned — this repo serves as your baseline backup.

---

**Author:** Luis Vásquez

