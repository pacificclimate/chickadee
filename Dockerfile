FROM python:3.7-slim

MAINTAINER https://github.com/pacificclimate/chickadee
LABEL Description="chickadee WPS" Vendor="Birdhouse" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

WORKDIR /code

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y \
      build-essential \
      gcc \
      r-base \
      r-base-dev \
      libudunits2-dev \
      libnetcdf-dev \
      python3-dev && \
    pip3 install -r requirements.txt --ignore-installed && \
    pip3 install gunicorn
    chmod +x /install_R_packages.sh && /install_R_packages.sh

COPY . .

EXPOSE 5004

CMD gunicorn --bind=0.0.0.0:5004 --timeout 90 chickadee.wsgi:application

# docker build -t pacificclimate/chickadee .
# docker run -p 8102:5004 pacificclimate/chickadee
# http://localhost:5004/wps?request=GetCapabilities&service=WPS
# http://localhost:5004/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
