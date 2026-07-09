# Omarchy Desktop Config

Personal Omarchy configuration for a desktop workstation focused on dual-monitor Hyprland workflow, seven persistent workspaces, desktop-oriented Waybar modules, Alacritty defaults, Steam/Dota 2 window behavior, NVIDIA Vulkan stability, Logitech G300s mouse tuning, Ferdium startup, and native Linux gaming. The tracked files under `.config/` are the single source of truth for desktop configuration; this README keeps only the setup order and manual instructions.

## Target System

- OS: Omarchy
- WM: Hyprland
- CPU: AMD Ryzen 7 5700X
- GPU: NVIDIA GeForce GTX 1650 SUPER
- Main display: `DP-1`
- Secondary display: `HDMI-A-1`

## Setup Steps

1. This repository assumes Omarchy is already installed.

2. Install Brave.

   ```bash
   sudo -v
   yay -S --noconfirm brave-bin
   ```

   Open Brave, set it as the default browser, set Google as the normal and private search engine, select the dark theme, then connect Brave Sync from your phone with the desktop QR code.

3. Install Ferdium.

   ```bash
   sudo pacman -S --needed --noconfirm flatpak
   flatpak install --noninteractive flathub org.ferdium.Ferdium
   ```

   Open Ferdium, choose `Use without account`, add the messaging services you need, and scan the QR code for WhatsApp.

4. Authenticate GitHub CLI.

   ```bash
   gh auth login
   ```

   Use browser login when prompted.

5. Add the Git push alias.

   ```bash
   echo 'alias gpm="git push origin main"' >> ~/.bashrc
   source ~/.bashrc
   ```

6. Clone this repository.

   ```bash
   cd ~/Projects
   git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs.git
   cd omarchy-configs
   ```

7. Compare the repository configs with the current system configs.

   ```bash
   python scripts/compare_configs.py
   ```

8. Apply the repository configs.

   ```bash
   python scripts/apply_configs.py
   ```

   The script previews creates/replacements first and only writes after you type `yes`. Replaced files are backed up under `~/.local/state/omarchy-configs/backups/`.

9. Compare again to confirm the files now match.

    ```bash
    python scripts/compare_configs.py
    ```

10. Reload the desktop.

    ```bash
    hyprctl reload
    omarchy restart waybar
    ```

    Reopen Alacritty windows so font, padding, and keyboard changes are picked up. Reboot if you want to verify the full autostart flow from a clean login.

11. Install Steam.

    ```bash
    sudo pacman -S --needed --noconfirm steam
    ```

12. Configure Dota 2.

    Use the native Linux build with Vulkan. Do not use Gamescope, Proton, Wine, or wrappers because they can break VAC verification and disable matchmaking.

    Steam launch options:

    ```bash
    SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid
    ```

13. Configure Left 4 Dead 2.

    Force X11 to avoid broken input scaling under Wayland.

    Steam launch options:

    ```bash
    SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=pulse %command% -console -novid
    ```

    If Waybar appears over the game, toggle real fullscreen with `SUPER + F`.

14. Configure StarCraft: Remastered.

    Download the Battle.net Windows installer from `https://www.blizzard.com/download`, add it to Steam as a non-Steam game, force Proton Experimental, run the installer, log in to Battle.net, and install StarCraft: Remastered while keeping the Battle.net window visible.

    Steam launch options:

    ```bash
    PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 %command%
    ```

15. Install the optional Ghost Pastel Omarchy theme.

    ```bash
    omarchy-theme-install https://github.com/row-huh/omarchy-ghost-pastel-theme
    ```

    Theme page: `https://omarchytheme.com/themes/ghost-pastel/`

## Author

Luis Vasquez
