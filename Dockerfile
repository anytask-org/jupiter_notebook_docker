FROM ubuntu:22.04
LABEL org.opencontainers.image.source https://github.com/anytask-org/jupiter_notebook_docker

RUN apt-get update
RUN apt-get install -y python2  python3 python3-pip
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

ADD requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir -r /requirements.txt

ADD get-pip.py /get-pip.py
RUN python2 /get-pip.py
RUN python2 -m pip install --no-cache-dir ipykernel

RUN adduser --disabled-password jupyter
RUN mkdir -p /home/jupyter/.jupyter
ADD jupyter_notebook_config.py /home/jupyter/.jupyter/
RUN chown -R jupyter:jupyter ~jupyter

RUN mkdir /notebooks
RUN chown -R jupyter:jupyter /notebooks

EXPOSE 8888

# Start uWSGI
CMD ["su", "--", "jupyter", "-c", "jupyter notebook"]
