FROM debian:7.5

RUN apt-get update ; apt-get install -y apt-utils
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get install -y python3

RUN apt-get install -y sudo
RUN useradd -m -d /xd -s /bin/bash xd
RUN echo xd ALL=NOPASSWD: ALL > /etc/sudoers.d/xd
CMD /bin/login -f xd

VOLUME /xd/task

