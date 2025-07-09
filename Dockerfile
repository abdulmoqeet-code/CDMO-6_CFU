FROM minizinc/minizinc:latest

WORKDIR /src

COPY . .

RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-venv \
    && apt-get clean


RUN python3 -m venv /env

RUN /env/bin/pip install --upgrade pip
RUN /env/bin/pip install -r requirements.txt

RUN /env/bin/python3 -m amplpy.modules install highs gurobi

RUN /env/bin/python3 -m amplpy.modules activate cd80a89f-c2e0-4faf-9a68-c68a8cdbc006

ENV PATH="/env/bin:$PATH"

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]