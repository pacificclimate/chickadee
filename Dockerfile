FROM rocker/r-ver:4.4

LABEL Maintainer="https://github.com/pacificclimate/chickadee" \
  Description="chickadee WPS" \
  Vendor="pacificclimate" \
  Version="0.6.1"

WORKDIR /tmp

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  libssl-dev \
  libxml2-dev \
  libudunits2-dev \
  libnetcdf-dev \
  libhdf5-serial-dev \
  libcurl4-gnutls-dev \
  libaec-dev \
  libgit2-dev \
  python3 \
  python3-pip \
  curl \
  sqlite3 \
  git

COPY pyproject.toml poetry.lock* install_pkgs.R ./
RUN Rscript install_pkgs.R

# Add path to libR.so to LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib:$LD_LIBRARY_PATH
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY . /tmp

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 && \
  poetry config virtualenvs.in-project true && \
  poetry install

EXPOSE 5000
CMD ["poetry", "run", "gunicorn", "--bind=0.0.0.0:5000", "--timeout", "0", "chickadee.wsgi:application"]