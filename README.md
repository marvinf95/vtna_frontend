# VTNA: Visualize Network Dynamics with Attributes
[![Binder](https://mybinder.org/badge.svg)](https://hub.mybinder.org/user/marvinf95-vtna_frontend-gs3u26rf/notebooks/frontend/vtna.ipynb)

# What is VTNA?
VTNA  is a [Jupyter Notebook](https://jupyter.org/) for the visualization of face-to-face networks collected over long time frames. 
This tool focuses specifically on data collected by the [Sociopatterns](http://www.sociopatterns.org/) project.

# Supported tags and respective `Dockerfile` links
-	[`latest`, `python0.1` (*Dockerfile*)](https://github.com/marvinf95/vtna_frontend/blob/master/Dockerfile)
-	[`alpine0.1` (*Dockerfile_alpine*)](https://github.com/marvinf95/vtna_frontend/blob/master/Dockerfile_alpine)
-	[`minimal-notebook0.1` (*Dockerfile_minimal-notebook*)](https://github.com/marvinf95/vtna_frontend/blob/master/Dockerfile_minimal-notebook)

# How to use this image

### Installation
Prerequisites:
* Internet connection
* [Installed docker](https://docs.docker.com/engine/installation/)
  * Running docker service
  * Docker CLI

## Start a vtna container
```console
$ docker run -t -p 8888:8888 --name vtna marvinf/vtna:python0.1
```
After the start you can open the notebook by copying the shown link in the terminal to the browser.

### Stop and start container
```console
$ docker stop vtna
$ docker start vtna
```

### Cleanup
Delete the docker container and the image.
```console
$ docker stop vtna && docker rm vtna
$ docker rmi marvinf/vtna:python0.1
```

## Additionally, If you want to use your own notebook ...
You can create your own Dockerfile that adds a notebook from the context into frontend/, like so.
```dockerfile
FROM marvinf/vtna:$TAG
USER vtna
WORKDIR /usr/src/vtna/
COPY $NOTEBOOK frontend/
CMD jupyter notebook --ip 0.0.0.0 --no-browser frontend/
```
```console
$ docker build -t vtna_private_notebook:1 .
$ docker run -t -p 8888:8888 --name vtna_private_notebook vtna_private_notebook:1
```

Alternatively, you can specify something along the same lines with `docker run` options.
```console
$ docker run -it -p 8888:8888 -u vtna -w /usr/src/vtna/ -v $(pwd)/notebook/$NOTEBOOK:/usr/src/vtna/frontend/$NOTEBOOK --name vtna_private_notebook marvinf/vtna:&TAG jupyter notebook --ip 0.0.0.0 --no-browser frontend/
```
(Notebook must be in a folder, cause otherwise the notebook is created not as a file in the container.)
Using this method means that there is no need for you to have a Dockerfile for your vtna container.

# Image Variants
The `vtna` images come in many flavors, each designed for a specific use case.

## `vtna:<version>`
This is the defacto image. If you are unsure about what your needs are, you probably want to use this one. It is designed to be used both as a throw away container (mount your source code and start the container to start your app), as well as the base to build other images off of.

## `vtna:minimal-notebook`
This image is based on the [Jupyter Notebook minimal image](https://hub.docker.com/r/jupyter/minimal-notebook/). It is useful if you want to test and add some code to the application. For that, the most common python modules are already installed. Because of that it's larger than the other images.

## `vtna:alpine`
This image is based on the popular [Alpine Linux project](http://alpinelinux.org), available in [the `alpine` official image](https://hub.docker.com/_/alpine). Alpine Linux is much smaller than most distribution base images (~5MB), and thus leads to much slimmer images in general.

This variant is highly recommended when final image size being as small as possible is desired. The main caveat to note is that it does use [musl libc](http://www.musl-libc.org) instead of [glibc and friends](http://www.etalabs.net/compare_libcs.html), so certain software might run into issues depending on the depth of their libc requirements. However, most software doesn't have an issue with this, so this variant is usually a very safe choice. See [this Hacker News comment thread](https://news.ycombinator.com/item?id=10782897) for more discussion of the issues that might arise and some pro/con comparisons of using Alpine-based images.

To minimize image size, it's uncommon for additional related tools (such as `git` or `bash`) to be included in Alpine-based images. Using this image as a base, add the things you need in your own Dockerfile (see the [`alpine` image description](https://hub.docker.com/_/alpine/) for examples of how to install packages if you are unfamiliar).

# Quick reference
-	**Where to get help**:  
	[the Docker Community Forums](https://forums.docker.com/), [the Docker Community Slack](https://blog.docker.com/2016/11/introducing-docker-community-directory-docker-community-slack/), or [Stack Overflow](https://stackoverflow.com/search?tab=newest&q=docker)

-	**Where to file issues**:  
	[https://github.com/marvinf95/vtna_frontend/issues](https://github.com/marvinf95/vtna_frontend/issues)

-	**Maintained by**:  
	[Students of the University Koblenz-Landau](https://www.uni-koblenz-landau.de/)

    | Name              | EMail                        |
    | --------          | --------                     |
    | Alex Baier        | abaier@uni-koblenz.de        |
    | Evgeny Sinderovich| evsinderovich@uni-koblenz.de |
    | Adam Mtarji       | amtarji@uni-koblenz.de       |
    | Kim Ballmes       | ballmes@uni-koblenz.de       |
    | Marvin Forster    | marvinforster@uni-koblenz.de |
    | Philipp Töws      | ptoews@uni-koblenz.de        |

-	**Supported Docker versions**:  
	[the latest release](https://github.com/docker/docker-ce/releases/latest) (down to 1.6 on a best-effort basis)

# License
View [license information](https://github.com/marvinf95/vtna_frontend/blob/master/LICENSE) for the software contained in this image.

As with all Docker images, these likely also contain other software which may be under other licenses (such as Bash, etc from the base distribution, along with any direct or indirect dependencies of the primary software being contained).

Some additional license information which was able to be auto-detected might be found in [the `repo-info` repository's `vtna/` directory](https://github.com/marvinf95/vtna_frontend/blob/master/LICENSE).

As for any pre-built image usage, it is the image user's responsibility to ensure that any use of this image complies with any relevant licenses for all software contained within.
