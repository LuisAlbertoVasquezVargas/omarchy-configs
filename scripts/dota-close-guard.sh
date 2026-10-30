#!/bin/sh
# Super+W must not close any window while this user's native Dota 2 is running.
pgrep -u "$(id -u)" -x dota2 >/dev/null
status=$?
case "$status" in
  0) exit 0 ;;
  1) exec hyprctl dispatch 'hl.dsp.window.close()' ;;
  *) exit "$status" ;;
esac
