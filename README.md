<!-- README.md -->

# 🜲 Omarchy Desktop Config

Minimal Omarchy setup focused on **dual-monitor productivity, native Linux gaming, and NVIDIA Vulkan stability** on a desktop workstation.

This configuration is tuned for a fast Hyprland workflow, persistent workspaces across two displays, Steam integration, and native Dota 2 matchmaking support without Proton or Gamescope.

---

## 🛠️ System Information

This configuration is optimized for:

* **OS:** Omarchy
* **WM:** Hyprland
* **CPU:** AMD Ryzen 7 5700X
* **GPU:** NVIDIA GeForce GTX 1650 SUPER
* **Main display:** `DP-1`
* **Secondary display:** `HDMI-A-1`

---

## 🌐 Brave Browser

### Install

Authenticate once:

```bash
sudo -v
```

Then install Brave:

```bash
yay -S --noconfirm brave-bin
```

### Setup

1. Open Brave
2. Set it as the default browser
3. Go to Settings → Search engine
4. Set:
   * Normal: Google
   * Private: Google
5. Go to Settings → Appearance → Theme
6. Select **Dark**

---

## 💬 Ferdium

Ferdium is used to centralize messaging services such as WhatsApp, Telegram, Discord, and Slack.

### Install

```bash
sudo pacman -S --needed --noconfirm flatpak
flatpak install --noninteractive flathub org.ferdium.Ferdium
```

### Setup

1. Open Ferdium
2. Select **Use without account**
3. Add the desired messaging services
4. Scan the QR code when configuring WhatsApp

---

## 🔐 GitHub Authentication

Authenticate with GitHub to enable repository cloning and management:

```bash
gh auth login
```

Follow the prompts. Browser login is recommended.

---

## ⚡ Git Aliases

Create a convenient alias for pushing to the main branch:

```bash
echo 'alias gpm="git push origin main"' >> ~/.bashrc
source ~/.bashrc
```

You can now push the current repository with:

```bash
gpm
```

---

## 📦 Clone Repository

```bash
cd ~/Projects
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs.git
cd omarchy-configs
```

---

## 🔄 Configuration Management

Apply the repository configuration:

```bash
python scripts/compare_configs.py
python scripts/apply_configs.py
python scripts/compare_configs.py
```

Then reload Hyprland and reboot to ensure all changes are applied:

```bash
hyprctl reload
reboot
```

---

## 🖥️ Monitors

This setup uses a dual-monitor layout:

* `DP-1` → main monitor, 2560x1440 at 120 Hz
* `HDMI-A-1` → secondary monitor, 1366x768 at 60 Hz

### Config

Open:

```bash
nvim ~/.config/hypr/monitors.conf
```

Use:

```ini
# ~/.config/hypr/monitors.conf

monitor=DP-1,2560x1440@120,0x0,1
monitor=HDMI-A-1,1366x768@60,2560x0,1
```

### Reload

```bash
hyprctl reload
```

---

## 🧰 Waybar

Waybar is used as the main status bar.

### Config

Open:

```bash
nvim ~/.config/waybar/config.jsonc
```

### Clock

Use the following clock configuration to display the date, weekday, and time:

```jsonc
"clock": {
  "format": "{:L%d %B %A %H:%M}",
  "format-alt": "{:L%d %B %A %H:%M}",
  "tooltip": false,
  "on-click-right": "omarchy-launch-floating-terminal-with-presentation omarchy-tz-select"
}
```

Right-clicking the clock opens the Omarchy timezone selector.

### Persistent Workspaces

Ensure persistent workspaces:

```jsonc
"persistent-workspaces": {
  "1": [],
  "2": [],
  "3": [],
  "4": [],
  "5": [],
  "6": [],
  "7": []
}
```

The battery module is intentionally omitted because this configuration targets a desktop system.

### Reload

```bash
pkill waybar
hyprctl dispatch exec waybar
```

---

## 🔤 Alacritty

Current system default terminal, based on `~/.config/xdg-terminals.list`.

### Config

Open:

```bash
nvim ~/.config/alacritty/alacritty.toml
```

