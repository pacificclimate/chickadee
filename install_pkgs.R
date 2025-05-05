# Create user library
dir.create(Sys.getenv("R_LIBS_USER"), recursive = TRUE)
.libPaths(Sys.getenv("R_LIBS_USER"))

# Install and load RcppTOML
if (!requireNamespace("RcppTOML", quietly = TRUE)) {
  install.packages("RcppTOML", repos = "https://cloud.r-project.org")
}
library(RcppTOML)

# Read the TOML file
toml_data <- RcppTOML::parseTOML("pyproject.toml")

# Extract dependencies
deps <- toml_data$tool$chickadee$`r-dependencies`


# Install devtools
install.packages("devtools", dependencies = TRUE)
library(devtools)

# Install packages with versions
for (pkg in names(deps)) {
    ver <- deps[[pkg]]
    if (!(pkg %in% rownames(installed.packages()))) {
        if (is.null(ver) || ver == "*" || ver == "") {
            install_version(pkg)
        } else {
            install_version(pkg, version = ver)
        }
    }
    
}

install.packages("githubinstall")
library(githubinstall)
gh_install_packages("pacificclimate/ClimDown", ref = "ci-climatex")


