## Weather icons

Taken from <https://dribbble.com/shots/4276406-OpenWeatherMap-iconset>

[`convert_svg2png.R`](convert_svg2png.R) replaces spaces in the file
names with `_` and converts the SVG files to PNG files, using
[ImageMagick](https://imagemagick.org).

- might also need to replace the yellow with white or black

[`icon_codes.json`](icon_codes.json) has `icon_list` which converts
image codes to descriptions (which are the file names)
and `weather_conditions` which converts the 3-digit weather condition
ID to the icon ID.

### Other sources of icons

- <https://www.iconsdb.com/black-icons/black-weather-icons.html>

- or maybe do this by hand, and try <https://cloudconvert.com/svg-to-bmp>
