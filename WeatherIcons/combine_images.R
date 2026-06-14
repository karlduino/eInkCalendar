#!/usr/bin/Rscript

idir <- "BMP"
odir <- "BMPfull"

if(!dir.exists(odir)) dir.create(odir)

files <- list.files(idir)

system("convert BMP/Sunrise.bmp -resize 32x32 tmp4.bmp")
system("convert BMP/Sunset.bmp -resize 32x32 tmp5.bmp")

for(file in files) {
   if(!grepl("^DAY", file) && !grepl("^NIGHT", file)) next

   cat(file, "\n")

   # reside image for today's weather
   system(paste("convert ", file.path(idir, file), "-resize 56x56 tmp1.bmp"))

   # fill out to 800x480
   system("convert tmp1.bmp -background white -gravity northeast -splice 472x0 tmp2.bmp")
   system("convert tmp2.bmp -background white -gravity southwest -splice 272x424 tmp3.bmp")

   # merge in sunrise/sunset icons
   system("convert tmp3.bmp tmp4.bmp -gravity northwest -geometry 25x25+210+48 -composite tmp6.bmp")
   system(paste("convert tmp6.bmp tmp5.bmp -gravity northwest -geometry 25x25+330+48 -composite tmp7.bmp"))

   # convert colorscale
   system(paste0("convert tmp7.bmp -dither FloydSteinberg -define dither:diffusion-amount=85% -remap eink_png/epaper_eink-2color.png BMP3:", file.path(odir, file)))
}

unlink("tmp*.bmp")
