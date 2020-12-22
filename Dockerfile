FROM r-base:4.0.3

MAINTAINER https://github.com/pacificclimate/chickadee
LABEL Description="chickadee WPS" Vendor="Birdhouse" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

WORKDIR /code

COPY requirements.txt r_requirements.txt install_pkgs.R ./

# Install python and R packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libgit2-dev \
      libpq-dev \
      python3.8 \
      python3-pip \
      python3-setuptools \
      python3-dev \
      libssl-dev \
      libxml2-dev \
      libudunits2-dev \
      libnetcdf-dev && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --ignore-installed && \
    pip3 install gunicorn && \
    Rscript install_pkgs.R r_requirements.txt

COPY . .

EXPOSE 5000

CMD gunicorn --bind=0.0.0.0:5000 --timeout 300 chickadee.wsgi:application

# docker build -t pacificclimate/chickadee .
# docker run -p 8102:5000 pacificclimate/chickadee
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
