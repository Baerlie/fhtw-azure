FROM python:3.8
LABEL maintainer="baerlie"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install -y tmux nano
RUN chmod +x ./sessions.sh
CMD ["/bin/bash", "-c", "./sessions.sh"]

# exposes ports 8000 for uvicorn, port 8501 for streamlit
EXPOSE 8000
EXPOSE 80
