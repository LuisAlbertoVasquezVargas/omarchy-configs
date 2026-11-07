<!-- AGENTS.md -->

# Setup responsibilities

Follow the sibling `../swe-standards` repository. Read its `README.md` and
`standards/python.md` before changing Python. Use `.venv` and maintain the root
`requirements.txt`.

This repository targets Omarchy 4.5.0 (Quattro RS) on the AMD/NVIDIA desktop
described in README.md. Use the same workflow as `../omarchy-configs-laptop`:
a root `setup.py`, no command-line arguments, named steps in README order, and
short messages when an installed component or matching setting is skipped.
Keep implementation/review separate from applying setup to the live desktop.

Implement the requested configurations, preserving unrelated settings. Back up
changed destinations, validate syntax before writing, and restore the affected
files when validation fails. Report failed checks. Do not claim a live 4.5
validation based on mocks, source inspection, or this machine's older install.

Use Omarchy 4.5's native ten workspaces per monitor and preserve its shortcuts,
numbering, monitor migration, and workspace layout modes. A user-owned widget
clone may show all ten buttons. Do not install the retired shared-workspace
rules or Steam/chat routing from the 4.0 setup.

Keep Agents setup report-only and preserve existing user-owned clones. Old
quota-collector, Steam geometry, and chat-placement workarounds are historical
reference in `docs/QUATTRO-4.0.md`; review and validate them before reintroducing
them. Do not restore a full `.config` snapshot or the retired installer.

Application sign-ins, synchronization, and visual/hardware checks remain manual.
Battery, touchpad, and laptop display settings do not belong in this desktop
setup. GPU updates, USB flashing, and reboots require their own user request.
