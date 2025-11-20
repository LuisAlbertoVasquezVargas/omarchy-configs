
# 🜲 Omarchy Configs

Omarchy configs for **dual-monitor setups with Dota 2 support and matchmaking enabled**.
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

Create your monitor layout in:

```
~/.config/hypr/monitors.conf
```

```ini
# Filename: ~/.config/hypr/monitors.conf

monitor=DP-1,2560x1440@120,0x0,1
monitor=HDMI-A-1,1366x768@60,2560x0,1
```

---

## 🧩 Append These Lines to the End of hyprland.conf

To activate workspace distribution, mouse settings, and Steam window rules, **append the following lines at the end of**:

```
~/.config/hypr/hyprland.conf
```

```ini
# Workspace assignments
# Primary monitor (DP-1): workspaces 1–3
workspace=1,monitor:DP-1
workspace=2,monitor:DP-1
workspace=3,monitor:DP-1

# Secondary monitor (HDMI-A-1): workspaces 4–6
workspace=4,monitor:HDMI-A-1
workspace=5,monitor:HDMI-A-1
workspace=6,monitor:HDMI-A-1

# Pointer configuration (Logitech G300s)
device {
    name = logitech-g300s-optical-gaming-mouse
    sensitivity = 0.20
    accel_profile = adaptative
}

# Steam window management
# Keep centering the login dialog
windowrulev2 = center, title:^Sign in to Steam$
# Force it to workspace 1
windowrulev2 = workspace 1, title:^Sign in to Steam$
```

This ensures your monitor setup takes effect **after** all Omarchy defaults.

---

## ⚙️ Extra Autostart Processes

These commands run automatically on login to ensure workspaces attach to the correct monitors:

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

## 🔤 Alacritty Font Size = 16

Increase the global Alacritty font size by editing:

```
~/.config/alacritty/alacritty.toml
```

Add or update:

```toml
[font]
size = 16
```

Restart Alacritty to apply.

---

## 🧰 Waybar Setup

Update the default Omarchy Waybar config to support **six workspaces**:

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

This keeps Waybar aligned with Hyprland.

---

## 🎮 Gaming Support

Dota 2 runs best **natively**, without wrappers such as Gamescope or Proton.
While wrappers still launch the game, **VAC verification fails**, meaning **no matchmaking**, only demo mode and local lobbies.

### Launch Options (Native Vulkan)

Use this inside Steam > Dota 2 > Properties > Launch Options:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid -safe
```

**Meaning of flags:**

* `-console` → Enables developer console
* `-novid` → Skip intro video
* `-safe` → Safe boot in case of bad configs

---

## 💿 Installing Steam and Brave

### Steam (official repo)

```bash
sudo pacman -S steam
```

### Brave Browser (AUR)

```bash
yay -S brave-bin
```

---

**Author:** Luis Vásquez

---

