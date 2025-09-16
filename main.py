import argparse
from smart_home.core.cli import CLI
from smart_home.core.hub import Hub

parser = argparse.ArgumentParser(description="Smart Home Hub CLI")
parser.add_argument('--config', type=str, default='data/configuracao.json',
                    help='Caminho para o arquivo de configuracao JSON.')
args = parser.parse_args()

cli = CLI(args.config)
cli.run()