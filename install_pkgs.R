# Create user library and install devtools package
dir.create(Sys.getenv('R_LIBS_USER'), recursive = TRUE);
.libPaths(Sys.getenv('R_LIBS_USER'));

# Install devtools and its dependencies
install.packages('usethis');
install.packages('covr');
install.packages('httr');
install.packages('rversions');
install.packages('devtools');

# Install packages from requirements list
requirements_file <- file("r_requirements.txt",open="r")
data <-readLines(requirements_file)
for (i in 1:length(data)){
    pkg_ver_pair <- unlist(stringr::str_split(data[i], "=="))
    pkg<-pkg_ver_pair[1]
    ver<-pkg_ver_pair[2]
    if (is.na(ver)){
        devtools::install_version(pkg)
    } else {
        devtools::install_version(pkg, version = ver);
    }
}
close(requirements_file)
