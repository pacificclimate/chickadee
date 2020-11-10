#!/bin/bash
R -e "
dir.create(Sys.getenv('R_LIBS_USER'), recursive = TRUE);
.libPaths(Sys.getenv('R_LIBS_USER'));
install.packages('https://cloud.r-project.org/src/contrib/ClimDown_1.0.2.tar.gz');
"

