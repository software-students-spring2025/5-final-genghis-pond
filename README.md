# Final Project - Genghis Pond

## Project Description

Welcome To Genghis Pond! A web app in which you can share and upload pictues of animals you encounter. The website uses machine learning to idenitify the animal in the photo. Others can also vote on what they believe the identification of the animal is! Then you can share the location of the encounter!
Don't worry, if your species is identified as being endangered it will not be shown on the website for the protection of the animal.


## Contributors

-[Anna Ye](https://github.com/AnnaTheYe)
-[Tadelin De Leon](https://github.com/TadelinD)
-[Kurt Lukowitsch](https://github.com/kl3641)
-[Sophia Wang](https://github.com/s-m-wang)

## Link To Container Images

Hosted on Docker Hub: https://hub.docker.com/r/annaye/genghis-pond

# How to run

## Public Website

You can visit our website using the link: https://genghis-pond.org/

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

# Citations
Databases used for the web app:

* GBIF.org (15 April 2025) GBIF Occurrence Download https://doi.org/10.15468/dl.zuup37
* IUCN (2025). The IUCN Red List of Threatened Species. Version 2025-1. https://www.iucnredlist.org/. Downloaded on 2025-04-07. https://doi.org/10.15468/0qnb58 accessed via GBIF.org on 2025-04-29.
