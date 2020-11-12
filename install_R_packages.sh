#!/bin/bash
R -e "
dir.create(Sys.getenv('R_LIBS_USER'), recursive = TRUE);
.libPaths(Sys.getenv('R_LIBS_USER'));
install.packages('usethis');
install.packages('covr');
install.packages('httr');
install.packages('rversions');
install.packages('devtools');
devtools::install_version('PCICt', version = '0.5.4.1');
devtools::install_version('udunits2', version = '0.13');
devtools::install_version('ncdf4', version = '1.17');
devtools::install_version('fields', version = '11.6');
devtools::install_version('foreach', version = '1.5.1');
devtools::install_version('seas', version = '0.5.2');
devtools::install_version('abind', version = '1.4.5');
devtools::install_version('ClimDown', version = '1.0.2')
"

