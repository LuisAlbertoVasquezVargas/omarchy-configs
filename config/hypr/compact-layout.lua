-- config/hypr/compact-layout.lua

do
  local palette = {}
  local user_directory = os.getenv("HOME")
  local palette_file = user_directory and io.open(user_directory .. "/.local/state/omarchy/current/theme/colors.toml", "r")

  if palette_file then
    for line in palette_file:lines() do
      local key, hex = line:match('^%s*([%w_]+)%s*=%s*"#(%x+)"')
      if key and (#hex == 6 or #hex == 8) then
        local format = #hex == 6 and "rgb" or "rgba"
        palette[key] = format .. "(" .. hex .. ")"
      end
    end
    palette_file:close()
  end

  local settings = {
    general = {
      gaps_in = 0,
      gaps_out = 0,
      border_size = 3,
    },
  }
  local active_border = palette.color6 or palette.accent
  local inactive_border = palette.background

  if active_border and inactive_border then
    settings.general.col = {
      active_border = active_border,
      inactive_border = inactive_border,
    }
    settings.group = {
      col = {
        border_active = active_border,
        border_inactive = inactive_border,
      },
    }
  end

  hl.config(settings)
end
