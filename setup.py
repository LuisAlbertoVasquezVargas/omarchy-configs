# setup.py

import codecs
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
import getpass
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

import tomlkit

THEME_NAME = "Ghost Pastel"
THEME_URL = "https://github.com/row-huh/omarchy-ghost-pastel-theme"
COMMAND_HEARTBEAT_SECONDS = 15

class StepOutput:
    def __init__(self, label, terminal, logs):
        self.prefix = f"[{label}] "
        self.terminal = terminal
        self.logs = logs
        self.line_start = True

    def log_only(self, message):
        for log in self.logs:
            log.write(message)
            log.flush()

    def write(self, message):
        for line in message.splitlines(keepends=True):
            labeled = (self.prefix if self.line_start else "") + line
            self.terminal.write(labeled)
            self.log_only(labeled)
            self.line_start = line.endswith(("\n", "\r"))
        self.flush()
        return len(message)

    def flush(self):
        self.terminal.flush()
        for log in self.logs:
            log.flush()

def write_command_output(destination, message, hidden):
    if hidden:
        if isinstance(destination, StepOutput):
            destination.log_only(message)
    else:
        destination.write(message)
        destination.flush()

def run_command(command, *, input=None, capture_output=False, quiet=False, merge_errors=False, check=True, env=None):
    description = shlex.join(command)
    print(f"$ {description}", flush=True)
    started = time.monotonic()
    last_output = started
    # Independent file reads preserve the child's write position and avoid
    # waiting for desktop services that inherit its output to close a pipe.
    with (
        tempfile.TemporaryFile() as output,
        tempfile.TemporaryFile() as errors,
        tempfile.TemporaryFile() as source,
    ):
        if input is not None:
            source.write(input.encode("utf-8"))
            source.seek(0)
        with subprocess.Popen(
            command, stdin=source if input is not None else None,
            stdout=output, stderr=subprocess.STDOUT if merge_errors else errors, env=env,
        ) as process:
            streams = [(output, sys.stdout, capture_output or quiet), (errors, sys.stderr, False)]
            offsets = [0, 0]
            decoders = [codecs.getincrementaldecoder("utf-8")(errors="replace") for _ in streams]
            line_ended = [True, True]
            while True:
                finished = process.poll() is not None
                for index, (stream, destination, hidden) in enumerate(streams):
                    while chunk := os.pread(stream.fileno(), 65536, offsets[index]):
                        offsets[index] += len(chunk)
                        message = decoders[index].decode(chunk)
                        write_command_output(destination, message, hidden)
                        if message:
                            line_ended[index] = message.endswith(("\n", "\r"))
                        last_output = time.monotonic()
                    if finished:
                        tail = decoders[index].decode(b"", final=True)
                        write_command_output(destination, tail, hidden)
                        if tail or not line_ended[index]:
                            write_command_output(destination, "\n", hidden)
                if finished:
                    break
                now = time.monotonic()
                if now - last_output >= COMMAND_HEARTBEAT_SECONDS:
                    print(f"Still running (PID {process.pid}, {now - started:.0f}s): {description}", flush=True)
                    last_output = now
                try:
                    process.wait(timeout=0.1)
                except subprocess.TimeoutExpired:
                    pass
            output.seek(0)
            errors.seek(0)
            result = subprocess.CompletedProcess(
                command, process.returncode,
                stdout=output.read().decode("utf-8", errors="replace") if capture_output else None,
                stderr=errors.read().decode("utf-8", errors="replace"),
            )
    print(f"Command finished (exit {result.returncode}, {time.monotonic() - started:.1f}s).", flush=True)
    if check:
        result.check_returncode()
    return result

def command_output(command, **options):
    return run_command(command, capture_output=True, **options).stdout

def run_step(number, total, label, actions, log_directory, run_log):
    filename = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    log_file = log_directory / f"{number:02d}-{filename}.log"
    with log_file.open("x", encoding="utf-8") as step_log:
        output = StepOutput(label, sys.stdout, [run_log, step_log])
        with redirect_stdout(output), redirect_stderr(output):
            started = time.monotonic()
            print(f"START {number}/{total} | Log: {log_file}")
            try:
                for action in actions:
                    action()
            except BaseException as error:
                print(f"\nFAILED after {time.monotonic() - started:.1f}s: {error}")
                raise
            print(f"FINISHED after {time.monotonic() - started:.1f}s\n")

