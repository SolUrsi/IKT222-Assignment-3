# IKT222-Assignment-3

This is the instruction guide on how to run the repository code. You may also enter the following link to directly interface with the website through my VPS instead of having to build it yourself: {URL} (Give it a try!)

This repository is an example project for the IKT222 25H course at UiA Grimstad, Assignment 3 - User Authentication :mortar_board:

## Prerequisites :exclamation:

1. Make sure you have **Docker** installed in order to be able to run this repository.
    - You may install Docker for your OS through the following link: [Docker Install](https://docs.docker.com/engine/install/)

## Setup :shipit:

Start by cloning the repository to your local computer:

```bash
git clone https://github.com/SolUrsi/IKT222-Assignment-3.git
```

Navigate to the root directory of the cloned repository.
Now copy the contents of `.env.example` into a new environment `.env` and change the SECRET_KEY variable to a secure string. This will be used by Flask to verify sessions:

```bash
cp .env.example .env
echo -n "Enter your secure SECRET_KEY: "
read SEC_KEY
sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SEC_KEY/" .env
rm .env.bak
echo "SECRET_KEY successfully written to .env"
```

From here you may build the Docker image and run it in Docker Compose. The database structure will be automatically created in the ./data directory during the build process.

```bash
docker compose build && docker compose up -d
```

You may now locally utilize the website by accessing it through your localhost which is exposed by default at port 5000:

`http://localhost:5000`


## Finished?

Simply shut down the container:

```bash
docker compose down
```

All done :white_check_mark:

## Known errors :x:

Currently no know errors.
