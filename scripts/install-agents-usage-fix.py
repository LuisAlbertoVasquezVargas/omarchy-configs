#!/usr/bin/python3
"""Install a user-owned Agents clone; never modify packaged Omarchy files."""

from datetime import datetime
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess


def main():
    source = Path(os.environ.get("OMARCHY_PATH", "/usr/share/omarchy"))
    config = Path.home() / ".config/omarchy"
    plugin_id = f"{os.environ.get('USER') or getpass.getuser()}.agents"
    target = config / "plugins" / plugin_id
    scripts = Path(__file__).resolve().parent
    updater = (source / "bin/omarchy-agent-usage-update").read_text()
    collect_line = '  collect "$collector" "$agent" &'
    if updater.count(collect_line) != 1:
        raise SystemExit("Installed updater changed; review it before applying this fix.")
    updater = updater.replace(collect_line,
        '  if [[ $agent == codex ]]; then\n'
        '    collector="$(dirname -- "$0")/codex-usage-collector.py"\n'
        '  fi\n' + collect_line)

    main_qml = target / "Main.qml"
    original = 'var command = ["omarchy-agent-usage-update"]'
    replacement = f'var command = [{json.dumps(str(target / "usage-update"))}]'
    qml = (main_qml if target.exists() else source / "shell/plugins/agents/Main.qml").read_text()
    if qml.count(original) != 1 and qml.count(replacement) != 1:
        raise SystemExit("Agents Main.qml changed; review it before applying this fix.")
    if target.exists():
        manifest = json.loads((target / "manifest.json").read_text())
        if manifest.get("omarchy", {}).get("clonedFrom") != "omarchy.agents":
            raise SystemExit("Existing target is not a clone of omarchy.agents.")

    # Back up outside the watched plugin tree to avoid duplicate plugin IDs.
    backup = Path.home() / ".local/state/omarchy/backups" / (
        "agents-usage-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    shutil.copy2(config / "shell.json", backup / "shell.json")
    if target.exists():
        shutil.copytree(target, backup / plugin_id)
    else:
        subprocess.run(["omarchy", "plugin", "clone", "omarchy.agents"], check=True)

    shutil.copy2(scripts / "codex-usage-collector.py", target / "codex-usage-collector.py")
    (target / "codex-usage-collector.py").chmod(0o755)
    (target / "usage-update").write_text(updater)
    (target / "usage-update").chmod(0o755)
    main_qml.write_text(qml.replace(original, replacement))
    subprocess.run(["omarchy", "plugin", "enable", plugin_id], check=True)
    subprocess.run([str(target / "usage-update"), "--force", "codex"], check=True)
    # A registry rescan can retain imported Main.qml in Qt's component cache.
    # Restart the shell so the widget actually runs the new updater command.
    subprocess.run(["omarchy", "restart", "shell"], check=True)
    print(f"Installed {plugin_id}. Backup: {backup}")


if __name__ == "__main__":
    main()
