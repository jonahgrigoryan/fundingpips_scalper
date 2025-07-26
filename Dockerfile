FROM continuumio/miniconda3

WORKDIR /app
COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "fundingpips-scalper", "/bin/bash", "-c"]

COPY . .
CMD ["pytest"]