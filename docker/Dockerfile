FROM debian:jessie

RUN apt-get update ; apt-get install -y apt-utils
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get install -y python3

RUN apt-get install -y sudo
RUN useradd -m -d /xd -s /bin/bash xd
RUN echo xd ALL=NOPASSWD: ALL > /etc/sudoers.d/xd
CMD /bin/login -f xd

VOLUME /xd/task

RUN apt-get install -y python3-sh vim tree
RUN apt-get install -y build-essential
