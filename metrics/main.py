from argparse import ArgumentParser

from lib.config import Config
from lib.tester import Tester

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config", action="store",
                        dest="config", required=True,
                        help="Path to a config file")

    args = parser.parse_args()
    config = Config(args.config)

    tester = Tester(config)
    tester.test()
