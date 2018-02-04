# Visualize Network Dynamics
Forschungspraktikum at West Institute

[Wiki](https://gitlab.uni-koblenz.de/marvinforster/vtna/wikis/home)


## Using the application with Docker
### Installation
Prerequisites:
* Internet connection
* [Installed docker](https://docs.docker.com/engine/installation/)
  * Running docker service
  * Docker CLI

The following commands that need to be executed in a terminal create a docker image with a jupyter notebook and the full application.
After building the image a container that is running the notebook will be created.
```bash
git clone $REPO
docker build -t $IMAGENAME:$TAG .
docker run --name vtna -t -p 8888:8888 $IMAGENAME:$TAG
```

Now you can click on the URL shown in the Terminal. This will open the notebook in your browser.

### Stop and start container
```bash
docker stop vtna
docker start vtna
```

### Cleanup
Delete the docker container and the image.
```bash
docker stop vtna && docker rm vtna
docker rmi $IMAGENAME:$TAG
```

## Team

| Name              | EMail                        |
| --------          | --------                     |
| Alex Baier        | abaier@uni-koblenz.de        |
| Evgeny Sinderovich| evsinderovich@uni-koblenz.de |
| Adam Mtarji       | amtarji@uni-koblenz.de       |
| Kim Ballmes       | ballmes@uni-koblenz.de       |
| Marvin Forster    | marvinforster@uni-koblenz.de |
| Philipp Töws      | ptoews@uni-koblenz.de        |
