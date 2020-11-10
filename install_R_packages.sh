#!/bin/bash
R -e "
dir.create(Sys.getenv('R_LIBS_USER'), recursive = TRUE);
.libPaths(Sys.getenv('R_LIBS_USER'));
install.packages('devtools');
require('devtools', lib=); 
install_version('ClimDown', version = '1.0.2', repos = 'https://cran.r-project.org/')
"

