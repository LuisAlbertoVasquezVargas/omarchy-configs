# 🜲 Omarchy Laptop Config

Minimal Omarchy setup focused on **stability, gaming, and daily productivity** on a single-display laptop.

---

## 📦 Clone Repository

```bash
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop.git
cd omarchy-configs-laptop
```

> Copy the configs manually into your `~/.config` directory as needed.

---

## 🧭 Core Components

Main tools used in this setup:

* **Hyprland** → Wayland compositor
* **Waybar** → status bar
* **Ghostty** → terminal emulator
* **Brave** → default browser
* **Ferdium** → messaging hub (WhatsApp Web, etc.)
* **Steam** → gaming platform

---

## 🧰 Waybar

Waybar is used as the main status bar.

### Config

Open:

```bash
nvim ~/.config/waybar/config.jsonc
```

Ensure persistent workspaces:

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

### Reload

```bash
pkill waybar
hyprctl dispatch exec waybar
```

---

## 🔤 Ghostty (Terminal)

Default terminal for this setup.

Open:

```bash
nvim ~/.config/ghostty/config
```

Set:

```ini
font-size = 14
```

---

## 🌐 Brave Browser

### Install

```bash
yay -S brave-bin
```

### Setup

1. Open Brave
2. Set as default browser
3. Go to settings → search engine
4. Set:

   * Normal: Google
   * Private: Google

---

## 💬 Ferdium (WhatsApp + Messaging)

Ferdium is used to centralize messaging apps like **WhatsApp Web**, avoiding phone dependency and browser tab clutter.

### Install

```bash
yay -S ferdium-bin
```

### Setup

1. Open Ferdium
2. Add service → **WhatsApp**
3. Scan QR code
4. (Optional) Add:

   * Telegram
   * Discord
   * Slack

---

## 🎮 Steam

### Install

```bash
sudo pacman -S steam
```

---

## 🎯 Dota 2 (Native + Matchmaking Enabled)

Dota 2 is configured to run **natively using Vulkan**.

⚠️ Do NOT use:

* Gamescope
* Proton
* Any wrapper

These break **VAC matchmaking**.

---

### Launch Options

Set in Steam:

```bash
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 %command% -console -novid
```

---

### Notes

* `-novid` → skips intro
* `-console` → enables developer console
* Native Vulkan ensures:

  * Proper input scaling
  * Stable FPS
  * Matchmaking enabled

---

## ⚙️ Hyprland (Base Behavior)

Minimal assumptions, no forced layouts.

Open:

```bash
nvim ~/.config/hypr/hyprland.conf
```

Suggested baseline:

```ini
# =============================
# Steam (ALL windows controlled)
# =============================

windowrule {
    name = steam-all
    match:class = ^steam.*$
    workspace = 1
    float = on
    center = on
}

windowrule {
    name = steam-title-fallback
    match:title = ^(Steam|Updating|Working|Loading).*
    workspace = 1
    float = on
    center = on
}

# =============================
# Dota 2 (launched via Steam)
# =============================

windowrule {
    name = dota2-main
    match:class = ^(steam_app_570|dota2)$
    workspace = 1
    fullscreen = on
    no_anim = on
}

# -----------------------------
# Pointer configuration (example)
# -----------------------------
device {
    name = logitech-g300s-optical-gaming-mouse
    sensitivity = 0.20
    accel_profile = adaptative
}
```

Reload:

```bash
hyprctl reload
```

---

## 🧠 Philosophy

This setup avoids:

* Hardcoded monitor layouts
* Overcomplicated automation
* Wayland wrappers that break games

Focus is on:

* Stability
* Predictability
* Native performance

---

**Author:** Luis Vásquez

