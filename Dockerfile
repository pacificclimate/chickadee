# vim:set ft=dockerfile:
FROM r-base:4.0.3
MAINTAINER https://github.com/pacificclimate/chickadee
LABEL Description="chickadee WPS" Vendor="pacificclimate" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

# Update system
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    python3.8 \
    python3-pip \
    python3-setuptools \
    python3-dev \
    python3-venv \
    libssl-dev \
    libxml2-dev \
    libudunits2-dev \
    libnetcdf-dev

COPY . /opt/wps

WORKDIR /opt/wps

# Create python environment
RUN ["python3", "-m", "venv", "venv"]

# Install WPS
RUN ["sh", "-c", "bash venv/bin/activate && pip3 install -e . && Rscript install_pkgs.R r_requirements.txt"]

EXPOSE 5004
ENTRYPOINT ["sh", "-c"]
CMD ["bash venv/bin/activate && exec chickadee start -b 0.0.0.0"]

# docker build -t pcic/chickadee .
# docker run -p 8102:5004 pcic/chickadee
# http://localhost:5004/wps?request=GetCapabilities&service=WPS
# http://localhost:5004/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
