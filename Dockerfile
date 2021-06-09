FROM rocker/r-ver:4.0.3

LABEL Maintainer="https://github.com/pacificclimate/chickadee" \
    Description="chickadee WPS" \
    Vendor="pacificclimate" \
    Version="0.6.0"

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.8 python3-pip libssl-dev libxml2-dev libudunits2-dev libnetcdf-dev libgit2-dev

ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib:$LD_LIBRARY_PATH
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"
ENV PATH=/root/.local/bin:$PATH

WORKDIR /tmp
COPY requirements.txt r_requirements.txt install_pkgs.R ./

RUN Rscript install_pkgs.R r_requirements.txt && \
    pip3 install -U pip && \
    pip3 install --user -r requirements.txt --ignore-installed && \
    pip3 install --user gunicorn

COPY . /tmp

EXPOSE 5000
CMD gunicorn --bind=0.0.0.0:5000 --timeout 300 chickadee.wsgi:application
