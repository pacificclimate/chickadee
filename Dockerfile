FROM rocker/r-ver:4.0.3 AS builder

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY requirements.txt r_requirements.txt install_pkgs.R ./

# Install python and R packages
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    # Install pip
    python3-pip \
    # Install libraries for R packages installation
    libssl-dev \
    libxml2-dev \
    libudunits2-dev \
    libnetcdf-dev \
    libgit2-dev && \
    # Install R packages
    Rscript install_pkgs.R r_requirements.txt && \
    # Install python packages
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --ignore-installed --user && \
    # Install gunicorn
    pip3 install gunicorn --user

FROM rocker/r-ver:4.0.3 AS prod
MAINTAINER https://github.com/pacificclimate/chickadee
LABEL Description="chickadee WPS" Vendor="pacificclimate" Version="0.5.2"

# Install Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3.8 \
      python3-pip

# COPY Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy compiled library files
# Necessary files are found manually by running processes
COPY --from=builder /usr/lib/x86_64-linux-gnu/libnetcdf.so.15 \
  /usr/lib/x86_64-linux-gnu/libhdf5_serial_hl.so.100 \
  /usr/lib/x86_64-linux-gnu/libhdf5_serial.so.103 \
  /usr/lib/x86_64-linux-gnu/libcurl-gnutls.so.4 \
  /usr/lib/x86_64-linux-gnu/libsz.so.2 \
  /usr/lib/x86_64-linux-gnu/libaec.so.0 \
  /usr/lib/x86_64-linux-gnu/libudunits2.so.0 \
  /usr/lib/x86_64-linux-gnu/

# Copy R packages in r_requirements.txt and their dependencies
# Directories cannot be recursively copied
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/PCICt \
  /root/R/x86_64-pc-linux-gnu-library/4.0/PCICt
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/udunits2 \
  /root/R/x86_64-pc-linux-gnu-library/4.0/udunits2
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/ncdf4 \
  /root/R/x86_64-pc-linux-gnu-library/4.0/ncdf4
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/fields \
  /root/R/x86_64-pc-linux-gnu-library/4.0/fields
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/foreach \
  /root/R/x86_64-pc-linux-gnu-library/4.0/foreach
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/seas \
  /root/R/x86_64-pc-linux-gnu-library/4.0/seas
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/abind \
  /root/R/x86_64-pc-linux-gnu-library/4.0/abind
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/ClimDown \
  /root/R/x86_64-pc-linux-gnu-library/4.0/ClimDown
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/doParallel \
  /root/R/x86_64-pc-linux-gnu-library/4.0/doParallel
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/maps \
  /root/R/x86_64-pc-linux-gnu-library/4.0/maps
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/spam \
  /root/R/x86_64-pc-linux-gnu-library/4.0/spam
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/dotCall64 \
  /root/R/x86_64-pc-linux-gnu-library/4.0/dotCall64
COPY --from=builder /root/R/x86_64-pc-linux-gnu-library/4.0/iterators \
  /root/R/x86_64-pc-linux-gnu-library/4.0/iterators

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
# Add path to libR.so to the environment variable LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib:$LD_LIBRARY_PATH

WORKDIR /code

COPY ./chickadee /code/chickadee

EXPOSE 5000

CMD gunicorn --bind=0.0.0.0:5000 --timeout 300 chickadee.wsgi:application

# docker build -t pacificclimate/chickadee .
# docker run -p 8102:5000 pacificclimate/chickadee
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
