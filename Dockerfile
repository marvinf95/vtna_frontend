## https://hub.docker.com/r/jupyter/minimal-notebook/
FROM jupyter/minimal-notebook

USER root

RUN apt-get update

## User from the minimal notebook
USER jovyan

WORKDIR /home/jovyan

COPY vtna ./vtna
COPY frontend ./frontend
RUN pip install --no-cache-dir -r frontend/requirements.txt
RUN pip install --no-cache-dir -r vtna/requirements.txt
RUN pip install vtna/

USER root

RUN jupyter nbextension enable --py widgetsnbextension && jupyter nbextension install --py fileupload && jupyter nbextension enable --py fileupload


USER jovyan
#EXPOSE 8888:8888

CMD jupyter notebook --ip 0.0.0.0 --no-browser
