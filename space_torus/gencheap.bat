@echo off
cd %~dp0assets\textures
gm convert earth.jpg -resize 2048x1024 earth_medium.jpg
gm convert earth.jpg -resize 1024x512 earth_small.jpg
gm convert moon.jpg -resize 512x256 moon_small.jpg
gm convert mars.jpg -resize 1024x512 mars_small.jpg
gm convert jupiter.jpg -resize 2048x1024 jupiter_medium.jpg
gm convert jupiter.jpg -resize 1024x512 jupiter_small.jpg
gm convert saturn.jpg -resize 2048x1024 saturn_medium.jpg
gm convert saturn.jpg -resize 1024x512 saturn_small.jpg
