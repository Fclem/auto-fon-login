FROM hypriot/rpi-python

RUN apt-get update

RUN apt-get install -y \
    git \
    --no-install-recommends

RUN rm -rf /var/lib/apt/lists/*

CMD ["bash"]