# Projeto Final — Smart Home (Hub de Automação Residencial)

## Visão Geral

Este projeto implementa um Smart Home Hub em Python, capaz de gerenciar diversos dispositivos residenciais através de uma interface de linha de comando (CLI). Ele aplica conceitos de Programação Orientada a Objetos (OOP), máquinas de estados finitos (FSM), persistência de dados (JSON e CSV), programação funcional e padrões de design.

## Estrutura do Projeto

```
smart_home/
  README.md
  requirements.txt
  data/
    configuracao.exemplo.json
    eventos.exemplo.csv
    relatorio.exemplo.csv
  smart_home/
    __init__.py
    core/
      cli.py             # implementação da linha de comando
      hub.py             # gerenciamento dos dispositivos e observadores
      dispositivos.py    # classe base e enums de tipos de dispositivos
      eventos.py         # tipos de eventos do hub
      observers.py       # Observer (console/arquivo)
      logger.py          # Singleton para logging em CSV
      persistencia.py    # carregar/salvar configuração em JSON
      erros.py           # exceções personalizadas
    dispositivos/       #uma classe específica para cada dispositivo implementado
      porta.py
      luz.py
      tomada.py
      cafeteira.py
      # outros de acordo com dispositivos escolhidos
```


## Requisitos

- Python 3.10 ou superior
- Biblioteca `transitions`

## Instalação
1.Clone o repositório:
```bash
git clone https://github.com/tamyressilvazz/Smart-Home.git
cd smart_home
```

2.Crie e ative o ambiente virtual:

No Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
No Windows (PowerShell):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

No Windows (Prompt de Comando):
```bash
python -m venv venv
.\venv\Scripts\activate.bat
```

3.Instale as dependências:
```bash
pip install -r requirements.txt
```


## Execução

Para iniciar o Smart Home Hub, execute:
```bash
python -m smart_home.core.cli --config data/configuracao.exemplo.json
```

## Uso do CLI

O sistema oferece um menu interativo com as seguintes opções:

1 - Listar dispositivos

2 - Mostrar dispositivo 

3 - Executar comando em dispositivo

4 - Alterar atributo de dispositivo

5 - Executar rotina

6 - Gerar relatório

7 - Salvar configuração

8 - Adicionar dispositivo

9 - Remover dispositivo

10 - Sair

## Exemplos

* Listar dispositivos
```bash
Escolha uma opcao: 1
# Exibe a lista de dispositivos cadastrados
```

* Adicionar uma luz
```bash
Escolha uma opcao: 8
Tipos suportados: PORTA, LUZ, TOMADA, CAFETEIRA, ...
tipo: LUZ
id (sem espacos): luz_cozinha
nome: Luz da Cozinha
brilho (0-100) [50]: 60
cor [QUENTE/FRIA/NEUTRA] [QUENTE]: FRIA
[EVENTO] DispositivoAdicionado: {'id': 'luz_cozinha', 'tipo': 'LUZ'}
dispositivo luz_cozinha adicionado.
```
* Executar comando para ligar a luz
```bash
Escolha uma opcao: 3
id do dispositivo: luz_cozinha
comando: ligar
argumentos (k=v separados por espaco) ou ENTER:
```
* Salvar configuração
```bash
Escolha uma opcao: 7
Configuracao salva.
```
* Sair
```bash
Escolha uma opcao: 10
saindo...
```
## Arquivos de Dados

* `data/configuracao.log.json`: Configuração inicial dos dispositivos e rotinas.

* `data/eventos.log.csv`: Log de eventos e transições dos dispositivos.

* `data/relatorio.log.csv`: Exemplo de relatório gerado pelo sistema.

## Rotinas Pré-definidas
* **modo_noite**: Tranca a porta de entrada, desliga todas as luzes e arma o alarme.
* **acordar**: Liga a luz do quarto (50% brilho), prepara a cafeteira e abre a persiana.
* **modo_conforto**: Liga ar condicionado em modo REFRIGERAÇÃO a 22°C, liga caixa de som e toca música ambiente, ajusta termostato para aquecimento a 24°C.
* **modo_eco**: Desliga ar condicionado e caixa de som, desativa termostato para economia de energia.

## Padrões de Projeto Utilizados

* **Singleton**: Para o sistema de logging.
* **Observer**: Para notificação de eventos.

## Programação Funcional
O sistema utiliza funções como map, filter e reduce para gerar relatórios, como:

* Consumo de energia por tomada inteligente.
* Tempo total em que cada luz permaneceu ligada.
* Dispositivos mais usados.

## Testes

Testes básicos podem ser executados diretamente nos módulos, utilizando blocos:
```Python
 if __name__ == '__main__':
```