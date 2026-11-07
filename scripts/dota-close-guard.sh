#!/usr/bin/env bash
# scripts/dota-close-guard.sh

pgrep -u "$(id -u)" -x dota2 >/dev/null
status=$?
case "$status" in
  0) exit 0 ;;
  1) exec hyprctl dispatch 'hl.dsp.window.close()' ;;
  *) exit "$status" ;;
esac
