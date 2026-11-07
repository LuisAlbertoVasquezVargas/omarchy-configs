# setup.py

from datetime import datetime
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import tomlkit

THEME_NAME = "Ghost Pastel"
THEME_URL = "https://github.com/row-huh/omarchy-ghost-pastel-theme"

def omarchy_output(*arguments):
    result = subprocess.run(
        ["omarchy", *arguments],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.stdout.strip()

def install_ghost_pastel():
    installed_themes = omarchy_output("theme", "list").splitlines()

    if THEME_NAME in installed_themes:
        print("Ghost Pastel is already installed; skipping.")
        return

    print("Installing Ghost Pastel...", flush=True)
    subprocess.run(["omarchy", "theme", "install", THEME_URL], check=True)

    if THEME_NAME not in omarchy_output("theme", "list").splitlines():
        raise RuntimeError("Ghost Pastel was not found after installation.")

    print("Ghost Pastel installed.")

def install_brave():
    if shutil.which("brave") is not None:
        print("Brave is already installed; skipping.")
        return

    print("Installing Brave...", flush=True)
    subprocess.run(["omarchy", "install", "browser", "brave"], check=True)

    if shutil.which("brave") is None:
        raise RuntimeError("Brave was not found after installation.")

    print("Brave installed.")

def set_brave_default():
    current_default = omarchy_output("default", "browser")
    if current_default == "brave":
        print("Brave is already the default browser; skipping.")
        return

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    mime_settings = config_directory / "mimeapps.list"
    backup = None
    if mime_settings.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = mime_settings.with_name(f"mimeapps.list.backup-{timestamp}")
        shutil.copy2(mime_settings, backup)
        print(f"MIME settings backed up to {backup}", flush=True)

    config_directory.mkdir(parents=True, exist_ok=True)
    print("Setting Brave as the default browser...", flush=True)
    try:
        subprocess.run(["omarchy", "default", "browser", "brave"], check=True)
        if omarchy_output("default", "browser") != "brave":
            raise RuntimeError("Brave is not the default browser after configuration.")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        if backup is None:
            mime_settings.unlink(missing_ok=True)
        else:
            shutil.copy2(backup, mime_settings)
        raise

    print("Brave set as the default browser.")

def report_whatsapp():
    current_version = omarchy_output("version")
    print(f"WhatsApp already installed in version {current_version}")

def report_slack():
    print("Slack can be installed as a service.")

def report_discord():
    current_version = omarchy_output("version")
    print(f"Discord already installed in version {current_version}")

def install_zathura():
    required_packages = ["zathura", "zathura-pdf-mupdf", "xdg-utils"]
    installed_packages = subprocess.check_output(["pacman", "-Qq"], text=True).splitlines()
    missing_packages = [package for package in required_packages if package not in installed_packages]

    if missing_packages:
        print(f"Installing Zathura dependencies: {', '.join(missing_packages)}...", flush=True)
        subprocess.run(["omarchy", "pkg", "add", *missing_packages], check=True)
    else:
        print("Zathura packages are already installed; skipping installation.")

    version = subprocess.check_output(["zathura", "--version"], text=True, stderr=subprocess.STDOUT)
    if "pdf-mupdf" not in version:
        raise RuntimeError("Zathura's pdf-mupdf plugin is not available.")

def set_zathura_pdf_default():
    desktop_id = "org.pwmt.zathura.desktop"
    current_default = subprocess.check_output(
        ["xdg-mime", "query", "default", "application/pdf"], text=True
    ).strip()

    if current_default == desktop_id:
        print("Zathura is already the default PDF reader; skipping.")
        return

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    mime_settings = config_directory / "mimeapps.list"
    backup = None
    if mime_settings.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = mime_settings.with_name(f"mimeapps.list.backup-{timestamp}")
        shutil.copy2(mime_settings, backup)
        print(f"MIME settings backed up to {backup}", flush=True)

    config_directory.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["xdg-mime", "default", desktop_id, "application/pdf"], check=True)
        current_default = subprocess.check_output(
            ["xdg-mime", "query", "default", "application/pdf"], text=True
        ).strip()
        if current_default != desktop_id:
            raise RuntimeError("Zathura is not the default PDF reader after configuration.")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        if backup is None:
            mime_settings.unlink(missing_ok=True)
        else:
            shutil.copy2(backup, mime_settings)
        raise

    print("Zathura set as the default PDF reader.")

