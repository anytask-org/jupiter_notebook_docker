FROM ubuntu:mantic
LABEL org.opencontainers.image.source https://github.com/anytask-org/jupiter_notebook_docker

RUN apt-get update && \
    apt-get install -y python3 python3-pip coreutils curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN curl https://pyenv.run | bash
RUN pyenv update
RUN pyenv install 2.7.18

ADD requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir -r /requirements.txt

ADD get-pip.py /get-pip.py
RUN python2 /get-pip.py
RUN python2 -m pip install --no-cache-dir ipykernel

RUN adduser --disabled-password jupyter
RUN mkdir -p /home/jupyter/.jupyter
ADD jupyter_notebook_config.py /home/jupyter/.jupyter/
ADD gatekeeper.py /home/jupyter/
ADD run.sh /home/jupyter/
RUN chown -R jupyter:jupyter ~jupyter

RUN mkdir /notebooks
RUN chown -R jupyter:jupyter /notebooks

EXPOSE 5555
EXPOSE 8888

WORKDIR /home/jupyter/
CMD ["su", "--", "jupyter", "-c", "./run.sh"]
