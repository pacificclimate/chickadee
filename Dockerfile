FROM rocker/r-ver:4.0.3 AS build

COPY r_requirements.txt install_pkgs.R ./

RUN apt-get update && \
  apt-get install -y --no-install-recommends libssl-dev libxml2-dev libudunits2-dev libnetcdf-dev libgit2-dev && \
  Rscript install_pkgs.R r_requirements.txt

FROM rocker/r-ver:4.0.3

LABEL Maintainer="https://github.com/pacificclimate/chickadee" \
  Description="chickadee WPS" \
  Vendor="pacificclimate" \
  Version="0.6.1"

WORKDIR /tmp

# Copy compiled library files
ARG LIB_FILEPATH=/usr/lib/x86_64-linux-gnu/

COPY --from=build ${LIB_FILEPATH}/libnetcdf.so.15 \
  ${LIB_FILEPATH}/libhdf5_serial_hl.so.100 \
  ${LIB_FILEPATH}/libhdf5_serial.so.103 \
  ${LIB_FILEPATH}/libcurl-gnutls.so.4 \
  ${LIB_FILEPATH}/libsz.so.2 \
  ${LIB_FILEPATH}/libaec.so.0 \
  ${LIB_FILEPATH}/libudunits2.so.0 \
  ${LIB_FILEPATH}/

# Copy R packages in r_requirements.txt and their dependencies
# Directories cannot be recursively copied
ARG R_FILEPATH=/root/R/x86_64-pc-linux-gnu-library/4.0

COPY --from=build ${R_FILEPATH}/PCICt ${R_FILEPATH}/PCICt
COPY --from=build ${R_FILEPATH}/udunits2 ${R_FILEPATH}/udunits2
COPY --from=build ${R_FILEPATH}/ncdf4 ${R_FILEPATH}/ncdf4
COPY --from=build ${R_FILEPATH}/fields ${R_FILEPATH}/fields
COPY --from=build ${R_FILEPATH}/foreach ${R_FILEPATH}/foreach
COPY --from=build ${R_FILEPATH}/seas ${R_FILEPATH}/seas
COPY --from=build ${R_FILEPATH}/abind ${R_FILEPATH}/abind
COPY --from=build ${R_FILEPATH}/ClimDown ${R_FILEPATH}/ClimDown
COPY --from=build ${R_FILEPATH}/doParallel ${R_FILEPATH}/doParallel
COPY --from=build ${R_FILEPATH}/maps ${R_FILEPATH}/maps
COPY --from=build ${R_FILEPATH}/spam ${R_FILEPATH}/spam
COPY --from=build ${R_FILEPATH}/dotCall64 ${R_FILEPATH}/dotCall64
COPY --from=build ${R_FILEPATH}/iterators ${R_FILEPATH}/iterators

# Add path to libR.so to the environment variable LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib:$LD_LIBRARY_PATH
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY . /tmp
COPY requirements.txt ./

RUN apt-get update && \
  apt-get install -y --no-install-recommends python3.9 python3-pip sqlite3 git && \
  # Use Python 3.9 explicitly
  update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 && \
  update-alternatives --set python3 /usr/bin/python3.9 && \
  # Update pip for Python 3.9
  python3.9 -m pip install -U pip && \
  python3.9 -m pip install -r requirements.txt && \
  python3.9 -m pip install gunicorn

EXPOSE 5000
CMD gunicorn --bind=0.0.0.0:5000 --timeout 0 chickadee.wsgi:application
