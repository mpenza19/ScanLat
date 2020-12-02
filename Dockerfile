# set base image
FROM python:3.8

# set container working directory
WORKDIR /opt

# get the dependencies file
COPY requirements.txt .

# install pip dependencies
RUN pip install -r requirements.txt

# download other dependencies (SFST)
RUN curl -O https://www.cis.uni-muenchen.de/~schmid/tools/SFST/data/SFST-1.4.7d.tar.gz \
  && tar -xzf SFST-1.4.7d.tar.gz \
  && cd SFST/src \
  && make \
  && make install

# alternate SFST download instructions
# RUN apt-get update \
#   && apt-get install -y sfst

# get dependency files
COPY dependencies/ dependencies/

# get input files
COPY input/ input/

# get application code
COPY src/ src/

# get/set env vars
ARG input_file
ENV INPUT_FILE="${input_file}"
ARG macronized_input
ENV MACRONIZED_INPUT="${is_macronized_input}"
ENV LATMOR_DIR="/opt/dependencies/LatMor/"
ENV UD_MODEL_PATH="/opt/dependencies/UDPipe-ud2/latin-proiel.udpipe"

# run code upon container start
CMD ["bash", "src/scanlat.sh"]
