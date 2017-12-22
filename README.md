# vacation-management
Written by Máté Szedlák (2017)

Demo holiday management web app
==========
This is a simple docker-based webapp written in python.

# Requirements
* docker
* docker compose
* local mysql server


# Usage
Once the docker -compose containers are up, the app can be reached at the localhost:
[**https://localhost**](https://localhost)

# Installation
Before starting the app, please configure the database connection in the config.py file:
* "Database configuration"

If the setting are correct, open a terminal, go to the project's root folder and run the following commands:
* docker-compose build
* docker-compose up -d

If the containers started correctly, the site can be reached at the [localhost](https://localhost).
To check the logs if needed, use the following command:
* docker-compose logs -f

# Start using
In order to use the app, google login is required.