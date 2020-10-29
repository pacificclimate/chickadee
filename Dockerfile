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
      python3-dev && \
    pip3 install -r requirements.txt --ignore-installed && \
    pip3 install gunicorn

COPY . .

EXPOSE 5004

CMD ["gunicorn", "--bind=0.0.0.0:5004", "chickadee.wsgi:application"]

# docker build -t pacificclimate/chickadee .
# docker run -p 8102:5004 pacificclimate/chickadee
# http://localhost:5004/wps?request=GetCapabilities&service=WPS
# http://localhost:5004/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