def omarchy_output(*arguments):
    return command_output(["omarchy", *arguments]).strip()

def verify_package_databases():
    repositories = command_output(["pacman-conf", "--repo-list"]).splitlines()
    if not repositories:
        raise RuntimeError("Pacman has no configured repositories. See README.md (Package Repository Databases).")

    database_directory = Path(command_output(["pacman-conf", "DBPath"]).strip()) / "sync"
    missing = []
    for repository in repositories:
        database = database_directory / f"{repository}.db"
        if not database.is_file() or database.stat().st_size == 0:
            missing.append(str(database))
    if missing:
        raise RuntimeError(
            "Pacman repository databases are missing or empty: " + ", ".join(missing)
            + ". Package installation cannot find targets without these indexes. "
            "No databases were refreshed or setup settings changed. "
            "Initialize repository metadata separately and review application dependency changes "
            "before installing packages; keep the Omarchy/desktop packages at 4.0.6. "
            "See README.md (Package Repository Databases)."
        )

    run_command(["pacman", "--sync", "--list", "--quiet"], quiet=True)
    print("Pacman repository databases are present and readable; no refresh performed.")

def install_ghost_pastel():
    installed_themes = omarchy_output("theme", "list").splitlines()

    if THEME_NAME in installed_themes:
        print("Ghost Pastel is already installed; skipping.")
        return

    print("Installing Ghost Pastel...", flush=True)
    run_command(["omarchy", "theme", "install", THEME_URL])

    if THEME_NAME not in omarchy_output("theme", "list").splitlines():
        raise RuntimeError("Ghost Pastel was not found after installation.")

    print("Ghost Pastel installed.")

def install_brave():
    if shutil.which("brave") is not None:
        print("Brave is already installed; skipping.")
        return

    print("Installing Brave...", flush=True)
    run_command(["omarchy", "install", "browser", "brave"])

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
        run_command(["omarchy", "default", "browser", "brave"])
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
    installed_packages = command_output(["pacman", "-Qq"]).splitlines()
    missing_packages = [package for package in required_packages if package not in installed_packages]

    if missing_packages:
        print(f"Installing Zathura dependencies: {', '.join(missing_packages)}...", flush=True)
        run_command(["omarchy", "pkg", "add", *missing_packages])
    else:
        print("Zathura packages are already installed; skipping installation.")

    version = command_output(["zathura", "--version"], merge_errors=True)
    if "pdf-mupdf" not in version:
        raise RuntimeError("Zathura's pdf-mupdf plugin is not available.")

def set_zathura_pdf_default():
    desktop_id = "org.pwmt.zathura.desktop"
    current_default = command_output(["xdg-mime", "query", "default", "application/pdf"]).strip()

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
        run_command(["xdg-mime", "default", desktop_id, "application/pdf"])
        current_default = command_output(["xdg-mime", "query", "default", "application/pdf"]).strip()
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
        command_output(["hyprctl", "reload"], merge_errors=True)
    except subprocess.CalledProcessError as error:
        details = error.output.strip() or str(error)
        raise RuntimeError(f"{label}: Hyprland reload failed: {details}") from error
    errors = command_output(["hyprctl", "configerrors"]).strip()
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
    run_command(["luac", "-p", "-"], input=updated)

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
        run_command(["codex", "features", "list"], quiet=True)
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
    run_command(["omarchy", "install", "gaming", "gpu-lib32"])
    run_command(["omarchy", "pkg", "add", "steam"])

    if shutil.which("steam") is None:
        raise RuntimeError("Steam was not found after installation.")

    print("Steam packages installed. Launch Steam manually to download/update the client and sign in.")

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
    for section in ["left", "center", "right"]:
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

def agents_weekly_panel_source(original):
    patch_file = Path(__file__).resolve().parent / "config/omarchy/agents-weekly.patch"
    sections = re.split(r"^@@[^\n]*\n", patch_file.read_text(), flags=re.MULTILINE)
    if len(sections) != 2:
        raise RuntimeError("The Agents weekly patch must contain exactly one hunk.")
    lines = sections[1].splitlines(keepends=True)
    before = "".join(line[1:] for line in lines if line.startswith((" ", "-")))
    after = "".join(line[1:] for line in lines if line.startswith((" ", "+")))
    if original.count(before) + original.count(after) != 1:
        raise RuntimeError("Agents widget implementation changed; review it before applying this step.")
    return original.replace(before, after, 1)

