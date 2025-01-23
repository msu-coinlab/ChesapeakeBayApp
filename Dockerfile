# Build: docker build -f Dockerfile -t api4opt-sa .
# Run: docker run -it --name api4opt-sa-1 -p 8000:8000 api4opt-sa
# Exec: docker exec -it api4opt-sa-1 bash

# Build with variables(does not work yet): docker build $(sed 's/^/ --build-arg /g' variables_standalone.env | xargs) -t api4opt-sa .
# Run with variables: docker run --env-file=variables_standalone.env -it --name api4opt-sa-1 -p 8000:8000 api4opt-sa
# Run with file in image (COPY variables_standalone.env /root/variables.env): add this line in entrypoint.sh export $(cat variables.env | xargs)


FROM python:3.10-bullseye
LABEL AUTHOR "Gregorio Toscano <gtoscano@fastmail.com>"

# Environment Vars
ENV PYTHONUNBUFFERED=1
ENV MSU_CBPO_PATH=/opt/opt4cast
ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_REGION=us-east-1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONIOENCODING=utf8
ENV LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"
ENV LC_CTYPE="en_US.UTF-8"
ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/lib
ENV LD_RUN_PATH=/usr/local/lib:/usr/lib
ENV AMQP_USERNAME=guest
ENV AMQP_PASSWORD=guest
ENV SQL_DATABASE=mydb
ENV SQL_USER=myuser
ENV SQL_PASSWORD=32ghukj45ihhkj3425
ENV SQL_PORT=3306


RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN apt-get update && apt-get upgrade -y
RUN apt-get -y install apt-utils locales-all locales wget
RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir -p /app \
    /app_src /app_src/github /app_src/data /app_src/ipopt \
    /app_src/CastEvaluation /app_src/alfred/ /app_src/MSUCast/ /app_src/run_base/ \
    /app_src/aws-sdk-cpp /app_src/redis-plus-plus /app_src/SimpleAmqpClient /app_src/crossguid \
    /opt/opt4cast/output/parquet /opt/opt4cast/data /opt/opt4cast/output/nsga3



WORKDIR /app/
COPY . ./

WORKDIR /app_src/data/
RUN wget -O apache-arrow-apt-source-latest-bullseye.deb https://apache.jfrog.io/artifactory/arrow/debian/apache-arrow-apt-source-latest-bullseye.deb
RUN dpkg -i apache-arrow-apt-source-latest-bullseye.deb
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y gcc g++ gfortran cmake git patch pkg-config liblapack-dev \
    libmetis-dev gawk build-essential cmake ninja-build bazel-bootstrap  \
    rabbitmq-server librabbitmq-dev libboost-all-dev libboost-log-dev libfmt-dev \
    nlohmann-json3-dev libhiredis0.14 libhiredis-dev libcurl4-openssl-dev libssl-dev \
    uuid-dev zlib1g-dev libpulse-dev ca-certificates lsb-release protobuf-c-compiler \
    libprotobuf-dev libprotobuf-lite23 libprotobuf-c-dev libsnappy-dev zip unzip \
    sudo awscli libarrow-dev libarrow-glib-dev libarrow-dataset-dev \
    libarrow-dataset-glib-dev libparquet-dev libparquet-glib-dev python3-dev \
    python3-pip python-is-python3 python3-geopandas  python3-psycopg2 systemctl \
    libcjson1 libcjson-dev redis software-properties-common apt-transport-https \
    gnupg2 libcurlpp0 libcurlpp-dev libc-ares-dev libc-ares2 librange-v3-dev

RUN pip install scikit-learn numpy uuid sqlalchemy pyarrow redis


RUN chown -R www-data.www-data /opt/opt4cast/output



# Copy the application files into the image


## CSVs config options
COPY data/csvs.tar.gz /opt/opt4cast/
WORKDIR /opt/opt4cast/
RUN tar xvfz csvs.tar.gz


#/tmp/loki-cpp /tmp/curlpp /tmp/c-ares 

