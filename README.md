
![logo](https://raw.githubusercontent.com/Humbedooh/clc/main/logo.svg) 
# CLC - Conscious Language Checker
CLC is a suite of tools that checks software projects for potentially problematic 
words and sentences and tracks the development over time. It comes with a background 
indexer and a web server with a visual user interface for viewing reports and 
adding/editing projects.

A (currently read-only) demo of this service can be found at: https://clcdemo.net/


## Installation

- Clone the repo: `git clone https://github.com/Humbedooh/clc.git`
- Go to the `server/` dir and fix up `clc.yaml` to your liking
- To run with `pipenv` for virtualizing the environment:
  - Install `pipenv`: `apt install pipenv` or `yum install pipenv` etc (older systems might use `pip3 install pipenv`)
  - From the `server/` dir, run: `pipenv install -r requirements.txt`
  - Start the service: `pipenv run python3 main.py` and see your service at http://localhost:8080 (default settings)
- OR, you can pick the global `pip3` method if `pipenv` is not available:
  - From the `server/` dir, run: `pip3 install -r requirements.txt`
  - Start the service: `python3 main.py` and see your service at http://localhost:8080 
 
### Running as a Docker container

The simplest form is to use the provided `Dockerfile` as such:

- `docker build . -t clc`
- `docker run -d -p 8080:8080 clc`

And visit http://localhost:8080/ for goodness!

### Speeding up YAML parsing
If you have a project with a lot of issues (10,000+), you can make use of the 
C++ YAML parser in python by installing the `libyaml-cpp-dev` package before you 
instapp PyYaml. This will speed up YAML parsing/writing by 10x.


## Default scan options
The default set or words and contexts to scan for is defined in the `defaults.yaml` file.
It contains a set of potentially problematic words and their contexts, as well as an exclude 
list (both files and sentence contexts) for where the words are either unavoidable or harmless.

Any new project added will use these defaults unless otherwise specified in the project settings.
