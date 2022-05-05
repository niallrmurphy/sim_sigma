sim_sigma
===
Build a network graph and simulate latency distance between nodes

## Install
System Prereqs
* pkg-config
* libcairo2-dev

If you want to visualize the simulation via matplotlib you'll also need to install the python-tk version that corresponds with your installed version of python.
* python3.8-tk

If you're on ubuntu 20.04, you can install these with this command:
* `sudo apt install pkg-config libcairo2-dev python3.8-tk`

To install sim_sigma, first install the requirements:
* `pip install -r requirements.txt`

There are `Makefile` convenience functions to do this for you:
* `make deps` to install system dependencies
* `make reqs` to install python requirements

## Run
To run the simulaltion:
* `python3 sim.py`

Using the `Makefile` you can also run this with:
* `make run`

You can run the tests the same way
* `python3 sim-test.py`
or
* `make tests`