def reload_hyprland(label):
    try:
        subprocess.check_output(["hyprctl", "reload"], text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        details = error.output.strip() or str(error)
        raise RuntimeError(f"{label}: Hyprland reload failed: {details}") from error
    errors = subprocess.check_output(["hyprctl", "configerrors"], text=True).strip()
    if errors:
        raise RuntimeError(f"{label}: Hyprland configuration errors: {errors}")
    print(f"{label}: Hyprland reloaded; no configuration errors.", flush=True)

def configure_neovim_plugin(filename, specification, label):
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    plugin_file = config_directory / "nvim/lua/plugins" / filename
    original = plugin_file.read_text() if plugin_file.exists() else ""

    if original.rstrip().endswith(specification.rstrip()):
        print(f"{label} is already configured; skipping.")
        return

    preserved_specs = f"  (function(...)\n{original}\n  end)(...),\n" if original.strip() else ""
    header = f"-- nvim/lua/plugins/{filename}\n\nreturn {{\n"
    updated = header + preserved_specs + specification
    subprocess.run(["luac", "-p", "-"], input=updated, text=True, check=True)

    if plugin_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = plugin_file.with_name(f"{filename}.backup-{timestamp}")
        shutil.copy2(plugin_file, backup)
        print(f"{label} settings backed up to {backup}", flush=True)

    plugin_file.parent.mkdir(parents=True, exist_ok=True)
    plugin_file.write_text(updated)
    print(f"{label} configured. Restart Neovim to apply.")

def configure_neo_tree():
    specification = """  {
    "nvim-neo-tree/neo-tree.nvim",
    opts = {
      filesystem = {
        filtered_items = {
          visible = true,
        },
      },
    },
  },
}
"""

    configure_neovim_plugin("neo-tree.lua", specification, "Neo-tree visibility")

def configure_codex_defaults():
    if shutil.which("codex") is None:
        raise RuntimeError("Install the Codex CLI before configuring its defaults.")

    config_directory = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    config_file = config_directory / "config.toml"
    original = config_file.read_text() if config_file.exists() else "# config.toml\n\n"
    try:
        configuration = tomlkit.parse(original)
    except tomlkit.exceptions.ParseError as error:
        raise RuntimeError(f"Invalid Codex configuration: {error}") from error

    defaults = {
        "approval_policy": "on-request",
        "approvals_reviewer": "auto_review",
        "sandbox_mode": "workspace-write",
    }
    if all(configuration.get(key) == value for key, value in defaults.items()):
        print("Codex approval defaults are already configured; skipping.")
        return

    for key, value in defaults.items():
        configuration[key] = value

    backup = None
    if config_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = config_file.with_name(f"config.toml.backup-{timestamp}")
        shutil.copy2(config_file, backup)
        print(f"Codex settings backed up to {backup}", flush=True)

    config_directory.mkdir(parents=True, exist_ok=True)
    try:
        config_file.write_text(tomlkit.dumps(configuration), encoding="utf-8")
        subprocess.run(["codex", "features", "list"], stdout=subprocess.DEVNULL, check=True)
    except (OSError, subprocess.CalledProcessError):
        if backup is None:
            config_file.unlink(missing_ok=True)
        else:
            shutil.copy2(backup, config_file)
        raise

    print("Codex approval defaults configured. Start a new Codex session to apply.")

def install_steam():
    if shutil.which("steam") is not None:
        print("Steam is already installed; skipping.")
        return

    print("Installing Steam...", flush=True)
    subprocess.run(["omarchy", "install", "gaming", "steam"], check=True)

    if shutil.which("steam") is None:
        raise RuntimeError("Steam was not found after installation.")

    print("Steam installed.")

def configure_bar_widget(widget_id, default_section, settings, label):
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    config_file = (config_directory / "omarchy/shell.json").resolve()
    configuration = json.loads(config_file.read_text()) if config_file.exists() else {}
    if not isinstance(configuration, dict):
        raise RuntimeError("Omarchy shell configuration must be a JSON object.")

    bar = configuration.setdefault("bar", {})
    if not isinstance(bar, dict):
        raise RuntimeError("Omarchy bar configuration must be a JSON object.")
    if "layout" not in bar:
        omarchy_directory = Path(os.environ.get("OMARCHY_PATH") or "/usr/share/omarchy")
        defaults = json.loads((omarchy_directory / "config/omarchy/shell.json").read_text())
        bar["layout"] = defaults["bar"]["layout"]

    layout = bar["layout"]
    if not isinstance(layout, dict):
        raise RuntimeError("Omarchy bar layout must be a JSON object.")
    matches = []
    legacy_id = f"{os.environ.get('USER') or getpass.getuser()}." + widget_id.removeprefix("omarchy.")
    for section in ["left", "centerBegin", "center", "centerEnd", "right", "tray"]:
        entries = layout.get(section, [])
        if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
            raise RuntimeError(f"Invalid Omarchy bar section: {section}")
        matches.extend(entry for entry in entries if entry.get("id") in [widget_id, legacy_id])
    if len(matches) > 1:
        raise RuntimeError(f"Multiple entries found for {widget_id}; resolve the duplicate entries first.")
    if matches:
        widget = matches[0]
    else:
        widget = {"id": widget_id}
        layout.setdefault(default_section, []).append(widget)

    if all(widget.get(key) == value and type(widget.get(key)) is type(value) for key, value in settings.items()):
        print(f"{label} is already configured; skipping.")
        return
    widget.update(settings)

    if config_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = config_file.with_name(f"shell.json.backup-{timestamp}")
        shutil.copy2(config_file, backup)
        print(f"Shell settings backed up to {backup}", flush=True)

    config_file.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=config_file.parent, prefix=".shell-", suffix=".tmp", delete=False
    ) as temporary:
        temporary.write(json.dumps(configuration, ensure_ascii=False, indent=2) + "\n")
        temporary_file = Path(temporary.name)
    try:
        if config_file.exists():
            shutil.copymode(config_file, temporary_file)
        temporary_file.replace(config_file)
    finally:
        temporary_file.unlink(missing_ok=True)

    print(f"{label} configured. Check the bar; the shell reloads automatically.")

