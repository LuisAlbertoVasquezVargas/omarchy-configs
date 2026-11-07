<!-- README.md -->

# Omarchy Desktop Config

Personal configuration for **Omarchy 4.5.0 (Quattro RS)** on this AMD/NVIDIA PC.
See the [4.5 release notes](https://omarchy.org/news/2026/11/omarchy-4-5/).

## Target System

- CPU: AMD Ryzen 7 5700X
- GPU: NVIDIA GeForce RTX 5060 Ti
- Primary display: Samsung LS27DG30X, 1920×1080 at 60 Hz, scale 1.
  Confirmed description: `Samsung Electric Company LS27DG30X H8CX700532`.
- Secondary display: BenQ G610HDAL, 1366×768 at 59.79 Hz, scale 1,
  connected through `HDMI-A-1` when in use.

The Samsung description was checked on this PC. The BenQ is disconnected; its
connector and mode come from the previous desktop setup and need a live check
when reconnected. No laptop, touchpad, or battery configuration is installed.

<!-- TODO: Describe additional hardware components. -->

## Configuration Workflow

This repository follows the same format as
[omarchy-configs-laptop](https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop):
a root `setup.py`, named steps in README order, a project `.venv`, and
`requirements.txt`. Python uses TOMLKit to preserve unrelated TOML settings.

Review the code before running it. `python setup.py` takes no arguments and
**applies configuration immediately**. There is no `--apply` or preview mode.
It checks the Omarchy version and active desktop session before performing
setup. Omarchy 4.0 installs and detected legacy workspace rules are refused.
This is a 4.5 setup, not an operating-system updater or a 4.0 migration tool.

Each step checks the installed component or desired setting and skips a match.
Changed files are backed up. Lua syntax and effective Hyprland configuration
are checked; affected files are restored if those checks fail. A failed step
stops the script, while earlier successful steps remain applied. Package
installations and theme changes are not automatically undone.

`setup.py` checks syntax, installed components, and configuration results as
part of applying each step. It retains backups and rollback for failed changes.

The files under `config/hypr/` are Lua source fragments read by `setup.py`.
Setup validates and appends each fragment to its corresponding user file:

| Source fragment | Destination under `~/.config/hypr/` | Purpose |
| --- | --- | --- |
| [compact-layout.lua](config/hypr/compact-layout.lua) | `looknfeel.lua` | Zero window gaps, three-pixel borders, and theme-based focus colors. |
| [displays.lua](config/hypr/displays.lua) | `monitors.lua` | Samsung/BenQ display profiles and GTK scale 1. |
| [dota-close-binding.lua](config/hypr/dota-close-binding.lua) | `bindings.lua` | Route Super+W through the helper that blocks closing while Dota runs. |

Hyprland reads the installed user files. Keep these repository fragments so
setup can reproduce the configuration, compare it on later runs, and validate
future changes.

Console output is labeled by README section, such as `[Brave]` or `[Steam]`.
Each section has `START`, `FINISHED`, or `FAILED` markers and an elapsed time;
existing-component and matching-setting skips remain explicit. Commands run
synchronously, report their exit status, and show a PID and elapsed time after
every 15 seconds without output. Setup waits for each command before continuing
and stops on failure. Interactive commands retain terminal input, including
normal `sudo` password prompts.

Every run prints its log directory under
`${XDG_STATE_HOME:-$HOME/.local/state}/omarchy-configs/logs/<timestamp>/`.
`setup.log` contains the full run; numbered files such as `03-brave.log` and
`10-steam.log` contain only that section. Command stdout and stderr are saved,
including query/validation stdout that is hidden from the console. Logs remain
available after a failure. Desktop services restarted by native helpers keep
their normal lifecycle; setup waits for the helper's readiness check, not for
the service to exit.

The setup covers the sections below through **Displays and Ten Workspaces per
Monitor**. Application sign-ins, synchronization, visual checks, and the
experimental NVIDIA update remain manual. Earlier implementations remain in
Git history at commit `563f023`. Future preferences are listed under
[Ideas](#ideas).

Implementation has been checked against the official `v4.5.0` source. The
Agents weekly display and Steam UI scale 1 were verified live on this PC
running 4.5.0-3. Remaining manual checks are listed in their respective sections.

## Installation USB

See [Create an Omarchy Installation USB](INSTALLATION-USB.md).
USB flashing, installation, updating Omarchy, and rebooting are separate from
running this repository's setup script.

## Clone This Repository

```bash
cd ~/Projects
git clone https://github.com/LuisAlbertoVasquezVargas/omarchy-configs.git
cd omarchy-configs
```

Create and activate the project environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Activate `.venv` in each terminal before running setup. Code follows the general
and Python conventions in the sibling `swe-standards` repository.

## Ghost Pastel Theme

After reviewing the code, run it as your normal desktop user from a terminal
inside the unlocked Omarchy 4.5.0 session, without `sudo` or arguments:

```bash
python setup.py
```

If Ghost Pastel is missing, setup installs and activates it with:

```bash
omarchy theme install https://github.com/row-huh/omarchy-ghost-pastel-theme
```

An already installed theme is skipped, including when another theme is active.
The script checks Omarchy's installed theme list after a new installation.
Confirm the bar, wallpaper, and terminal colors visually.

## Brave

Setup skips installation when `brave` is already available. Otherwise it uses
Omarchy's browser installer and checks the executable afterward:

```bash
omarchy install browser brave
```

It then checks the default browser and sets Brave only when needed:

```bash
omarchy default browser
omarchy default browser brave
```

Existing `mimeapps.list` is backed up before changing the default. The result
is checked and previous MIME settings are restored if the change fails.

### Setup

1. Open Brave.
2. Select **Dark** under **Settings → Appearance → Theme**.
3. Under **Settings → Sync**, select **I have a Sync Code**.
4. On your phone, open Brave's Sync settings, select **Add a new device**, and
   scan the desktop QR code.
5. Wait for synchronization to finish.
6. Set Google for normal and private browsing under **Settings → Search engine**.

The old instruction to disable graphics acceleration remains retired.

## Ghostty

Terminal selection is not automated. Test Ghostty and Foot on Quattro RS before
choosing and documenting the default terminal.

## WhatsApp

WhatsApp is supplied by Omarchy. Setup reports the installed Omarchy version
without changing the app. Open it from the launcher and link your phone.

## Slack

As in the laptop workflow, setup reports that Slack can be installed as a
service. Installation and sign-in remain manual. The web-app option is:

```bash
omarchy webapp install "Slack" "https://app.slack.com/client" ""
```

The empty icon argument downloads the icon automatically. With Brave selected
as the default browser, the web app opens in Brave. Sign in and allow
notifications when prompted.

## Discord

Discord is supplied by Omarchy. Setup reports the installed Omarchy version
without changing the app. Open Discord from the launcher and sign in.

## Zathura

Setup installs only missing packages:

```bash
omarchy pkg add zathura zathura-pdf-mupdf xdg-utils
```

It verifies that `zathura --version` lists the `pdf-mupdf` plugin, then checks
the PDF association. A matching default is skipped. Otherwise, MIME settings
are backed up before setting and checking the association; failures restore
the previous settings.

Equivalent checks:

```bash
zathura --version
xdg-mime query default application/pdf
```

The association must be `org.pwmt.zathura.desktop`. Opening a sample PDF is a
manual check; routine setup does not create or open one.

## Neovim

Setup creates the Neo-tree visibility override under
`~/.config/nvim/lua/plugins/neo-tree.lua`. Existing plugin specifications are
retained as a nested Lazy.nvim specification, followed by the visibility
setting. Lua syntax is checked before saving, changed files are backed up,
and an unchanged override is skipped.

Hidden, filtered, and Git-ignored files are shown with their filtered styling.
Restart Neovim and inspect Neo-tree to verify the result.

## Codex CLI Approval Defaults

The Codex CLI must already be installed. Setup uses TOMLKit to merge these
top-level settings into `${CODEX_HOME:-$HOME/.codex}/config.toml`:

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
sandbox_mode = "workspace-write"
```

Unrelated settings and comments are preserved. Matching defaults are skipped;
changed files are backed up and checked with `codex features list`. Failed
validation restores the original file.

Start a new Codex session and check `/permissions`. Profiles, command-line
options, and managed requirements can override these defaults. Sign-in remains
manual. Official references: [Auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review)
and [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

## Steam

Setup skips an existing `steam` executable. Otherwise it runs the foreground
stages of Omarchy 4.5's Steam installer, in order, so the native helper selects
the correct graphics dependencies:

```bash
omarchy install gaming gpu-lib32
omarchy pkg add steam
omarchy lifecycle dispatch post-install steam
```

Each command is monitored and must finish successfully before setup continues.
The `steam` executable is checked afterward. Unlike
[`omarchy install gaming steam`](https://github.com/basecamp/omarchy/blob/v4.5.0/bin/omarchy-install-gaming-steam),
setup leaves Steam closed: the stock installer's detached client launch can
download/update the client after the installer returns, independently of setup.
Launch Steam manually afterward to finish client initialization and sign in.
Client downloads, games, and launch options remain manual. Existing Steam
preferences are not rewritten.

### Steam UI Scaling

The display configuration below sets GTK and monitor scale to 1 on this PC.
An already running desktop session can still pass the previous `GDK_SCALE=2`
to Steam, doubling text and icons in the main, Friends, and chat windows even
when Hyprland reports monitor scale 1. After applying the display configuration,
log out and back in, then launch Steam again so it inherits the new scale.

If Steam still appears oversized, open **Steam → Settings → Interface**, turn
off **Scale text and icons to match monitor settings**, and accept Steam's
restart prompt.

Check the session environment and Steam's own display-scale log:

```bash
systemctl --user show-environment | rg '^GDK_SCALE='
rg 'Display\[[0-9]+\].*scale=' ~/.local/share/Steam/logs/webhelper_gpu.txt | tail -n 1
```

For the Samsung, expect `GDK_SCALE=1` and a new Steam log entry with
`bounds=[0,0 1920x1080]` and `scale=1`. Check the UI scale before adding window
geometry rules; resizing a window does not reduce its text or icon scale.

### Dota 2 Launch Options

Set these manually in Dota 2's Steam launch options:

```text
SDL_AUDIODRIVER=pulse PULSE_LATENCY_MSEC=60 VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json %command% -console -novid
```

Restored unchanged from commit `563f023`. These personal launch options have
not yet been revalidated on Omarchy 4.5.0. `setup.py` does not edit them.

## Disable Super+W While Dota 2 Runs

Setup installs [scripts/dota-close-guard.sh](scripts/dota-close-guard.sh) under
`~/.config/hypr/` and applies the reviewed
[keybinding override](config/hypr/dota-close-binding.lua). Matching files are
skipped; changed files are backed up and Lua is validated before saving.

Super+W normally closes the focused window. This override consumes the shortcut
while your native `dota2` process is running, on every workspace. After Dota
exits, closing works normally. Steam alone does not block closing, and a process
lookup error prevents closing. Failed binding validation restores both the
binding file and any helper changed by that attempt.

Test Super+W before starting Dota, while Dota runs, and after exiting it.
The close dispatcher matches Omarchy 4.5's default binding; that source check
and the guard tests do not replace this live check.

## Clock Format

Setup merges these settings into the existing built-in clock entry:

```json
{
  "id": "omarchy.clock",
  "format": "dd MMM ddd · 'W'ww · HH:mm",
  "formatAlt": "dd MMM ddd · 'W'ww · HH:mm",
  "verticalFormat": "HH\n—\nmm"
}
```

The existing bar position, other widget options, and unrelated shell settings
are preserved. A missing layout inherits Omarchy's installed layout; a missing
clock is added in the center. Duplicate clocks are reported for resolution.
Matching settings are skipped. Changed JSON is backed up and written atomically.

The shell reloads automatically. Check the date, week number, and time visually.

## Agents Widget

Setup installs the weekly-percentage/countdown display change below in a
user-owned Agents clone. Existing clones and provider settings are preserved;
only the reviewed display bindings are changed. A matching active clone is
skipped. The old quota collector is not installed.

Account setup stays manual.

### Weekly Percentage and Reset Countdown

Adapted from the laptop's [Agents display change in commit
66affcc](https://github.com/LuisAlbertoVasquezVargas/omarchy-configs-laptop/commit/66affcc57b9773a4343707cf59e74190a6bfb50c).
The Weekly row shows the allowance **used** beside its reset countdown as soon
as the panel opens:

```text
Weekly  ━━━━━░░░░░  35% · 3d 19h
```

Session, monthly, and model-scoped rows retain their existing display. Native
usage collection, provider preferences, tooltips, and bar placement are
preserved. The value reserves room for `100% · 00h 00m` and expands for longer
text, using Omarchy's locale number formatter and plain-text rendering.

The focused [QML patch](config/omarchy/agents-weekly.patch) changes only the
`CompactLimit` value and its width measurement in the user-owned clone:

```text
~/.config/omarchy/plugins/<username>.agents/Panel.qml
```

Running `python setup.py` now applies this change in its **Agents Widget**
step. Setup reuses an existing clone whose manifest identifies it as cloned
from `omarchy.agents`. If absent, it stages the built-in panel and creates a
clone with `omarchy plugin clone omarchy.agents` after validation. Packaged
files under `/usr/share/omarchy/` remain unchanged.

The staged QML syntax is checked with `/usr/lib/qt6/bin/qmlformat --ignore-settings`
before installation. Unexpected patch context stops the step for review.
Before cloning or writing, setup backs up
`shell.json` and any existing cloned `Panel.qml` outside the watched tree, under
`${XDG_STATE_HOME:-$HOME/.local/state}/omarchy/backups/agents-widget-<timestamp>/`.
Setup installs the validated panel, restarts the shell, and verifies that the
clone is enabled. A failed installation restores the saved files, removes a
clone created by that attempt, and restarts the previous configuration.

Check that the clone is enabled with `omarchy plugin list --json`. Open Agents
and verify that the weekly percentage and countdown fit without hovering;
visual verification remains manual. Subsequent setup runs skip a matching
active clone and print that the weekly display is already configured.

## Compact Window Layout and Focus Border

Setup appends the reviewed [compact layout](config/hypr/compact-layout.lua) to
`~/.config/hypr/looknfeel.lua`. It preserves unrelated settings, skips a matching
override, validates Lua, backs up changes, and reloads Hyprland. Failed
validation restores the file and reloads its previous configuration.

The settings use zero inner/outer gaps and a three-pixel border. Focused and
grouped borders use the current theme's `color6`, falling back to `accent`;
inactive borders use `background`. Missing palette values leave existing
border colors intact. Colors are read again when Hyprland reloads.

Verify the spacing and colors visually, including after a theme change.

## Displays and Ten Workspaces per Monitor

Setup appends [this PC's display profiles](config/hypr/displays.lua) to
`~/.config/hypr/monitors.lua`, preserving unrelated settings:

- Samsung LS27DG30X: confirmed description, 1920×1080 at 60 Hz, scale 1, `0x0`.
- BenQ G610HDAL: `HDMI-A-1`, 1366×768 at 59.79 Hz, scale 1, `auto-right`.
- GTK `GDK_SCALE=1`. Log out and back in for new application processes to
  inherit the setting.

Lua syntax, backups, repeat-run skips, and rollback follow the compact-layout
step. The BenQ's description and placement still need a live check after it is
reconnected; the fallback monitor rule remains in place for other displays.

Workspace placement uses **Omarchy 4.5's native ten slots per monitor**.
Each monitor's bar labels its slots locally; Hyprland uses global blocks of ten
IDs underneath. Super+1 through Super+0 select slots on the focused monitor,
with Omarchy's default move shortcuts and monitor hotplug behavior retained.
The old shared ten-workspace placement and Steam/chat routing are not installed.

To show all ten slots, including empty ones, setup clones `omarchy.workspaces`
into `~/.config/omarchy/plugins/<username>.workspaces/` and updates its button
list. The tenth label is `0`; active layout glyphs and guest workspaces are
preserved. This changes bar buttons, not the native workspace manager.

The staged widget's QML syntax is checked before installation. Backups live under
`${XDG_STATE_HOME:-$HOME/.local/state}/omarchy/backups/workspaces-widget-<timestamp>/`,
outside the watched plugin tree. An active, matching clone is skipped. The
shell is restarted after a change; failure restores the previous files and
removes a clone created by the failed attempt. Unexpected upstream widget
implementations stop the step for review.

The native plugin CLI uses `~/.config`; setup checks that location before
performing changes. Run these checks after applying setup:

```bash
hyprctl monitors all
hyprctl configerrors
hyprctl -j workspaces | jq 'sort_by(.id) | map({id, monitor, windows})'
```

Verify resolutions, non-overlapping positions, shortcuts on each monitor,
all ten buttons, and unplug/reconnect behavior. Hardware and visual checks
for the disconnected BenQ and monitor hotplug behavior remain outstanding.

## Ideas

These are future preferences; setup does not apply them:

- **Steam window layout:** arrange Library, Friends, and chat comfortably
  within the screen, using sizes suited to the connected display.
- **Optional app placement:** place Steam, Dota, and chat apps into chosen
  workspace slots when available, respecting manual moves, avoiding unwanted
  focus changes, and preserving Omarchy's native ten workspaces per monitor.

## Experimental: NVIDIA GPU Driver Update

This is a separate optional operation, not performed by `setup.py`:

```bash
omarchy update
omarchy system reboot
nvidia-smi
```

Run it only when specifically updating the system. Revalidate older game
workarounds after the update instead of reinstalling the old configuration tree.

## Apply Configs with an Agent

Follow the root [AGENTS.md](AGENTS.md). Implement the requested setup steps,
review them, and apply to the live desktop only when asked. Preserve unrelated
settings, validate each changed component, and report remaining manual checks.
Earlier source and instructions remain in Git history at commit `563f023`.

## Validate the Repository

Check source syntax before applying changes:

```bash
source .venv/bin/activate
python -m py_compile setup.py
luac -p config/hypr/*.lua
bash -n scripts/dota-close-guard.sh
```

These commands check syntax without applying desktop configuration. Setup also
validates staged QML and Lua before writing and checks installation results.
Application behavior and visual checks remain manual.
