#!/usr/bin/Rscript

idir <- "BMP"
odir <- "BMPfull"

if(!dir.exists(odir)) dir.create(odir)

files <- list.files(idir)

system("convert BMP/Sunrise.bmp -resize 25x25 tmp4.bmp")
system("convert BMP/Sunset.bmp -resize 25x25 tmp5.bmp")

for(file in files) {
   if(!grepl("^DAY", file) && !grepl("^NIGHT", file)) next

   cat(file, "\n")
   system(paste("convert ", file.path(idir, file), "-resize 50x50 tmp1.bmp"))
   system("convert tmp1.bmp -background white -gravity northeast -splice 375x0 tmp2.bmp")
   system("convert tmp2.bmp -background white -gravity southwest -splice 375x430 tmp3.bmp")

   system("convert tmp3.bmp tmp4.bmp -gravity northwest -geometry 25x25+320+40 -composite tmp6.bmp")
   system(paste("convert tmp6.bmp tmp5.bmp -gravity northwest -geometry 25x25+410+40 -composite tmp7.bmp"))
   system(paste0("convert tmp7.bmp -dither FloydSteinberg -define dither:diffusion-amount=85% -remap eink_png/epaper_eink-2color.png BMP3:", file.path(odir, file)))
}

unlink("tmp*.bmp")
