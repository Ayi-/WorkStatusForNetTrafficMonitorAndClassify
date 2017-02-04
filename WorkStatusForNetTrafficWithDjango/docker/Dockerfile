FROM daocloud.io/ubuntu:14.04

MAINTAINER Eli ae_lion@163.com

EXPOSE 8081
RUN ln -snf /bin/bash /bin/sh
# 替换apt源
#ADD https://raw.githubusercontent.com/Ayi-/docker-ubuntu-14.04/master/sources.list /etc/apt/sources.list
RUN sed -i 's/archive.ubuntu/mirrors.aliyun/g' /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y wget \
    curl \
    git \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    libmysqlclient-dev \
    python-dev \
    rabbitmq-server
# 创建用户

RUN \
    adduser aiiyi --gecos "" --disabled-password && \
    echo "aiiyi:000000" | sudo chpasswd && \
    echo "root:000000" | sudo chpasswd && \
    
    # 创建nginx用户
    groupadd nginx  && \ 
    useradd -g nginx -s /sbin/nologin nginx  && \
    # 创建nginx日志目录
    mkdir -p /var/nginx/log

# 切换用户
USER aiiyi

# 切换工作目录
WORKDIR /home/aiiyi

# 设置环境变量
ENV HOME /home/aiiyi
#ENV PYENV_ROOT $HOME/.pyenv
#ENV PATH $PYENV_ROOT/bin:$PATH

RUN \
    # 安装Pyenv
    mkdir /home/aiiyi/.pyenv && \
    curl -L https://api.github.com/repos/yyuu/pyenv/tarball | tar xz --strip=1 -C /home/aiiyi/.pyenv && \

    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /home/aiiyi/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /home/aiiyi/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> /home/aiiyi/.bashrc && \
    export PYENV_ROOT="$HOME/.pyenv" && \
    export PATH="$PYENV_ROOT/bin:$PATH" && \
    eval "$(pyenv init -)" && \

    # 安装pyenv-virtualenv
    mkdir /home/aiiyi/.pyenv/plugins/pyenv-virtualenv && \
    curl -L https://api.github.com/repos/yyuu/pyenv-virtualenv/tarball | tar xz --strip=1 -C /home/aiiyi/.pyenv/plugins/pyenv-virtualenv && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /home/aiiyi/.bashrc && \
    eval "$(pyenv virtualenv-init -)" && \
    echo $PYENV_ROOT && \

    # 安装python 2.7.12
    wget http://mirrors.sohu.com/python/2.7.12/Python-2.7.12.tar.xz -P /home/aiiyi/.pyenv/cache/ && \
    pyenv install 2.7.12  && \
    pyenv rehash  && \

    # 创建virtualenv
    pyenv virtualenv 2.7.12 wsfnt  && \

    # 修改pip源
    mkdir ~/.pip && \
    echo "[global]" > ~/.pip/pip.conf  &&\
    echo "trusted-host = mirrors.aliyun.com" >> ~/.pip/pip.conf  && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple/" >> ~/.pip/pip.conf
   
    # 安装nginx 1.10.2
    # curl -L http://nginx.org/download/nginx-1.10.2.tar.gz | tar xz --strip=1