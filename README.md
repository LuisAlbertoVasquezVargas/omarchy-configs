
# 🜲 Omarchy Configs

Omarchy configs for **dual monitor setups with Dota 2 support and matchmaking enabled**.
These are my personal system and UI configuration files, tuned for a fast, minimal workflow and reliable gaming experience on Omarchy OS.

**Motivation:**
After experimenting with various Wayland setups, I wanted a stable configuration that handles dual monitors cleanly, feels consistent with Windows pointer precision, and allows Dota 2 matchmaking to work natively without VAC issues.
This setup was built and tested on an **AMD Ryzen 7 5700X** paired with an **NVIDIA GeForce GTX 1650 SUPER**, aiming to keep Omarchy lightweight yet polished — ready for both productivity and competitive gaming.

---

## 🧭 Overview

Optimized for:

* Dual display (`DP-1` main + `HDMI-A-1` secondary)
* 6 workspaces distributed evenly across both monitors
* NVIDIA Vulkan environment for Dota 2 matchmaking stability
* Brave browser and Steam integration for daily use and gaming

---

## 🖥️ Dual Monitor Configuration

This replaces the default single-monitor Omarchy layout with a **two-display setup** and six workspace assignments.
The main display (`DP-1`) runs at **2560×1440 @ 120 Hz**, and the secondary (`HDMI-A-1`) runs at **1366×768 @ 60 Hz**, positioned to the right.

```ini
# Filename: ~/.config/hypr/monitors.conf

monitor=DP-1,2560x1440@120,0x0,1
monitor=HDMI-A-1,1366x768@60,2560x0,1
```

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

# Steam window management

# Keep centering the login dialog
windowrulev2 = center, title:^Sign in to Steam$
# And force it to workspace 1
windowrulev2 = workspace 1, title:^Sign in to Steam$
```

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

---

## 🔤 Alacritty Font Size = 16

To increase the font size globally in Alacritty to **16**, edit:

```
~/.config/alacritty/alacritty.toml
```

Add or update these lines:

```toml
[font]
size = 16
```

If the `[font]` block already exists, just change the `size` value.

This applies instantly after you reopen Alacritty.

---

## 🎮 Gaming Support

Dota 2 runs best **natively**, without additional wrappers such as Gamescope or Proton.
While these wrappers will still launch the game correctly, **secure features like matchmaking will be unavailable** — you’ll be limited to **demo mode and local lobbies** only.
Running the native Linux version avoids this issue entirely, as **VAC verification always fails under wrappers**.

### Launch Options

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid -safe
```

---

## 💿 Installing Steam and Brave

### Steam (official repo)

```bash
sudo pacman -S steam
```

### Brave (AUR)

```bash
yay -S brave-bin
```

---

**Author:** Luis Vásquez

---

If you want, I can also add screenshots, file tree, or a “quick install” script for your repo.

