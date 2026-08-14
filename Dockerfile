FROM python:latest

# Install xvfb - a virtual X display server for the GUI to display to
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgirepository1.0-dev xvfb \
    python3-gi gobject-introspection gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1

COPY . /TwitchDropsMiner/
WORKDIR /TwitchDropsMiner/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x ./docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]

HEALTHCHECK --interval=10s --timeout=5s --start-period=5m --retries=3 CMD ./healthcheck.sh

CMD timeout $(( (60 - $(date +%-M)) * 60 - $(date +%-S) )) python main.py -vvvv

# Example command to build:
# docker build -t twitch_drops_miner .

# Suggested command to run:
# docker run -itd --init --pull=always --restart=always -v ./cookies.jar:/TwitchDropsMiner/cookies.jar -v ./settings.json:/TwitchDropsMiner/settings.json:ro -v /etc/localtime:/etc/localtime:ro --name twitch_drops_miner ghcr.io/valentin-metz/twitchdropsminer:master

# Suggested additional containers for monitoring:
# docker run -d --restart=always --name autoheal -e AUTOHEAL_CONTAINER_LABEL=all -v /var/run/docker.sock:/var/run/docker.sock -v /etc/localtime:/etc/localtime:ro willfarrell/autoheal
# docker run -d --restart=always --name watchtower -v ~/.docker/config.json:/config.json:ro -v /var/run/docker.sock:/var/run/docker.sock -v /etc/localtime:/etc/localtime:ro containrrr/watchtower --cleanup --include-restarting --include-stopped --interval 60
