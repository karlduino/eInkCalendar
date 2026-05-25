#!/usr/bin/Rscript

idir <- "BMP"
odir <- "BMPsmall"

if(!dir.exists(odir)) dir.create(odir)

files <- list.files(idir)
for(file in files) {
    system(paste("convert -resize 100x100", file.path(idir, file), file.path(odir, file)))
}