def configure_agents_widget():
    configure_cloned_widget(
        "omarchy.agents", "Agents weekly percentage and reset countdown", agents_weekly_panel_source,
    )

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
    run_command(["luac", "-p", "-"], input=updated)
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

def report_workspaces():
    current_version = omarchy_output("version")
    print(f"Using native Omarchy {current_version} workspaces: global IDs 1-10 with the default shortcuts.")

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

    run_command(["bash", "-n", str(source)])

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
    old_code = """  function workspaceIds() {
    var ids = [1, 2, 3, 4, 5]
    var values = Hyprland.workspaces.values
"""
    new_code = """  function workspaceIds() {
    var ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    var values = Hyprland.workspaces.values
"""
    if original.count(old_code) + original.count(new_code) != 1:
        raise RuntimeError("Workspace widget implementation changed; review it before applying this step.")
    return original.replace(old_code, new_code, 1)

def configure_workspace_buttons():
    configure_cloned_widget(
        "omarchy.workspaces", "All ten workspace buttons", workspace_button_source,
    )

def configure_cloned_widget(source_id, label, update_source):
    plugin_id = f"{os.environ.get('USER') or getpass.getuser()}.{source_id.removeprefix('omarchy.')}"
    config_directory = Path.home() / ".config/omarchy"
    plugin_directory = config_directory / "plugins" / plugin_id
    shell_file = config_directory / "shell.json"
    shell_existed = shell_file.exists()

    if plugin_directory.is_symlink():
        raise RuntimeError(f"{plugin_directory} must be a user-owned plugin directory, not a symlink.")
    plugin_existed = plugin_directory.exists()
    if plugin_existed:
        manifest = json.loads((plugin_directory / "manifest.json").read_text())
        if manifest.get("id") != plugin_id or manifest.get("omarchy", {}).get("clonedFrom") != source_id:
            raise RuntimeError(f"{plugin_directory} is not a clone of {source_id}.")
        filename = manifest["entryPoints"]["barWidget"]
        widget_file = plugin_directory / filename
        if widget_file.is_symlink() or not widget_file.resolve().is_relative_to(plugin_directory.resolve()):
            raise RuntimeError("The widget must be a regular file inside its clone.")
    else:
        catalog = json.loads(omarchy_output("plugin", "catalog"))
        source = next((plugin for plugin in catalog if plugin["id"] == source_id and plugin["firstParty"]), None)
        if source is None:
            raise RuntimeError(f"Built-in widget was not found: {source_id}")
        manifest = json.loads(Path(source["manifestPath"]).read_text())
        filename = manifest["entryPoints"]["barWidget"]
        widget_file = Path(source["barWidgetPath"])

    original = widget_file.read_text()
    updated = update_source(original)
    shell_settings = json.loads(shell_file.read_text()) if shell_existed else {}
    layout = shell_settings.get("bar", {}).get("layout", {})
    active_ids = {entry["id"] for entries in layout.values() for entry in entries}
    if original == updated and plugin_id in active_ids:
        print(f"{label} is already configured; skipping.")
        return

    with tempfile.TemporaryDirectory(prefix="widget-check-") as temporary:
        staged_widget = Path(temporary) / Path(filename).name
        staged_widget.write_text(updated)
        run_command(
            ["/usr/lib/qt6/bin/qmlformat", "--ignore-settings", str(staged_widget)],
            quiet=True,
        )

    state_directory = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_directory = state_directory / "omarchy/backups" / f"{source_id.removeprefix('omarchy.')}-widget-{timestamp}"
    backup_directory.mkdir(parents=True)
    if shell_existed:
        shutil.copy2(shell_file, backup_directory / "shell.json")
    if plugin_existed:
        shutil.copy2(widget_file, backup_directory / Path(filename).name)
    print(f"{label} backups saved to {backup_directory}", flush=True)

    try:
        if not plugin_existed:
            run_command(["omarchy", "plugin", "clone", source_id])
        widget_file = plugin_directory / filename
        widget_file.write_text(updated)
        if plugin_existed and plugin_id not in active_ids:
            run_command(["omarchy", "plugin", "enable", plugin_id])
        run_command(["omarchy", "restart", "shell"])
        plugins = json.loads(omarchy_output("plugin", "list", "--json"))
        if not any(plugin["id"] == plugin_id and plugin.get("enabled") for plugin in plugins):
            raise RuntimeError(f"{plugin_id} did not become enabled after the shell restart.")
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError):
        if shell_existed:
            shutil.copy2(backup_directory / "shell.json", shell_file)
        else:
            shell_file.unlink(missing_ok=True)
        if plugin_existed:
            shutil.copy2(backup_directory / Path(filename).name, widget_file)
        elif plugin_directory.is_dir():
            shutil.rmtree(plugin_directory)
        run_command(["omarchy", "restart", "shell"], check=False)
        raise

    print(f"{label} configured and enabled as {plugin_id}.")

