import os
from smart_home.core.cli import CLI
from smart_home.core.hub import SmartHomeHub
def main():
    # Define o caminho padrão para o arquivo de configuração JSON
    config_path = os.path.join('data', 'configuracao.log.json')
    
    # Garante que o diretório 'data' existe
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Cria a instância da CLI passando o caminho da configuração
    cli = CLI(config_path)
    
    # Executa o principal da CLI
    cli.run()
if __name__ == '__main__':
    main()
