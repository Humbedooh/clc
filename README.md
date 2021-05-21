
![logo](https://raw.githubusercontent.com/Humbedooh/clc/main/logo.svg) 
# CLC - Conscious Language Checker


## Installation

- Clone the repo: `git clone https://github.com/Humbedooh/clc.git`
- Go to the `server/` dir and fix up `clc.yaml` to your liking
- Install `pipenv`: `apt install pipenv` or `yum install pipenv` etc (older systems might use `pip3 install pipenv`)
- From the `server/` dir, run: `pipenv install -r requirements.txt`
- Finally, to start the service, run: `pipenv run python3 main.py` and see your service at http://localhost:8080 (default settings)

### Running as a Docker container

The simplest form is to use the provided `Dockerfile` as such:

- `docker build . -t clc`
- `docker run -d -p 8080:8080 clc`

And visit http://localhost:8080/ for goodness!

