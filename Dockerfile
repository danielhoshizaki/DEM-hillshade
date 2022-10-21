FROM  ubuntu:20.04

# Install GDAL and Python
RUN \
  apt -y update --fix-missing && \
  apt -y install software-properties-common && \
  apt -y update && \
  apt -y upgrade && \
  apt -y install gfortran \
                 gdal-bin \
                 libhdf5-dev \
                 libgdal-dev \
                 python3-gdal \
                 python3-pip \
                 libsm6 \
                 libxext6 \
                 libxrender-dev && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install python dependencies
COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all files
COPY . /workspace

# Defualt run configuration
CMD ["python3", "-u", "src/hillshade.py"]