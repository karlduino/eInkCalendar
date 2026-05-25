#!/usr/bin/Rscript

# replace spaces with _
files <- list.files("SVG")
for(file in files) {
    if(grepl("\\s+", file)) # if white space, replace with _
        system(paste0('replace_spaces.rb "', file.path("SVG", file), '"'))
}

# if BMP directory doesn't exist, create
bmp_dir <- "BMP"
if(!dir.exists(bmp_dir)) dir.create(bmp_dir)

# convert SVG -> BMP
files <- list.files("SVG")
for(file in files) {
    ifile <- file.path("SVG", file)
    ofile <- file.path("BMP", sub("\\.svg$", ".bmp", file))
    system(paste('convert', ifile, ofile))
}
