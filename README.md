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

Open:

```bash
nvim ~/.config/hypr/monitors.conf
```

Add:

```ini
# Filename: ~/.config/hypr/monitors.conf

monitor=DP-1,2560x1440@120,0x0,1
monitor=HDMI-A-1,1366x768@60,2560x0,1
```

Reload Hyprland to apply:

```bash
hyprctl reload
```

---

## 🧩 Append These Lines to the End of hyprland.conf

Open:

```bash
nvim ~/.config/hypr/hyprland.conf
```

Append:

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
windowrulev2 = center, title:^Sign in to Steam$
windowrulev2 = workspace 1, title:^Sign in to Steam$

# Dota 2 always on workspace 1
windowrulev2 = workspace 1, class:^dota2$
```

Reload Hyprland:

```bash
hyprctl reload
```

---

## ⚙️ Extra Autostart Processes

Open:

```bash
nvim ~/.config/hypr/autostart.conf
```

Add:

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

Reload Hyprland:

```bash
hyprctl reload
```

---

## 🔤 Ghostty (Default Terminal on Recent Omarchy)

Recent Omarchy versions **replaced Alacritty with Ghostty** as the default terminal emulator.

### Font Size

Open:

```bash
nvim ~/.config/ghostty/config
```

Set:

```ini
font-size = 16
```

Close all terminal windows and open a new one to apply.

---

## 🧰 Waybar Setup

Open:

```bash
nvim ~/.config/waybar/config.jsonc
```

Add:

```jsonc
"persistent-workspaces": {
  "1": [],
  "2": [],
  "3": [],
  "4": [],
  "5": [],
  "6": []
}
```

Restart Waybar or log out/in to apply.

---

## 🎮 Gaming Support

Native Linux gaming focused on stability, correct input scaling, and compatibility with Hyprland.

---

## 🎯 Dota 2 (Native Vulkan, Matchmaking Enabled)

Dota 2 runs best **natively**, without wrappers like Gamescope or Proton.
While wrappers may launch the game, **VAC verification fails**, meaning **no matchmaking**, only demo mode and local lobbies.

### Launch Options (Native Vulkan)

Set inside Steam:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid
```

**Meaning of flags:**

* `-console` → enable developer console
* `-novid` → skip intro
* `-safe` → safe mode for recoveries

---

## 🧟 Left 4 Dead 2 (Native, X11)

Left 4 Dead 2 works best when **forcing X11**, avoiding Gamescope and borderless hacks.
This configuration launches cleanly, uses the correct monitor resolution, and avoids broken input scaling under Wayland.

### Launch Options

Set inside Steam:

```bash
SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=pulse %command% -console -novid
```

**Notes:**

* Game may initially show the Waybar
* Toggle real fullscreen with **SUPER + F**
* Once fullscreen, input scaling and clicks behave correctly
* No window positioning flags required
* Stable across launches

---

## 🧠 StarCraft: Remastered (Steam + Proton)

StarCraft: Remastered does **not** have a native Linux build.
The most reliable way to run it on Omarchy is **Steam + Proton Experimental**.

Attempts via Lutris or standalone Wine are significantly less stable due to Battle.net agent issues.

### Installation Steps

1. Download the **Battle.net Windows installer**:

   ```
   https://www.blizzard.com/download
   ```

2. In Steam:

   * Add the installer as a **Non-Steam Game**
   * Force compatibility → **Proton Experimental**

3. Launch the installer and install **Battle.net**

4. Inside Battle.net:

   * Log in
   * Install **StarCraft: Remastered**
   * Keep the Battle.net window visible during download (do not minimize)

> Proton Experimental is required during installation.
> Other Proton versions may cause Battle.net downloads to freeze.

### Launch Options (Recommended)

Set in **Steam → StarCraft: Remastered → Properties → Launch Options**:

```bash
PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 %command%
```

### After Installation

* Proton Experimental can be kept, or
* Switched to a stable Proton version (e.g. Proton 9.0)

SC:R runs smoothly once installed.

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

### After installing Brave

#### **1. Set Brave as the default browser**

On first launch → click **Make default browser**.

#### **2. Change the default search engine (normal + private)**

1. Open Brave
2. Settings
3. Search engine
4. Set both to **Google**

---

**Author:** Luis Vásquez

