import json
import os
from smart_home.core.erros import ConfigInvalida

# carregar/salvar configuração em JSON
class Persistencia:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def carregar_configuracao(self) -> dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Arquivo de configuracao nao encontrado: {self.config_path}")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Validação básica da estrutura do JSON
            if not isinstance(config, dict) or 'dispositivos' not in config or 'rotinas' not in config:
                raise ConfigInvalida("Estrutura do arquivo de configuracao JSON invalida.")
            return config
        except json.JSONDecodeError as e:
            raise ConfigInvalida(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            raise ConfigInvalida(f"Erro inesperado ao carregar configuracao: {e}")
    def salvar_configuracao(self, config: dict):
        try:
            # Garante que o diretório 'data' existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Erro ao salvar configuracao: {e}")

#teste
if __name__ == '__main__':
    test_config_path = 'data/config.json'
    persistencia = Persistencia(test_config_path)