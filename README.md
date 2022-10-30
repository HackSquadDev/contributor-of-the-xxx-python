# COTO (Contributor of The Organization) Bot

[![Lint](https://github.com/HackSquadDev/contributor-of-the-xxx-python/actions/workflows/linting.yml/badge.svg)](https://github.com/HackSquadDev/contributor-of-the-xxx-python/actions/workflows/linting.yml)
[![Format](https://github.com/HackSquadDev/contributor-of-the-xxx-python/actions/workflows/formatting.yml/badge.svg)](https://github.com/HackSquadDev/contributor-of-the-xxx-python/actions/workflows/formatting.yml)

## Why?

As a part of [HackSquad 2022](https://hacksquad.dev/), a competition took place where you'd have to create an autonomous "being of the Internet" (or "bot" to be precise) which takes the top contributor of a GitHub Organization within a given period and congratulates them for their contributions in both Discord and Twitter. \

Speaking of that, This project has been made by one of the teams which joined forces in that competition. Feel free to have a look around! <br>

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

You can setup the project with ease in two different ways. They are:

- Docker: (easier, requires [Docker Engine](https://docker.com/) and [Docker Compose](https://docs.docker.com/compose/))

```bash
# building the image
$ docker-compose build

# running it
$ docker-compose up
```

- Manual: (requires **Python 3.10** or later)

```bash
# setting up virtual environment using venv
$ python -m venv venv
$ source venv/bin/activate

# install dependencies using pip
$ pip install -r requirements.txt

# run the bot
$ python main.py
```

<br>

## License

```
MIT License

Copyright (c) 2022 HackSquadDev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
...
```

Kindly view the [original document](LICENSE) for the full license.