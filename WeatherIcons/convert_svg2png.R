#!/usr/bin/Rscript

# replace spaces with _
files = list.files("SVG")
for(file in files) {
    if(grepl("\\s+", file)) # if white space, replace with _
        system(paste0('replace_spaces.rb "', file.path("SVG", file), '"'))
}

# convert SVG -> PNG
files = list.files("SVG")
for(file in files) {
    ifile = file.path("SVG", file)
    ofile = file.path("PNG", sub("\\.svg$", ".png", file))
    system(paste('convert', ifile, ofile))
}
