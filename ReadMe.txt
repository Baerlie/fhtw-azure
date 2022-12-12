docker installs tmux and nano with the python 3.8 image

pull and run with the following commands:
docker pull baerlie/fhtw-a-lab3:latest
docker run -it -p 8000:8000 -p 8501:8501 --name lab3_pscheidl fhtw-a-lab3

container will start streamlit and uvicorn in one container