#!/bin/bash
R -e "install.packages('devtools');
require('devtools'); 
install_version('ClimDown', version = '1.0.2', repos = 'https://cran.r-project.org/')"

