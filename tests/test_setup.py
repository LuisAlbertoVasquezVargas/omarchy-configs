# tests/test_setup.py

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import tomlkit

REPOSITORY = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("desktop_setup", REPOSITORY / "setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
REAL_RUN = subprocess.run

class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.environment = patch.dict(os.environ, {
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_STATE_HOME": str(self.home / ".local/state"),
            "CODEX_HOME": str(self.home / "codex"),
            "HYPRLAND_INSTANCE_SIGNATURE": "unit-test-session",
            "USER": "desktop-test",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        home_patch = patch.object(setup.Path, "home", return_value=self.home)
        home_patch.start()
        self.addCleanup(home_patch.stop)
        output = redirect_stdout(StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)
        self.write(".config/hypr/hyprland.lua", 'require("default.hypr.omarchy")\n')
        self.write(".config/hypr/bindings.lua", "-- Keep my bindings.\n")
        self.write(".config/hypr/monitors.lua", 'local omarchy_monitor_scale = "auto"\n')
        self.write(".config/hypr/looknfeel.lua", "-- Keep my appearance.\n")

    def write(self, relative, content):
        path = self.home / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def shell_settings(self, widget=None):
        return {
            "idle": {"lock": 900},
            "plugins": ["keep-this-plugin"],
            "bar": {"layout": {
                "left": [{"id": "custom.left"}],
                "center": [widget or {"id": "omarchy.clock", "format": "old", "custom": True}],
                "right": [{"id": "desktop-test.agents"}],
            }},
        }

    def test_arguments_are_rejected_before_any_command(self):
        with patch.object(sys, "argv", ["setup.py", "--apply"]), patch.object(setup, "omarchy_output") as output:
            with self.assertRaisesRegex(RuntimeError, "takes no arguments"):
                setup.verify_environment()
        output.assert_not_called()

    def test_old_omarchy_stops_main_before_installing_anything(self):
        with (
            patch.object(sys, "argv", ["setup.py"]),
            patch.object(setup.os, "geteuid", return_value=1000),
            patch.object(setup.shutil, "which", return_value="/usr/bin/omarchy"),
            patch.object(setup, "omarchy_output", return_value="4.0.6-1"),
            patch.object(setup, "install_ghost_pastel") as install,
        ):
            with self.assertRaisesRegex(RuntimeError, "4.5.0.*4.0.6-1"):
                setup.main()
        install.assert_not_called()
        self.assertFalse((self.home / "codex").exists())

    def test_45_package_revision_is_accepted_and_legacy_rules_are_rejected(self):
        with (
            patch.object(sys, "argv", ["setup.py"]),
            patch.object(setup.os, "geteuid", return_value=1000),
            patch.object(setup.shutil, "which", return_value="/usr/bin/omarchy"),
            patch.object(setup, "omarchy_output", return_value="4.5.0-3"),
        ):
            setup.verify_environment()
            path = self.write(".config/hypr/hyprland.lua", 'require("hypr.steam-workspaces")\n')
            with self.assertRaisesRegex(RuntimeError, "Legacy 4.0"):
                setup.verify_environment()
            self.assertEqual(path.read_text(), 'require("hypr.steam-workspaces")\n')

    def test_matching_theme_and_installed_brave_are_skipped(self):
        with patch.object(setup, "omarchy_output", return_value="Ghost Pastel"), patch.object(setup.subprocess, "run") as run:
            setup.install_ghost_pastel()
            run.assert_not_called()
        with patch.object(setup.shutil, "which", return_value="/usr/bin/brave"), patch.object(setup.subprocess, "run") as run:
            setup.install_brave()
            run.assert_not_called()

    def test_missing_browser_after_installation_is_a_failure(self):
        with patch.object(setup.shutil, "which", return_value=None), patch.object(setup.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "Brave was not found"):
                setup.install_brave()
        run.assert_called_once_with(["omarchy", "install", "browser", "brave"], check=True)

    def test_browser_failure_restores_existing_mime_settings(self):
        path = self.write(".config/mimeapps.list", "keep the PDF association\n")
        def change_default(*arguments, **options):
            path.write_text("failed browser update")
        with patch.object(setup, "omarchy_output", side_effect=["chromium", "chromium"]), patch.object(setup.subprocess, "run", side_effect=change_default):
            with self.assertRaisesRegex(RuntimeError, "not the default browser"):
                setup.set_brave_default()
        self.assertEqual(path.read_text(), "keep the PDF association\n")
        self.assertEqual(len(list(path.parent.glob("mimeapps.list.backup-*"))), 1)

    def test_pdf_failure_restores_existing_mime_settings(self):
        path = self.write(".config/mimeapps.list", "keep the browser association\n")
        def change_default(*arguments, **options):
            path.write_text("failed PDF update")
        with patch.object(setup.subprocess, "check_output", side_effect=["other.desktop", "wrong.desktop"]), patch.object(setup.subprocess, "run", side_effect=change_default):
            with self.assertRaisesRegex(RuntimeError, "not the default PDF reader"):
                setup.set_zathura_pdf_default()
        self.assertEqual(path.read_text(), "keep the browser association\n")

    def test_zathura_requires_its_pdf_plugin(self):
        with (
            patch.object(setup.subprocess, "check_output", side_effect=["zathura\nzathura-pdf-mupdf\nxdg-utils\n", "zathura 0.5"]),
            patch.object(setup.subprocess, "run") as run,
        ):
            with self.assertRaisesRegex(RuntimeError, "pdf-mupdf"):
                setup.install_zathura()
        run.assert_not_called()

    def test_codex_preserves_toml_comments_profiles_and_multiline_strings(self):
        original = '# Keep this comment\nmodel = "existing-model"\ninstructions = """hello\n[text, not a table]\nworld"""\n[profiles.custom]\nsandbox_mode = "read-only"\n'
        path = self.write("codex/config.toml", original)
        with patch.object(setup.shutil, "which", return_value="/usr/bin/codex"), patch.object(setup.subprocess, "run") as run:
            setup.configure_codex_defaults()
            updated = path.read_text()
            setup.configure_codex_defaults()
        self.assertEqual(run.call_count, 1)
        values = tomlkit.parse(updated)
        self.assertIn("# Keep this comment", updated)
        self.assertEqual(values["instructions"], tomlkit.parse(original)["instructions"])
        self.assertEqual(values["profiles"]["custom"]["sandbox_mode"], "read-only")
        self.assertEqual(values["approval_policy"], "on-request")
        self.assertEqual(values["approvals_reviewer"], "auto_review")
        self.assertEqual(values["sandbox_mode"], "workspace-write")

    def test_failed_codex_validation_restores_the_original(self):
        path = self.write("codex/config.toml", 'model = "keep-me"\n')
        failure = subprocess.CalledProcessError(1, ["codex", "features", "list"])
        with patch.object(setup.shutil, "which", return_value="/usr/bin/codex"), patch.object(setup.subprocess, "run", side_effect=failure):
            with self.assertRaises(subprocess.CalledProcessError):
                setup.configure_codex_defaults()
        self.assertEqual(path.read_text(), 'model = "keep-me"\n')

    def test_neovim_preserves_existing_specs_and_skips_an_identical_override(self):
        original = 'return { { "other/plugin", opts = { custom = true } } }\n'
        path = self.write(".config/nvim/lua/plugins/neo-tree.lua", original)
        setup.configure_neo_tree()
        updated = path.read_text()
        setup.configure_neo_tree()
        self.assertEqual(path.read_text(), updated)
        self.assertIn(original, updated)
        self.assertIn('"nvim-neo-tree/neo-tree.nvim"', updated)
        self.assertEqual(len(list(path.parent.glob("neo-tree.lua.backup-*"))), 1)

    def test_display_override_preserves_other_rules_and_does_not_duplicate(self):
        path = self.home / ".config/hypr/monitors.lua"
        original = path.read_text()
        with patch.object(setup, "reload_hyprland"):
            setup.configure_displays()
            updated = path.read_text()
            setup.configure_displays()
        self.assertTrue(updated.startswith(original))
        self.assertEqual(path.read_text(), updated)
        self.assertIn("LS27DG30X H8CX700532", updated)
        self.assertNotIn("LU28R55", updated)
        self.assertNotIn("eDP-1", updated)
        self.assertEqual(len(list(path.parent.glob("monitors.lua.backup-*"))), 1)

    def test_hyprland_failure_restores_the_original_configuration(self):
        path = self.home / ".config/hypr/looknfeel.lua"
        original = path.read_text()
        with patch.object(setup, "reload_hyprland", side_effect=[None, RuntimeError("invalid config"), None]) as reload:
            with self.assertRaisesRegex(RuntimeError, "invalid config"):
                setup.configure_compact_layout()
        self.assertEqual(path.read_text(), original)
        self.assertEqual(reload.call_count, 3)

    def test_failed_dota_binding_removes_a_new_helper(self):
        with patch.object(setup, "configure_hyprland_override", side_effect=RuntimeError("invalid binding")):
            with self.assertRaisesRegex(RuntimeError, "invalid binding"):
                setup.configure_dota_close_guard()
        self.assertFalse((self.home / ".config/hypr/dota-close-guard.sh").exists())

    def test_clock_merge_preserves_clone_identity_position_and_other_settings(self):
        settings = self.shell_settings({"id": "desktop-test.clock", "format": "old", "custom": True})
        path = self.write(".config/omarchy/shell.json", json.dumps(settings))
        setup.configure_clock_format()
        updated = path.read_text()
        setup.configure_clock_format()
        result = json.loads(updated)
        self.assertEqual(path.read_text(), updated)
        self.assertEqual(result["idle"], settings["idle"])
        self.assertEqual(result["plugins"], settings["plugins"])
        self.assertEqual(result["bar"]["layout"]["right"], settings["bar"]["layout"]["right"])
        clock = result["bar"]["layout"]["center"][0]
        self.assertEqual(clock["id"], "desktop-test.clock")
        self.assertTrue(clock["custom"])
        self.assertEqual(clock["format"], "dd MMM ddd · 'W'ww · HH:mm")
        self.assertEqual(len(list(path.parent.glob("shell.json.backup-*"))), 1)

    def test_duplicate_clocks_are_reported_without_writing(self):
        settings = self.shell_settings()
        settings["bar"]["layout"]["center"].append({"id": "desktop-test.clock"})
        path = self.write(".config/omarchy/shell.json", json.dumps(settings))
        original = path.read_text()
        with self.assertRaisesRegex(RuntimeError, "Multiple entries"):
            setup.configure_clock_format()
        self.assertEqual(path.read_text(), original)

    def test_agents_step_does_not_change_the_configuration(self):
        path = self.write(".config/omarchy/shell.json", json.dumps(self.shell_settings()))
        original = path.read_text()
        with patch.object(setup, "omarchy_output", return_value="4.5.0-3"), patch.object(setup.subprocess, "run") as run:
            setup.report_agents_widget()
        run.assert_not_called()
        self.assertEqual(path.read_text(), original)

    def test_workspace_patch_is_repeatable_and_rejects_unknown_implementations(self):
        original = (REPOSITORY / "tests/fixtures/Workspaces.qml").read_text()
        updated = setup.workspace_button_source(original)
        self.assertEqual(setup.workspace_button_source(updated), updated)
        self.assertIn("var guests = []", updated)
        with self.assertRaisesRegex(RuntimeError, "implementation changed"):
            setup.workspace_button_source("unknown upstream widget")
        staged = self.write("staged/Workspaces.qml", updated)
        subprocess.run(
            ["node", str(REPOSITORY / "tests/workspace-buttons.test.cjs")],
            env=dict(os.environ, WIDGET_QML_PATH=str(staged)), check=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def test_workspace_clone_failure_restores_the_shell_and_removes_the_new_clone(self):
        original = (REPOSITORY / "tests/fixtures/Workspaces.qml").read_text()
        packaged = self.write("packaged/Workspaces.qml", original)
        manifest = self.write("packaged/manifest.json", json.dumps({"entryPoints": {"barWidget": "Workspaces.qml"}}))
        shell = self.write(".config/omarchy/shell.json", json.dumps(self.shell_settings()))
        shell_before = shell.read_text()
        catalog = [{"id": "omarchy.workspaces", "firstParty": True, "manifestPath": str(manifest), "barWidgetPath": str(packaged)}]
        clone = self.home / ".config/omarchy/plugins/desktop-test.workspaces"
        def simulate(command, **options):
            if command[0] == "node":
                return REAL_RUN(command, **options)
            if command[:3] == ["omarchy", "plugin", "clone"]:
                clone.mkdir(parents=True)
                (clone / "Workspaces.qml").write_text(original)
                shell.write_text('{"changed": true}')
            if command == ["omarchy", "restart", "shell"] and options.get("check"):
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        with patch.object(setup, "omarchy_output", return_value=json.dumps(catalog)), patch.object(setup.subprocess, "run", side_effect=simulate):
            with self.assertRaises(subprocess.CalledProcessError):
                setup.configure_workspace_buttons()
        self.assertEqual(shell.read_text(), shell_before)
        self.assertFalse(clone.exists())
        self.assertEqual(packaged.read_text(), original)

    def test_active_workspace_clone_is_skipped_without_restarting_the_shell(self):
        updated = setup.workspace_button_source((REPOSITORY / "tests/fixtures/Workspaces.qml").read_text())
        self.write(".config/omarchy/plugins/desktop-test.workspaces/Workspaces.qml", updated)
        self.write(".config/omarchy/plugins/desktop-test.workspaces/manifest.json", json.dumps({
            "id": "desktop-test.workspaces", "omarchy": {"clonedFrom": "omarchy.workspaces"},
            "entryPoints": {"barWidget": "Workspaces.qml"},
        }))
        settings = self.shell_settings()
        settings["bar"]["layout"]["left"].append({"id": "desktop-test.workspaces"})
        self.write(".config/omarchy/shell.json", json.dumps(settings))
        with patch.object(setup.subprocess, "run") as run:
            setup.configure_workspace_buttons()
        run.assert_not_called()

    def test_dota_guard_closes_only_when_process_lookup_reports_no_game(self):
        binary = self.home / "bin"
        binary.mkdir()
        lookup = binary / "pgrep"
        lookup.write_text('#!/bin/sh\nexit "$GUARD_STATUS"\n')
        lookup.chmod(0o755)
        dispatcher = binary / "hyprctl"
        dispatcher.write_text('#!/bin/sh\nprintf "%s\\n" "$*" > "$GUARD_LOG"\n')
        dispatcher.chmod(0o755)
        log = self.home / "guard.log"
        for status in (0, 1, 2):
            with self.subTest(status=status):
                log.unlink(missing_ok=True)
                result = subprocess.run(
                    ["/bin/bash", str(REPOSITORY / "scripts/dota-close-guard.sh")],
                    env=dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"], GUARD_STATUS=str(status), GUARD_LOG=str(log)),
                )
                self.assertEqual(result.returncode, 0 if status in (0, 1) else status)
                self.assertEqual(log.exists(), status == 1)
                if status == 1:
                    self.assertEqual(log.read_text().strip(), "dispatch hl.dsp.window.close()")

if __name__ == "__main__":
    unittest.main()
