# COTO (Contributor of The Organization) Bot

[![Lint](https://github.com/HackSquadDev/contributor-of-the-xxx-python/actions/workflows/linting.yml/badge.svg)](https://github.com/HackSquadDev/contributor-of-the-xxx-python/actions/workflows/linting.yml)

## Setup

### Environment Variables

Before running the steps mentioned below, make sure you set the required secrets using the following command:

```bash
# use the example file to create local environment file
$ cp .env.example .env

# fill up the values using your favorite editor
$ nano .env
```

### Initialize

- Manual: (requires **Python 3.10** or later)

```bash
# setting up virtual environment using venv
$ python -m venv ven
$ source venv/bin/activate

# install dependencies using pip
$ pip install -r requirements.txt

# run the bot
$ python main.py
```

- Docker: (easier, requires [Docker Engine](https://docker.com/) and [Docker Compose](https://docs.docker.com/compose/))

```bash
# building the image
$ docker-compose build

# running it
$ docker-compose up
```
