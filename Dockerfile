FROM rocker/r-ver:4.4 AS build

COPY pyproject.toml install_pkgs.R ./

RUN apt-get update && \
  apt-get install -y --no-install-recommends libssl-dev libxml2-dev libudunits2-dev libnetcdf-dev libgit2-dev && \
  Rscript install_pkgs.R

FROM rocker/r-ver:4.4

LABEL Maintainer="https://github.com/pacificclimate/chickadee" \
  Description="chickadee WPS" \
  Vendor="pacificclimate" \
  Version="0.6.1"

WORKDIR /tmp

# Copy compiled library files
ARG LIB_FILEPATH=/usr/lib/x86_64-linux-gnu/

# Copy R packages
# Directories cannot be recursively copied
ARG R_FILEPATH=/root/R/x86_64-pc-linux-gnu-library/4.4

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
ENV LD_LIBRARY_PATH=/usr/local/lib/R/lib
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY . /tmp
COPY pyproject.toml poetry.lock* ./

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && \
  apt-get install -y --no-install-recommends python3 python3-pip curl sqlite3 git && \
  curl -sSL https://install.python-poetry.org | python3

RUN poetry config virtualenvs.in-project true && \
  poetry lock && \
  poetry install

EXPOSE 5000
CMD ["poetry", "run", "gunicorn", "--bind=0.0.0.0:5000", "--timeout", "0", "chickadee.wsgi:application"]

