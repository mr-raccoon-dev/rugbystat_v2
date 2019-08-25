#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

FROM python:3.6-slim-buster

# Copy default endpoint specific user settings overrides into container to specify Python path
COPY .devcontainer/settings.vscode.json /root/.vscode-remote/data/Machine/settings.json

# Tell python not to produce any `__pycache__` and `*.pyc` files
ENV PYTHONBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 INSIDE_DOCKER=1

# Install git, process tools
RUN apt update && apt -y install \
    git \
    gcc \
    make \
    procps \
    default-libmysqlclient-dev \
    && apt autoremove -y \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /workspace
WORKDIR /workspace

# Install pylint
RUN pip install pylint

# Install Python dependencies from requirements.txt if it exists
COPY .devcontainer/requirements.txt.temp requirements.txt* /workspace/
COPY requirements/ /workspace/requirements/

# RUN if [ -f "requirements.txt" ]; then pip install -r requirements.txt && rm requirements.txt*; fi
RUN pip install -r /workspace/requirements/local.txt

# Copy the entrypoint.sh and start.sh and make them executable
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

# All subsequent commands will be run from the /workspace folder
WORKDIR /workspace

ENTRYPOINT ["/entrypoint.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]
