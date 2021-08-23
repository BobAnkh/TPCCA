# Transient Performance of Congestion Control Algorithms

Quantifying the Transient Performance of Congestion Control Algorithms (SIGCOMM 2021 POSTER)

## Usage

### Setup

We do our experiment on Ubuntu, so if you are using other OS, please setup the envrionment by yourself according to `setup.sh`.

First create a virtual environment for python, using `conda`, `venv` or whatever you like, and activate it.

Run `setup.sh` by `bash setup.sh` or other similar commands. The script `setup.sh` will help you do the following things:

- Create folders needed.
- Install **Rust** if you haven't installed it.
- Get all git submodules.
- Reset everything.
- Build ccp-kernel and other CCAs.
- Build **Mahimahi**.
- Install some Python dependencies.

### Run experiment

We use `config.toml` in default to configure all the parameters needed for running experiments. See it for the detailed configuration.

When you finish your experiment settings in `config.toml`, you can just run `python run_exp.py`.

Also you can use `-c` or `--config` argument to specify another config file(in tomal format), e.g. `python run_exp.py -c another_config.toml`.

### Analyze data collected and plot figures

We use `config.toml` in default to configure all the parameters needed for analyzing data collected. See it for the detailed configuration.

When you finish your analysis settings in `config.toml`, you can just run `python log_parse.py`.

Also you can use `-c` or `--config` argument to specify another config file(in tomal format), e.g. `python log_parse.py -c another_config.toml`.

## Credits

Many thanks to [Congestion Control Plane](https://ccp-project.github.io/)([SIGCOMM2018-PAPER](https://akshayn.xyz/res/ccp-sigcomm18.pdf)). With its awesome work, we can easily implement a series of CCAs and do our analysis.

Also thanks to [Mahimahi](https://github.com/ravinet/mahimahi) for enabling us to emulate on different network conditions.

## LICENSE

[Apache-2.0](/LICENSE) © BobAnkh

## Cite

```bibtex
@inproceedings{10.1145/3472716.3472861,
author = {Shen, Yixin and Meng, Zili and Chen, Jing and Xu, Mingwei},
title = {Quantifying the Transient Performance of Congestion Control Algorithms},
year = {2021},
isbn = {9781450386296},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3472716.3472861},
doi = {10.1145/3472716.3472861},
booktitle = {Proceedings of the SIGCOMM '21 Poster and Demo Sessions},
pages = {42–44},
numpages = {3},
keywords = {verification, congestion control algorithm, transient performance},
location = {Virtual Event},
series = {SIGCOMM '21}
}
```
