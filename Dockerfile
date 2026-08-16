FROM python:latest

# Install xvfb - a virtual X display server for the GUI to display to
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libgirepository1.0-dev xvfb \
    python3-gi gobject-introspection gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1

COPY . /TwitchDropsMiner/
WORKDIR /TwitchDropsMiner/

ENV HEALTHCHECK_PATH=/TwitchDropsMiner/healthcheck.timestamp \
    HEALTHCHECK_MAX_AGE=120

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x ./docker_entrypoint.sh ./healthcheck.sh \
    && date +%s > "$HEALTHCHECK_PATH" \
    && ./healthcheck.sh \
    && rm -f "$HEALTHCHECK_PATH"
ENTRYPOINT ["./docker_entrypoint.sh"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5m --retries=3 CMD ./healthcheck.sh

CMD ["bash", "-c", "exec timeout --kill-after=30s \"$(( (60 - $(date +%-M)) * 60 - $(date +%-S) ))s\" python main.py -vvvv"]

# Example command to build:
# docker build -t twitch_drops_miner .

# Suggested command to run:
# docker run -itd --init --pull=always --restart=always --network=host --label autoheal=true --label autoheal.stop.timeout=30 -v ./cookies.jar:/TwitchDropsMiner/cookies.jar -v ./settings.json:/TwitchDropsMiner/settings.json:ro -v /etc/localtime:/etc/localtime:ro --name twitch_drops_miner ghcr.io/valentin-metz/twitchdropsminer:master

# Suggested additional containers for monitoring:
# docker run -d --restart=always --network=none --name autoheal -e AUTOHEAL_CONTAINER_LABEL=autoheal -e AUTOHEAL_INTERVAL=30 -v /var/run/docker.sock:/var/run/docker.sock -v /etc/localtime:/etc/localtime:ro willfarrell/autoheal:1.1.0
# docker run -d --restart=always --name watchtower -v ~/.docker/config.json:/config.json:ro -v /var/run/docker.sock:/var/run/docker.sock -v /etc/localtime:/etc/localtime:ro containrrr/watchtower --cleanup --include-restarting --include-stopped --interval 60