def configure_clock_format():
    formats = {
        "format": "dd MMM ddd · 'W'ww · HH:mm",
        "formatAlt": "dd MMM ddd · 'W'ww · HH:mm",
        "verticalFormat": "HH\n—\nmm",
    }
    configure_bar_widget("omarchy.clock", "center", formats, "Clock format")

def report_agents_widget():
    current_version = omarchy_output("version")
    print(f"Agents widget left unchanged on Omarchy {current_version}; existing user clones are preserved.")

def configure_hyprland_override(filename, source_name, label):
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    config_file = config_directory / "hypr" / filename
    source_file = Path(__file__).resolve().parent / "config/hypr" / source_name
    override = source_file.read_text()
    original = config_file.read_text()

    reload_hyprland(f"{label} check")
    if original.rstrip().endswith(override.rstrip()):
        print(f"{label} is already configured; skipping.")
        return

    updated = original.rstrip() + "\n\n" + override
    subprocess.run(["luac", "-p", "-"], input=updated, text=True, check=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = config_file.with_name(f"{filename}.backup-{timestamp}")
    shutil.copy2(config_file, backup)
    print(f"{label} settings backed up to {backup}", flush=True)

    try:
        config_file.write_text(updated)
        reload_hyprland(f"{label} update")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        shutil.copy2(backup, config_file)
        reload_hyprland(f"{label} restore")
        raise

    print(f"{label} configured.")

def configure_compact_layout():
    configure_hyprland_override("looknfeel.lua", "compact-layout.lua", "Compact layout and theme borders")

def configure_displays():
    configure_hyprland_override("monitors.lua", "displays.lua", "Samsung and BenQ display profiles")

def report_monitor_workspaces():
    current_version = omarchy_output("version")
    print(f"Using native Omarchy workspace behavior: 10 workspaces per monitor in version {current_version}")

def configure_dota_close_guard():
    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    destination = config_directory / "hypr/dota-close-guard.sh"
    if destination.is_symlink():
        raise RuntimeError("The Dota close-window helper must be a regular user-owned file.")
    source = Path(__file__).resolve().parent / "scripts/dota-close-guard.sh"
    original = destination.read_text() if destination.exists() else None
    updated = source.read_text()
    already_installed = original == updated and destination.stat().st_mode & 0o777 == 0o755
    backup = None

    if already_installed:
        print("Dota close-window guard is already installed; skipping the helper copy.")
    else:
        if original is not None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backup = destination.with_name(f"dota-close-guard.sh.backup-{timestamp}")
            shutil.copy2(destination, backup)
            print(f"Close-window guard backed up to {backup}", flush=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(updated)
        destination.chmod(0o755)

    try:
        configure_hyprland_override("bindings.lua", "dota-close-binding.lua", "Super+W Dota guard")
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        if not already_installed:
            if backup is None:
                destination.unlink(missing_ok=True)
            else:
                shutil.copy2(backup, destination)
        raise

    print("Super+W closes the focused window unless this user's Dota 2 process is running.")

def workspace_button_source(original):
    old_code = """  // The first five of the monitor's own, and any of the rest that exist. After
  // them come workspaces that are only visiting: those of a monitor that is
  // unplugged, which had no room to join this one's.
  function workspaceIds() {
    var base = root.block * root.slots
    var ids = [base + 1, base + 2, base + 3, base + 4, base + 5]
"""
    new_code = """  function workspaceIds() {
    var base = root.block * root.slots
    var ids = []
    for (var slot = 1; slot <= root.slots; slot++) ids.push(base + slot)
"""
    if original.count(old_code) + original.count(new_code) != 1:
        raise RuntimeError("Workspace widget implementation changed; review it before applying this step.")
    return original.replace(old_code, new_code, 1)

def configure_workspace_buttons():
    plugin_id = f"{os.environ.get('USER') or getpass.getuser()}.workspaces"
    config_directory = Path.home() / ".config/omarchy"
    plugin_directory = config_directory / "plugins" / plugin_id
    shell_file = config_directory / "shell.json"
    plugin_existed = plugin_directory.exists() or plugin_directory.is_symlink()
    shell_existed = shell_file.exists()

    if plugin_existed:
        manifest = json.loads((plugin_directory / "manifest.json").read_text())
        if manifest.get("id") != plugin_id or manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.workspaces":
            raise RuntimeError(f"{plugin_directory} is not a clone of omarchy.workspaces.")
        filename = manifest["entryPoints"]["barWidget"]
        widget_file = plugin_directory / filename
        if widget_file.is_symlink() or not widget_file.resolve().is_relative_to(plugin_directory.resolve()):
            raise RuntimeError("The workspace widget must be a regular file inside its clone.")
    else:
        catalog = json.loads(omarchy_output("plugin", "catalog"))
        source = next((plugin for plugin in catalog if plugin["id"] == "omarchy.workspaces" and plugin["firstParty"]), None)
        if source is None:
            raise RuntimeError("Built-in workspace widget was not found.")
        manifest = json.loads(Path(source["manifestPath"]).read_text())
        filename = manifest["entryPoints"]["barWidget"]
        widget_file = Path(source["barWidgetPath"])

    original = widget_file.read_text()
    updated = workspace_button_source(original)
    shell_settings = json.loads(shell_file.read_text()) if shell_existed else {}
    layout = shell_settings.get("bar", {}).get("layout", {})
    active_ids = {entry["id"] for entries in layout.values() for entry in entries}
    if original == updated and plugin_id in active_ids:
        print("All ten workspace buttons are already configured; skipping.")
        return

    test_file = Path(__file__).resolve().parent / "tests/workspace-buttons.test.cjs"
    with tempfile.TemporaryDirectory(prefix="workspace-widget-check-") as temporary:
        staged_widget = Path(temporary) / Path(filename).name
        staged_widget.write_text(updated)
        subprocess.run(
            ["/usr/lib/qt6/bin/qmlformat", "--ignore-settings", str(staged_widget)],
            stdout=subprocess.DEVNULL, check=True,
        )
        try:
            subprocess.check_output(
                ["node", str(test_file)], env=dict(os.environ, WIDGET_QML_PATH=str(staged_widget)),
                stderr=subprocess.STDOUT, text=True,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"Workspace button checks failed:\n{error.output}") from error

    state_directory = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_directory = state_directory / "omarchy/backups" / f"workspaces-widget-{timestamp}"
    backup_directory.mkdir(parents=True)
    if shell_existed:
        shutil.copy2(shell_file, backup_directory / "shell.json")
    if plugin_existed:
        shutil.copy2(widget_file, backup_directory / Path(filename).name)
    print(f"Workspace widget backups saved to {backup_directory}", flush=True)

    try:
        if not plugin_existed:
            subprocess.run(["omarchy", "plugin", "clone", "omarchy.workspaces"], check=True)
        widget_file = plugin_directory / filename
        widget_file.write_text(updated)
        if plugin_existed and plugin_id not in active_ids:
            subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
        subprocess.run(["omarchy", "restart", "shell"], check=True)
    except (OSError, subprocess.CalledProcessError):
        if shell_existed:
            shutil.copy2(backup_directory / "shell.json", shell_file)
        else:
            shell_file.unlink(missing_ok=True)
        if plugin_existed:
            shutil.copy2(backup_directory / Path(filename).name, widget_file)
        elif plugin_directory.is_dir():
            shutil.rmtree(plugin_directory)
        subprocess.run(["omarchy", "restart", "shell"], check=False)
        raise

    print("All ten workspace buttons configured; native per-monitor workspace behavior is unchanged.")

def verify_environment():
    if len(sys.argv) > 1:
        raise RuntimeError("This script takes no arguments. Run: python setup.py")
    if os.geteuid() == 0:
        raise RuntimeError("Run setup as your desktop user, without sudo.")
    if shutil.which("omarchy") is None:
        raise RuntimeError("Run this script on an Omarchy desktop.")

    version = omarchy_output("version")
    if version.split("-", 1)[0] != "4.5.0":
        raise RuntimeError(f"This setup targets Omarchy 4.5.0 (Quattro RS); installed version is {version}. No setup steps were applied.")
    if not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        raise RuntimeError("Run setup from a terminal inside your active Omarchy desktop session.")

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    if config_directory.resolve() != (Path.home() / ".config").resolve():
        raise RuntimeError("Omarchy 4.5's plugin CLI writes to ~/.config; this desktop setup requires that configuration location.")
    for name in ("hyprland.lua", "bindings.lua"):
        path = config_directory / "hypr" / name
        content = path.read_text()
        retired = ("hypr.steam-workspaces", "hypr.chat-workspaces", "hypr.repo-workspaces", "steam_window_geometries", "local connected_monitors")
        if any(marker in content for marker in retired) or re.search(r"\bfor\s+workspace\s*=\s*8\s*,\s*10\s+do\b", content):
            raise RuntimeError(f"Legacy 4.0 overrides found in {path}. Review them before using native 4.5 workspaces; see docs/QUATTRO-4.0.md. No setup steps were applied.")

def main():
    verify_environment()
    install_ghost_pastel()
    install_brave()
    set_brave_default()
    report_whatsapp()
    report_slack()
    report_discord()
    install_zathura()
    set_zathura_pdf_default()
    configure_neo_tree()
    configure_codex_defaults()
    install_steam()
    configure_dota_close_guard()
    configure_clock_format()
    report_agents_widget()
    configure_compact_layout()
    configure_displays()
    configure_workspace_buttons()
    report_monitor_workspaces()

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
