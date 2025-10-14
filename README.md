# IKT222-Assignment-3

This is the instruction guide on how to run the repository code. You may also enter the following link to directly interface with the website through my VPS instead of having to build it yourself: {URL}

This repository is an example project for the IKT222 25H course at UiA Grimstad, Assignment 3 - User Authentication :mortar-board:.

## Prerequisites :exclamation:

1. Make sure you have Docker installed in order to be able to run this repository.
    - You may install Docker for your OS through the following link: [Docker Install](https://docs.docker.com/engine/install/)

## Setup :shipit:

Start by cloning the repository to your local computer:

```bash
git clone https://github.com/SolUrsi/IKT222-Assignment-3.git
```

From here you may build the Docker image and run it in Docker Compose:

```bash
sudo docker compose build && sudo docker compose up -d
```

You may now locally utilize the website by accessing it through your local host which is exposed by default at port 5000:

`http://localhost:5000`


## Finished?

Simply shut down the container:

```bash
sudo docker compose down
```

All done :white_check_mark:

## Known errors :x:
