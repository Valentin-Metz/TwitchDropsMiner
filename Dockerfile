FROM python:3.10-bullseye

# Install xvfb - a virtual X display server for the GUI to display to
RUN apt-get update && apt-get upgrade -y
RUN apt-get install libgirepository1.0-dev xvfb -y

COPY . /TwitchDropsMiner/
WORKDIR /TwitchDropsMiner/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x ./docker_entrypoint.sh
ENTRYPOINT ["./docker_entrypoint.sh"]

HEALTHCHECK --interval=10s --timeout=5s --start-period=1m --retries=3 CMD ./healthcheck.sh

ENV UNLINKED_CAMPAIGNS=1
ENV PRIORITY_BY_ENDING_SOONEST=0
CMD ["python", "main.py", "-vvv"]

# Example command to build:
# docker build -t twitch_drops_miner .

# Suggested command to run:
# docker run -itd --init --pull=always --restart=always -v ./cookies.jar:/TwitchDropsMiner/cookies.jar -v ./settings.json:/TwitchDropsMiner/settings.json:ro --name twitch_drops_miner ghcr.io/valentin-metz/twitchdropsminer:master

# Suggested additional containers for monitoring:
# docker run -d --restart=always --name autoheal -e AUTOHEAL_CONTAINER_LABEL=all -v /var/run/docker.sock:/var/run/docker.sock willfarrell/autoheal
# docker run -d --restart=always --name watchtower -v /var/run/docker.sock:/var/run/docker.sock -v /etc/localtime:/etc/localtime:ro -v ~/.docker/config.json:/config.json:ro containrrr/watchtower --cleanup --include-restarting --include-stopped --interval 60
