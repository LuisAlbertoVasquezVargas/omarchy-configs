<!-- AGENTS.md -->

# Setup responsibilities

Follow the sibling `../swe-standards` repository. Read its `README.md` and
`standards/python.md` before changing Python. Use `.venv` and maintain the root
`requirements.txt`.

This emergency branch targets Omarchy 4.0.6 (Quattro) on the AMD/NVIDIA desktop
described in README.md. It is based on `main`; keep the 4.5 setup on `main`.
Use the same workflow as `../omarchy-configs-laptop`:
a root `setup.py`, no command-line arguments, named steps in README order, and
short messages when an installed component or matching setting is skipped.
Keep implementation/review separate from applying setup to the live desktop.

Implement the requested configurations, preserving unrelated settings. Back up
changed destinations, validate syntax before writing, and restore the affected
files when validation fails. Report failed checks. Do not claim live 4.0.6
validation based on mocks, source inspection, or another installed version.
Check compatibility against the official `v4.0.6` source, not current defaults.
Do not run system updates, package database refreshes, or upgrade/migration
helpers. Missing application packages may be installed with the 4.0.6 native
helpers, which use `--needed` without a full upgrade. Setup configures an
existing 4.0.6 desktop; it does not downgrade a 4.5 installation.

Use Omarchy 4.0.6's native global workspaces 1-10 and preserve its shortcuts,
numbering, monitor movement, and workspace layout modes. A user-owned widget
clone may show all ten buttons, including empty workspaces. Do not install
4.5's per-monitor workspace implementation or restore retired persistent
monitor-assignment rules or Steam/chat routing from the old 4.0 setup.

Agents setup installs the weekly-percentage/countdown display patch adapted
to 4.0.6's `LimitRow` in a user-owned clone, preserving unrelated clone edits
and provider settings. Do not use 4.5's `CompactLimit` or I18n APIs.
Skip a matching active clone; validate staged QML syntax before writing,
back up changes outside the plugin tree, and roll back failed installations.
Keep validation focused on syntax and runtime installation/configuration checks.
Do not add unit-test suites unless requested.
Keep Omarchy's native usage collector. Old quota-collector, Steam geometry,
and chat-placement implementations remain in Git history at commit `563f023`;
review and validate them before reintroducing them. The README's Ideas section
records future preferences without enabling them. Do not restore a full
`.config` snapshot or the retired installer.

Application sign-ins, synchronization, and visual/hardware checks remain manual.
Battery, touchpad, and laptop display settings do not belong in this desktop
setup. GPU updates, USB flashing, and reboots require their own user request.
