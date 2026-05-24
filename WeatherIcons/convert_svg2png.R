#!/usr/bin/Rscript

# replace spaces with _
files <- list.files("SVG")
for(file in files) {
    if(grepl("\\s+", file)) # if white space, replace with _
        system(paste0('replace_spaces.rb "', file.path("SVG", file), '"'))
}

# if PNG directory doesn't exist, create
png_dir <- "PNG"
if(!dir.exists(png_dir)) dir.create(png_dir)

# convert SVG -> PNG
files <- list.files("SVG")
for(file in files) {
    ifile <- file.path("SVG", file)
    ofile <- file.path("PNG", sub("\\.svg$", ".png", file))
    system(paste('convert', ifile, ofile))
}
