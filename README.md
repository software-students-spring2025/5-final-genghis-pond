[![Genghis Pond CI/CD](https://github.com/software-students-spring2025/5-final-genghis-pond/actions/workflows/web-app-build.yaml/badge.svg)](https://github.com/software-students-spring2025/5-final-genghis-pond/actions/workflows/web-app-build.yaml)

# Final Project - Genghis Pond

## Project Description

Welcome To Genghis Pond! A web app in which you can share and upload pictues of animals you encounter. The website uses machine learning to idenitify the animal in the photo. Others can also vote on what they believe the identification of the animal is! Then you can share the location of the encounter!
Don't worry, if your species is identified as being critically endangered it will not be shown on the website for the protection of the animal.


## Contributors

- [Anna Ye](https://github.com/AnnaTheYe)
- [Tadelin De Leon](https://github.com/TadelinD)
- [Kurt Lukowitsch](https://github.com/kl3641)
- [Sophia Wang](https://github.com/s-m-wang)

## Link To Container Images

Hosted on Docker Hub: 
- Flask Web-app [https://hub.docker.com/r/annaye/genghis-pond](https://hub.docker.com/r/annaye/genghis-pond)
- Mongodb [https://hub.docker.com/_/mongo](https://hub.docker.com/_/mongo)

# How to run

## Public Website

You can visit our website using the link: [https://genghis-pond.org/](https://genghis-pond.org/)

## Local Configuration

### 1. Make sure you have downloaded docker desktop and have made an account.

### 2. Clone our repository:

```
git clone https://github.com/software-students-spring2025/5-final-genghis-pond
```


### 3. Build the docker image:

```
docker-compose up --build
```

### 4. Visit the link:

```
http://localhost:5002/
```

## Running Pytests

### 2. Clone our repository:

```
git clone https://github.com/software-students-spring2025/5-final-genghis-pond
```

### 3. Change directories:

```
cd 5-final-genghis-pond
```

### 4. Set MONGO_URI

```
$export MONGO_URI=mongodb://localhost:27017/genghis-pond-test
```

### 5. Build the docker image in detached mode:

```
docker compose up --d
```

### 6. Start virtual environment:

```
pipenv shell
```

### 7. Run pytests with coverage:

```
pipenv run pytest --cov=. --cov-report=term-missing
```

# Example .env file in root directory

```
PASSWORD=realverycoolpassword
HOST=host.ip.address
USERNAME=username
DOCKER_USERNAME=docker_username
DOCKER_PASSWORD=docker_password
FLASK_ENV=production
MONGO_URI=mongodb://localhost:27017/testdb
AWS_ACCESS_KEY_ID=secret_key_id
AWS_SECRET_ACCESS_KEY=secret_access_key
AWS_STORAGE_BUCKET_NAME=bucket_name
AWS_S3_REGION_NAME=region
PYTHONPATH=. pytest
```

# Citations
Databases used for the web app:

* GBIF.org (15 April 2025) GBIF Occurrence Download https://doi.org/10.15468/dl.zuup37
* IUCN (2025). The IUCN Red List of Threatened Species. Version 2025-1. https://www.iucnredlist.org/. Downloaded on 2025-04-07. https://doi.org/10.15468/0qnb58 accessed via GBIF.org on 2025-04-29.

* Speciesnet
authors:
  - family-names: Gadot
    given-names: Tomer
  - family-names: Istrate
    given-names: Ștefan
  - family-names: Kim
    given-names: Hyungwon
  - family-names: Morris
    given-names: Dan
  - family-names: Beery
    given-names: Sara
  - family-names: Birch
    given-names: Tanya
  - family-names: Ahumada
    given-names: Jorge
title: "To crop or not to crop: Comparing whole-image and cropped classification on a large dataset of camera trap images"
version: "1.0.0"
date-released: "2024-11-24"
publisher: "Wiley Online Library"
journal: "IET Computer Vision"
volume: "18"
issue: "8"
pages: "1193--1208"
year: "2024"
doi: "10.1049/cvi2.12318" 
type: software
keywords:
  - Camera traps
  - Conservation
  - Computer vision