## Install dependencies


WORKDIR /app_src/github/
RUN git clone --recurse-submodules https://github.com/aws/aws-sdk-cpp && \
    git clone https://github.com/sewenew/redis-plus-plus.git && \
    git clone https://github.com/alanxz/SimpleAmqpClient.git && \
    git clone https://github.com/graeme-hill/crossguid

WORKDIR /app_src/aws-sdk-cpp 
RUN cmake /app_src/github/aws-sdk-cpp -DAUTORUN_UNIT_TESTS=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/usr/local/ -DBUILD_ONLY="s3" && \
    make clean && \
    make && \
    make install

WORKDIR /app_src/redis-plus-plus 
RUN cmake -DREDIS_PLUS_PLUS_CXX_STANDARD=17 /app_src/github/redis-plus-plus/ -DCMAKE_BUILD_TYPE=Release && \
    make clean && \
    make && \
    make install

WORKDIR /app_src/SimpleAmqpClient
RUN cmake /app_src/github/SimpleAmqpClient -DCMAKE_BUILD_TYPE=Release && \
    make clean && \
    make && \
    make install

WORKDIR /app_src/crossguid 
RUN cmake /app_src/github/crossguid -DCMAKE_BUILD_TYPE=Release && \
    make clean && \
    make && \
    make install



## Install COIN Operation Research Tools
WORKDIR /app_src/ipopt/
RUN git clone https://github.com/coin-or-tools/ThirdParty-ASL.git && \
    git clone https://github.com/coin-or-tools/ThirdParty-HSL.git && \
    git clone https://github.com/coin-or-tools/ThirdParty-Mumps.git && \
    git clone https://github.com/coin-or/Ipopt.git

COPY data/solvers.tar.gz /app_src/ipopt/ThirdParty-ASL/
WORKDIR /app_src/ipopt/ThirdParty-ASL
RUN tar xvfz solvers.tar.gz && \
    ./configure && \
    make clean && \
    make && \
    make install 

COPY data/coinhsl.tar.gz /app_src/ipopt/ThirdParty-HSL/
WORKDIR /app_src/ipopt/ThirdParty-HSL
RUN tar xvfz coinhsl.tar.gz && \
    ./configure && \
    make clean && \
    make && \
    make install 

WORKDIR /app_src/ipopt/ThirdParty-Mumps
RUN chmod +x get.Mumps && \
    ./get.Mumps && \
    ./configure && \
    make clean && \
    make && \
    make install 


WORKDIR /app_src/ipopt/Ipopt
RUN ./configure && \
    make clean && \
    make && \
    make install 

WORKDIR /app_src/github/
RUN git clone https://github.com/gtoscano/CastEvaluation.git && \
    git clone https://github.com/gtoscano/alfred_aio.git && \
    #git clone https://github.com/gtoscano/alfred.git && \
    git clone https://github.com/gtoscano/MSUCast.git && \
    git clone https://github.com/gtoscano/run_base


WORKDIR /app_src/CastEvaluation
RUN cmake /app_src/github/CastEvaluation && \
    make clean && \
    make && \
    make install 

WORKDIR /app_src/alfred
RUN cmake /app_src/github/alfred_aio && \
    make clean && \
    make && \
    make install


WORKDIR /app_src/MSUCast
RUN cmake /app_src/github/MSUCast && \
    make clean && \
    make && \
    make install

WORKDIR /app_src/run_base
RUN cmake /app_src/github/run_base && \
    make clean && \
    make && \
    make install



WORKDIR /app


# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# We use the --system flag so packages are installed into the system python
# and not into a virtualenv. Docker containers don't need virtual environments. 
RUN pipenv install --system --deploy


# Expose port 8000 on the container
EXPOSE 8000
#ENTRYPOINT [ "entrypoint.sh" ]



# Make the entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Optionally, you can keep the CMD if needed
# CMD ["gunicorn", "cast.wsgi:application", "--bind", "0.0.0.0:8000"]

# Set the entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