def verify_environment():
    if len(sys.argv) > 1:
        raise RuntimeError("This script takes no arguments. Run: python setup.py")
    if os.geteuid() == 0:
        raise RuntimeError("Run setup as your desktop user, without sudo.")
    if shutil.which("omarchy") is None:
        raise RuntimeError("Run this script on an Omarchy desktop.")

    version = omarchy_output("version")
    if version.split("-", 1)[0] != "4.0.6":
        raise RuntimeError(f"This emergency branch requires Omarchy 4.0.6; installed version is {version}. Install or restore 4.0.6 separately. No setup steps were applied.")
    if not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        raise RuntimeError("Run setup from a terminal inside your active Omarchy desktop session.")

    config_directory = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    if config_directory.resolve() != (Path.home() / ".config").resolve():
        raise RuntimeError("Omarchy 4.0.6's plugin CLI writes to ~/.config; this desktop setup requires that configuration location.")
    for executable in ("hyprctl", "luac", "bash", "pacman", "pacman-conf", "/usr/lib/qt6/bin/qmlformat"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Required validation tool is missing: {executable}. No setup steps were applied.")
    errors = command_output(["hyprctl", "configerrors"]).strip()
    if errors:
        raise RuntimeError(f"Resolve existing Hyprland configuration errors before setup: {errors}")
    for name in ("hyprland.lua", "bindings.lua"):
        path = config_directory / "hypr" / name
        content = path.read_text()
        retired = ("hypr.steam-workspaces", "hypr.chat-workspaces", "hypr.repo-workspaces", "steam_window_geometries", "local connected_monitors")
        if any(marker in content for marker in retired) or re.search(r"\bfor\s+workspace\s*=\s*8\s*,\s*10\s+do\b", content):
            raise RuntimeError(f"Retired workspace or app-routing overrides found in {path}. Review them before using native 4.0.6 workspaces; see README.md (Displays and Ten Workspaces). No setup steps were applied.")

def main():
    steps = [
        ("Environment", [verify_environment, verify_package_databases]),
        ("Ghost Pastel Theme", [install_ghost_pastel]),
        ("Brave", [install_brave, set_brave_default]),
        ("WhatsApp", [report_whatsapp]),
        ("Slack", [report_slack]),
        ("Discord", [report_discord]),
        ("Zathura", [install_zathura, set_zathura_pdf_default]),
        ("Neovim", [configure_neo_tree]),
        ("Codex CLI Approval Defaults", [configure_codex_defaults]),
        ("Steam", [install_steam]),
        ("Disable Super+W While Dota 2 Runs", [configure_dota_close_guard]),
        ("Clock Format", [configure_clock_format]),
        ("Agents Widget", [configure_agents_widget]),
        ("Compact Window Layout and Focus Border", [configure_compact_layout]),
        ("Displays and Ten Workspaces", [
            configure_displays, configure_workspace_buttons, report_workspaces,
        ]),
    ]
    state_directory = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    log_directory = state_directory / "omarchy-configs/logs" / timestamp
    log_directory.mkdir(mode=0o700, parents=True)
    print(f"Setup logs: {log_directory}", flush=True)
    with (log_directory / "setup.log").open("x", encoding="utf-8") as run_log:
        for number, (label, actions) in enumerate(steps, start=1):
            run_step(number, len(steps), label, actions, log_directory, run_log)
        message = f"Setup finished: {len(steps)}/{len(steps)} steps. Manual checks remain in README.md. Logs: {log_directory}"
        print(message, flush=True)
        run_log.write(message + "\n")

if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
