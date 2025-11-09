
# 🜲 Omarchy Configs

Omarchy configs for **dual monitor setups with Dota 2 support and matchmaking enabled**.  
These are my personal system and UI configuration files, tuned for a fast, minimal workflow and reliable gaming experience on Omarchy OS.

**Motivation:**  
After experimenting with various Wayland setups, I wanted a stable configuration that handles dual monitors cleanly, feels consistent with Windows pointer precision, and allows Dota 2 matchmaking to work natively without VAC issues.  
This setup aims to keep Omarchy lightweight yet polished — ready for both productivity and competitive gaming.

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

# Input devices
device {
    name = logitech-g300s-optical-gaming-mouse
    sensitivity = 0.20
    accel_profile = adaptative
}
```

The input device section fine-tunes pointer behavior for the **Logitech G300s** mouse.
This setup approximates the feel of **Windows “pointer speed = 13” with “Enhance pointer precision = enabled”**, giving smoother tracking and similar cursor acceleration under Hyprland.

---

## ⚙️ Extra Autostart Processes

These commands are executed automatically on startup to ensure each workspace is initialized and attached to its corresponding monitor.

```ini
# Filename: ~/.config/hypr/autostart.conf

exec = hyprctl dispatch workspace 1
exec = hyprctl dispatch movetoworkspace 1,DP-1
exec = hyprctl dispatch workspace 2
exec = hyprctl dispatch movetoworkspace 2,DP-1
exec = hyprctl dispatch workspace 3
exec = hyprctl dispatch movetoworkspace 3,DP-1
exec = hyprctl dispatch workspace 4
exec = hyprctl dispatch movetoworkspace 4,HDMI-A-1
exec = hyprctl dispatch workspace 5
exec = hyprctl dispatch movetoworkspace 5,HDMI-A-1
exec = hyprctl dispatch workspace 6
exec = hyprctl dispatch movetoworkspace 6,HDMI-A-1
```

---

## 🧰 Waybar Setup

The default Omarchy Waybar configuration supports five workspaces.
This setup updates the `persistent-workspaces` array to support **six workspaces**, matching the dual-monitor Hyprland layout.

```jsonc
# Filename: ~/.config/waybar/config.jsonc

"persistent-workspaces": {
  "1": [],
  "2": [],
  "3": [],
  "4": [],
  "5": [],
  "6": []
}
```

This ensures all six workspaces are consistently displayed in the Waybar interface.

---

## 🎮 Gaming Support

Dota 2 runs best **natively**, without additional wrappers such as Gamescope or Proton.
While these wrappers will still launch the game correctly, **secure features like matchmaking will be unavailable** — you’ll be limited to **demo mode and local lobbies** only.
Running the native Linux version avoids this issue entirely, as **VAC verification always fails under wrappers**.

If you must use custom Vulkan or debugging settings, the following command can still be used:

```bash
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid -safe
```

### Explanation of Flags

* **`-console`** → Enables the developer console inside Dota 2 for custom commands or diagnostics.
* **`-novid`** → Skips the Valve intro video during launch, speeding up startup time.
* **`-safe`** → Launches the game in safe mode, using default settings to recover from crashes or bad configs.

---

## 💿 Installing Steam and Brave

### Steam (from official Arch repositories)

```bash
sudo pacman -S steam
```

### Brave Browser (via AUR)

```bash
yay -S brave-bin
```

Once installed, both integrate seamlessly under Omarchy and Wayland.

---

**Author:** Luis Vásquez

