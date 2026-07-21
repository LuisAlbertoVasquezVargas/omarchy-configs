# Omarchy Desktop Config

Personal Omarchy configuration for a desktop workstation focused on dual-monitor Hyprland workflow, seven persistent workspaces, desktop-oriented Waybar modules, Ghostty defaults, Steam/Dota 2 window behavior, NVIDIA Vulkan stability, Logitech G300s mouse tuning, Ferdium startup, and native Linux gaming. The tracked files under `.config/` are the single source of truth for desktop configuration; this README keeps only the setup order and manual instructions.

## Target System

- OS: Omarchy
- WM: Hyprland
- CPU: AMD Ryzen 7 5700X
- GPU: NVIDIA GeForce RTX 3060 Ti
- Main display: `DP-1`
- Secondary display: `HDMI-A-1`

## Ghostty Setup

1. Install Ghostty.

   ```bash
   omarchy install terminal ghostty
   ```

2. Make Ghostty the default terminal.

   ```bash
   omarchy default terminal ghostty
   ```

The tracked Ghostty configuration changes the font size from `9` to `13` and disables font-size inheritance so every new window starts at size `13`.

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

4. Install Node.js and npm for the OpenAI Codex CLI.

   ```bash
   sudo pacman -S --needed nodejs npm
   ```

   Verify the installation.

   ```bash
   node -v
   npm -v
   ```

5. Install the OpenAI Codex CLI globally with npm.

   ```bash
   npm install -g @openai/codex
   ```

   Verify the installation.

   ```bash
   codex --version
   ```

6. Authenticate GitHub CLI.

   ```bash
   gh auth login
   ```

   Use browser login when prompted.

7. Add the Git push alias.

   ```bash
   echo 'alias gpm="git push origin main"' >> ~/.bashrc
   source ~/.bashrc
   ```

8. Clone this repository.

   ```bash
   cd ~/Projects
   git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs.git
   cd omarchy-configs
   ```

9. Compare the repository configs with the current system configs.

   ```bash
   python scripts/compare_configs.py
   ```

10. Apply the repository configs.

   ```bash
   python scripts/apply_configs.py
   ```

   The script previews creates/replacements first and only writes after you type `yes`. Replaced files are backed up under `~/.local/state/omarchy-configs/backups/`.

11. Compare again to confirm the files now match.

    ```bash
    python scripts/compare_configs.py
    ```

12. Reload the desktop.

    ```bash
    hyprctl reload
    omarchy restart waybar
    ```

    Reopen Ghostty windows so font, padding, and keyboard changes are picked up. Reboot if you want to verify the full autostart flow from a clean login.

13. Install Steam.

    ```bash
    sudo pacman -S --needed --noconfirm steam
    ```

14. Configure Dota 2.

    Use the native Linux build with Vulkan. Do not use Gamescope, Proton, Wine, or wrappers because they can break VAC verification and disable matchmaking.

    Steam launch options:

    ```bash
    SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid
    ```

15. Configure Left 4 Dead 2.

    Force X11 to avoid broken input scaling under Wayland.

    Steam launch options:

    ```bash
    SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=pulse %command% -console -novid
    ```

    If Waybar appears over the game, toggle real fullscreen with `SUPER + F`.

16. Configure StarCraft: Remastered.

    Download the Battle.net Windows installer from `https://www.blizzard.com/download`, add it to Steam as a non-Steam game, force Proton Experimental, run the installer, log in to Battle.net, and install StarCraft: Remastered while keeping the Battle.net window visible.

    Steam launch options:

    ```bash
    PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 %command%
    ```

17. Install the optional Ghost Pastel Omarchy theme.

    ```bash
    omarchy-theme-install https://github.com/row-huh/omarchy-ghost-pastel-theme
    ```

    Theme page: `https://omarchytheme.com/themes/ghost-pastel/`

## Experimental: Neovim Image Rendering

This experiment renders standalone images and inline Markdown images inside Neovim through Ghostty's graphics-protocol support. PDF documents remain external and open in Zathura. The Neovim configuration is intentionally not tracked yet because this workflow is still being evaluated.

1. Confirm Ghostty is the default terminal and start Neovim from a fresh Ghostty window.

2. Install the image conversion and PDF preview dependencies.

   ```bash
   omarchy pkg add imagemagick zathura zathura-pdf-mupdf
   ```

3. Enable the image module from LazyVim's existing `snacks.nvim` plugin by creating `~/.config/nvim/lua/plugins/image-rendering.lua`:

   ```lua
   return {
     {
       "folke/snacks.nvim",
       opts = {
         image = {},
       },
     },
   }
   ```

4. Restart Neovim and run `:checkhealth snacks`. Ghostty and ImageMagick should pass the image checks when Neovim is running interactively inside Ghostty.

5. Test a standalone PNG or JPEG, then open a Markdown document containing a relative image reference. Use Zathura for PDF previews rather than rendering PDFs inline.

Headless Neovim cannot complete the terminal graphics handshake, so its health check may incorrectly report that the graphics protocol is unavailable. Validate rendering in an interactive Ghostty window.

## Experimental: Codex Workspace Shortcut

These shortcuts open Codex and a terminal in the corresponding project workspace:

- `SUPER + HOME` uses workspace 2 and `~/Projects/MOVER-research-materials/`.
- `SUPER + END` uses workspace 3 and `~/Projects/shopping-list-ui/`.

Add the following lines to `~/.config/hypr/bindings.conf`. They are intentionally kept out of the tracked Hyprland configuration while they are being evaluated:

```text
bindd = SUPER, HOME, Codex + terminal (workspace 2), workspace, 2
bind = SUPER, HOME, exec, [workspace 2 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/MOVER-research-materials/" && exec codex'
bind = SUPER, HOME, exec, [workspace 2 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/MOVER-research-materials/" && exec bash'
bindd = SUPER, END, Codex + terminal (workspace 3), workspace, 3
bind = SUPER, END, exec, [workspace 3 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/shopping-list-ui/" && exec codex'
bind = SUPER, END, exec, [workspace 3 silent] uwsm-app -- xdg-terminal-exec bash -lc 'cd "$HOME/Projects/shopping-list-ui/" && exec bash'
```

## Experimental: NVIDIA GPU Driver Update

This machine uses the NVIDIA open kernel modules. Update the GPU driver packages as part of a full system upgrade so the kernel, DKMS module, and user-space libraries remain compatible:

```bash
yay -Syu nvidia-open-dkms nvidia-utils
```

After the upgrade completes successfully, reboot and verify the loaded driver:

```bash
omarchy system reboot
nvidia-smi
```
