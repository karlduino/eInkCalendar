#!/usr/bin/Rscript

idir <- "BMP"
odir <- "BMPfull"

if(!dir.exists(odir)) dir.create(odir)

files <- list.files(idir)

system("convert BMP/Sunrise.bmp -resize 40x40 tmp4.bmp")
system("convert BMP/Sunset.bmp -resize 40x40 tmp5.bmp")

for(file in files) {
   if(!grepl("^DAY", file) && !grepl("^NIGHT", file)) next

   cat(file, "\n")
   system(paste("convert ", file.path(idir, file), "-resize 80x80 tmp1.bmp"))
   system("convert tmp1.bmp -background white -gravity northeast -splice 360x0 tmp2.bmp")
   system("convert tmp2.bmp -background white -gravity southwest -splice 360x400 tmp3.bmp")

   system("convert tmp3.bmp tmp4.bmp -gravity northwest -geometry 40x40+600+0 -composite tmp6.bmp")
   system(paste("convert tmp6.bmp tmp5.bmp -gravity northwest -geometry 40x40+600+30 -composite", file.path(odir, file)))
}

unlink("tmp*.bmp")
