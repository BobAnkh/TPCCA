# Quantify Transient Performance

Quantifying the Transient Performance of Congestion Control Algorithms (SIGCOMM 2021 POSTER)

## Usage

### Setup

We do our experiment on Ubuntu, so if you are using other OS, please setup yourself according to `setup.sh`.

First create a virtual environment for python, using `conda`, `venv` or whatever you like, and activate it.

Run `setup.sh` by `sh setup.sh` or other similar commands. The script `setup.sh` will help you do the following things:

- Create folders needed.
- Install **Rust** if you haven't installed it.
- Get all git submodules.
- Reset everything.
- Build ccp-kernel and other CCAs.
- Build Mahimahi.
- Install some Python dependencies.

### Run experiment

We use `config.toml` to configure all the parameters needed for running experiments. See it for the detailed configuration.

When you finish your experiment settings in `config.toml`, you can just run `python run_exp.py`.

### Analyze data collected

We use `config.toml` to configure all the parameters needed for analyzing data collected. See it for the detailed configuration.

When you finish your analysis settings in `config.toml`, you can just run `python log_parse.py`.

## Thanks

Many thanks to [Congestion Control Plane](https://ccp-project.github.io/)([SIGCOMM2018-PAPER](https://akshayn.xyz/res/ccp-sigcomm18.pdf)). With its awesome work, we can easily implement a series of CCAs and do our analysis.

Also thanks to [Mahimahi](https://github.com/ravinet/mahimahi) for enabling us to emulate on different network conditions.

## LICENSE

[Apache-2.0](/LICENSE) © BobAnkh

## Cite
