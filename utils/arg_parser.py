import argparse

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        help=
        'Path of the config file. File should be toml.',
        default='config.toml')
    args = parser.parse_args()
    return args
