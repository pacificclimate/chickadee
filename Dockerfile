# vim:set ft=dockerfile:
FROM continuumio/miniconda3
MAINTAINER https://github.com/nikola-rados/chickadee
LABEL Description="chickadee WPS" Vendor="Birdhouse" Version="0.1.0"

# Update Debian system
RUN apt-get update && apt-get install -y \
 build-essential \
&& rm -rf /var/lib/apt/lists/*

# Update conda
RUN conda update -n base conda

# Copy WPS project
COPY . /opt/wps

WORKDIR /opt/wps

# Create conda environment with PyWPS
RUN ["conda", "env", "create", "-n", "wps", "-f", "environment.yml"]

# Install WPS
RUN ["/bin/bash", "-c", "source activate wps && pip install -e ."]

# Start WPS service on port 5004 on 0.0.0.0
EXPOSE 5004
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source activate wps && exec chickadee start -b 0.0.0.0 -c /opt/wps/etc/demo.cfg"]

# docker build -t nikola-rados/chickadee .
# docker run -p 5004:5004 nikola-rados/chickadee
# http://localhost:5004/wps?request=GetCapabilities&service=WPS
# http://localhost:5004/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
