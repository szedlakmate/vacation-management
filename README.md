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

** Before first use, the corresponding database should be resetted by visiting the following address:
* [https://localhost/reset](https://localhost/reset)

To check the logs if needed, use the following command:
* docker-compose logs -f

# Start using
In order to use the app, google login is required.

Please note that the very first user who registers will automatically become admin.

# Known bugs
The list of known bugs can be reached [here](https://github.com/szedlakmate/vacation-management/blob/master/Known_bugs.md).