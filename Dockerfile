FROM jupyter/minimal-notebook

## User from the minimal notebook
USER jovyan

WORKDIR /home/jovyan

#RUN apt-get update && apt-get install -yq pip python3.6

COPY vtna ./vtna
COPY frontend ./frontend
RUN ls
RUN pip install --no-cache-dir -r frontend/requirements.txt
RUN pip install --no-cache-dir -r vtna/requirements.txt
RUN pip install vtna/

#EXPOSE 8888

CMD jupyter notebook --ip 0.0.0.0 --no-browser

#CMD jupyter notebook --ip 0.0.0.0 --no-browser
