
# 🜲 Omarchy Configs

Omarchy configs for **dual monitor setups with Dota 2 support and matchmaking enabled**.  
These are my personal system and UI configuration files tuned for a fast, minimal workflow and reliable gaming experience on Omarchy OS.

---

## 🧭 Overview

Optimized for:
- Dual display (`DP-1` main + `HDMI-A-1` secondary)
- Clean workspace distribution across both monitors
- NVIDIA Vulkan setup for Dota 2 matchmaking stability
- LATAM keyboard layout and NumLock enabled by default
- Brave browser and Steam integration for daily use and gaming

---

## ⚙️ Setup Instructions

### 1. Clone this repository
```bash
cd ~/projects
git clone https://github.com/<your-username>/omarchy-configs.git
cd omarchy-configs
````

### 2. Copy configs to your system

```bash
mkdir -p ~/.config/hypr ~/.config/waybar
cp -r .config/hypr/* ~/.config/hypr/
cp -r .config/waybar/* ~/.config/waybar/
```

Assumes:

* `DP-1` → 2560x1440 @ 120Hz
* `HDMI-A-1` → 1366x768 @ 60Hz

Relaunch Hyprland after copying (Super + Esc → Relaunch).

---

## 🧩 Hyprland Highlights

* Workspaces 1–4 bound to **DP-1**
* Workspaces 5–8 bound to **HDMI-A-1**
* `latam` keyboard layout, Caps = Compose key
* Persistent dual-monitor setup for consistent window placement

---

## 🧰 Waybar Setup

Includes:

* Workspace icons with active indicator
* System status modules (network, audio, battery, CPU)
* Clock and update indicators centered

Config location:
`~/.config/waybar/config.jsonc`

---

## 🎮 Gaming Support

### Steam / Dota 2

Use this launch command if matchmaking fails or VAC can’t verify your machine:

```bash
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid -safe
```

### Essential packages

```bash
sudo pacman -S steam
yay -S brave-bin
```

---

## 🧠 Quick Notes

* Check monitor info: `hyprctl monitors`
* Most display/input changes require a Hyprland relaunch.
* Keep your configs versioned — this folder can serve as your backup baseline.

---

**Author:** Luis Vásquez

---
```


