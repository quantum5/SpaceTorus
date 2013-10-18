@echo off
cd %~dp0assets\textures
gm convert earth.jpg -resize 1024x512 earth_small.jpg
gm convert moon.jpg -resize 512x256 moon_small.jpg
gm convert mars.jpg -resize 1024x512 mars_small.jpg
gm convert jupiter.jpg -resize 1024x512 jupiter_small.jpg
gm convert saturn.jpg -resize 1024x512 saturn_small.jpg
::gm convert uranus.jpg -resize 4x2 uranus_small.jpg
::gm convert neptune.jpg -resize 512x256 neptune_small.jpg
copy uranus.jpg uranus_small.jpg
copy neptune.jpg neptune_small.jpg
