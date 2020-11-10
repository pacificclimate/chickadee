#!/bin/bash
R -e "
dir.create(Sys.getenv('R_LIBS_USER'), recursive = TRUE);
.libPaths(Sys.getenv('R_LIBS_USER'));
install.packages('PCICt');
install.packages('udunits2');
install.packages('ncdf4');
install.packages('fields');
install.packages('foreach');
install.packages('seas');
install.packages('abind');
install.packages('https://cloud.r-project.org/src/contrib/ClimDown_1.0.2.tar.gz', dependencies=c('PCICt', 'udunits2', 'ncdf4', 'fields', 'foreach', 'seas', 'abind'))
"

