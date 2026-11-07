-- config/hypr/dota-close-binding.lua

do
  hl.unbind("SUPER + W")
  o.bind("SUPER + W", "Close window (disabled while Dota 2 runs)",
    '"' .. os.getenv("HOME") .. '/.config/hypr/dota-close-guard.sh"')
end
