
![logo](https://raw.githubusercontent.com/Humbedooh/clc/main/logo.svg) 
# CLC - Conscious Language Checker


## Installation

- Clone the repo
- go to the `server` dir and fix up `clc.yaml` to your liking
- install `pipenv`: `apt install pipenv` or `yum install pipenv` etc
- from the `server` dir, run: `pipenv install -r requirements.txt`
- finally, to start the service, run: `pipenv run python3 main.py` and rejoice

### Running as a Docker container

The simplest form is to use the provided `Dockerfile` as such:

- `docker build . -t clc`
- `docker run -d -p 8080:8080 clc`

And visit http://localhost:8080/ for goodness!