### Font Size

Locate or add:

```toml
[font]
size = 13.0
```

Close all terminal windows and open a new one to apply the change.

---

## ⚙️ Hyprland

This configuration assigns seven workspaces across two monitors.

* Workspaces `1`, `2`, `3`, `7` → `DP-1`
* Workspaces `4`, `5`, `6` → `HDMI-A-1`

### Config

Open:

```bash
nvim ~/.config/hypr/hyprland.conf
```

### Hyprland Rules

Append the following rules at the end of the file:

```ini
# ~/.config/hypr/hyprland.conf

workspace=1,monitor:DP-1
workspace=2,monitor:DP-1
workspace=3,monitor:DP-1
workspace=4,monitor:HDMI-A-1
workspace=5,monitor:HDMI-A-1
workspace=6,monitor:HDMI-A-1
workspace=7,monitor:DP-1

windowrule {
    name = steam-all
    match:class = ^steam.*$
    workspace = 1
    float = on
    center = on
}

windowrule {
    name = steam-title-fallback
    match:class = ^steam$
    match:title = ^(Steam|Updating|Working|Loading).*
    workspace = 1
    float = on
    center = on
}

windowrule {
    name = steam-signin
    match:initial_title = ^Sign in to Steam$
    workspace = 1
    float = on
    center = on
}

windowrule {
    name = dota2-main
    match:class = ^(steam_app_570|dota2)$
    workspace = 1
    fullscreen = on
    no_anim = on
    monitor = DP-1
}

device {
    name = logitech-g300s-optical-gaming-mouse
    sensitivity = 0.20
    accel_profile = adaptive
}
```

### Reload

```bash
hyprctl reload
```

---

## ⚙️ Hyprland Autostart

Use autostart to initialize the workspace layout after login.

### Config

Open:

```bash
nvim ~/.config/hypr/autostart.conf
```

Add:

```ini
# ~/.config/hypr/autostart.conf

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
exec = hyprctl dispatch workspace 7
exec = hyprctl dispatch movetoworkspace 7,DP-1
```

### Reload

```bash
hyprctl reload
```
---

## 🎮 Steam

### Install

```bash
sudo pacman -S --needed --noconfirm steam
```

---

## 🎯 Dota 2

Dota 2 is configured to run **natively using Vulkan**.

Do not use:

* Gamescope
* Proton
* Wine
* Any wrapper

These can break VAC verification and disable matchmaking.

### Launch Options

Set in Steam:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid
```

### Notes

* `-novid` → skips intro
* `-console` → enables developer console
* Native Vulkan keeps matchmaking enabled
* NVIDIA ICD path avoids incorrect Vulkan provider selection

---

## 🧟 Left 4 Dead 2

Left 4 Dead 2 works best when forcing X11.

This avoids broken input scaling under Wayland and does not require Gamescope or borderless hacks.

### Launch Options

Set in Steam:

```bash
SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=pulse %command% -console -novid
```

### Notes

* Game may initially show Waybar
* Toggle real fullscreen with **SUPER + F**
* Once fullscreen, input scaling and clicks behave correctly
* No window positioning flags are required

---

## 🧠 StarCraft: Remastered

StarCraft: Remastered does not have a native Linux build.

The most reliable setup on Omarchy is:

* Steam
* Battle.net Windows installer
* Proton Experimental

Lutris and standalone Wine are less stable due to Battle.net agent issues.

### Installation

1. Download the Battle.net Windows installer:

```text
https://www.blizzard.com/download
```

2. In Steam:
   * Add the installer as a Non-Steam Game
   * Force compatibility with Proton Experimental

3. Launch the installer and install Battle.net

4. Inside Battle.net:
   * Log in
   * Install StarCraft: Remastered
   * Keep the Battle.net window visible during download

### Launch Options

Set in Steam:

```bash
PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 %command%
```

### Notes

* Proton Experimental is recommended during installation
* Other Proton versions may freeze Battle.net downloads
* After installation, Proton Experimental can be kept or replaced with a stable Proton version

---

## 👤 Author

Luis Vásquez
```
