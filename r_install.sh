#!/bin/bash

# Create user library and install devtools package
R -e "
dir.create(Sys.getenv('R_LIBS_USER'), recursive = TRUE);
.libPaths(Sys.getenv('R_LIBS_USER'));
install.packages('usethis');
install.packages('covr');
install.packages('httr');
install.packages('rversions');
install.packages('devtools');
"

# Install packages from requirements list
cat r_requirements.txt | while read line || [[ -n $line ]]; do
    IFS='=='
    read -ra pkg_ver_pair <<< "$line"
    R -e "
    .libPaths(Sys.getenv('R_LIBS_USER'));
    devtools::install_version('${pkg_ver_pair[0]}', version = '${pkg_ver_pair[2]}');
    "
done
