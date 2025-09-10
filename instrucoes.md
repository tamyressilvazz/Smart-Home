# Projeto Final — Smart Home (Hub de Automação Residencial)

## Objetivo

O projeto consiste em desenvolver um **sistema de automação residencial** em Python, chamado **Smart Home Hub**, capaz de gerenciar diferentes dispositivos (porta, luz, tomada inteligente, termostato, cafeteira, persiana, irrigador, alarme, etc.).

O sistema deve aplicar conceitos estudados na disciplina: **OOP (herança, polimorfismo, encapsulamento, classes abstratas, dataclasses, enums, descritores, propriedades)**, **exceções**, **arquivos (JSON e CSV)**, **programação funcional (map/filter/reduce, compreensões)**, **design patterns (Singleton, Observer)** e **máquinas de estados finitos (FSM) com a biblioteca `transitions`**.

O **hub** deve oferecer uma **interface em linha de comando (CLI)** com menu em português (os itens do menu podem ser **sem acentos** para facilitar a digitação e evitar problemas de _encoding_, se for o caso), persistindo estado entre execuções (carrega configuração ao iniciar, salva ao sair).

## Requisitos Técnicos

### 1. Organização

* Código em pacotes e módulos.
* Cada tipo de dispositivo em sua classe própria, herdando de uma classe raiz.
* `README.md` com instruções de execução e exemplos.
* Possível estrutura de pastas segue abaixo.

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

---

### 2. Ambiente

* Python 3.10+.
* `venv` + `requirements.txt`.

---

### 3. Dispositivos

* **Obrigatórios (3):** Porta, Luz, Tomada inteligente.
* **Adicionar pelo menos 3 outros** dispositivos da lista abaixo (ou inventar novos).
* A lista não é exaustiva; os alunos podem propor variações.
  Exemplos adicionais: Termostato, Cafeteira, Persiana, Irrigador, Alarme, Sensor de presença, Câmera.
* Cada dispositivo adicional deve ter:

  * Uma máquina de estados interna usando **`transitions`**.
  * **Atributos validados** com descritores e propriedades.
  * Métodos de comando claros (`ligar`, `desligar`, `abrir`, `fechar`, etc.).
* Segue abaixo a estrutura a ser seguida para os dispositivos obrigatórios. **Esses três dispositivos devem seguir exatamente essas FSMs.**

#### 1) Porta

* **Estados:** `trancada`, `destrancada`, `aberta`
* **Eventos/transições:**
  * `destrancar`: `trancada → destrancada`
  * `trancar`: `destrancada → trancada`
  * `abrir`: `destrancada → aberta`
  * `fechar`: `aberta → destrancada`
* **Regras/validacoes:**
  * Não é permitido `trancar` se a porta está `aberta`.
  * Armazene como atributo as `tentativas_invalidas` (contador de vezes em que tentou trancar uma porta aberta).

#### 2) Luz

* **Estados:** `off`, `on`
* **Eventos/transições:**
  * `ligar`: `off → on`
  * `desligar`: `on → off`
  * `definir_brilho[x]`: `on → on` *(permanece no estado `on`; **validar** que brilho está entre 0–100)*
  * `definir_cor[COLOR]`: `on → on` *(validar cor dentro de `Enum` associado)*
* **Atributos com validacao (descritores/propriedades):**
  * `brilho: int (0–100)`.
  * `cor: Enum (ex.: QUENTE, FRIA, NEUTRA)`.

#### 3) Tomada inteligente

* **Estados:** `off`, `on`
* **Eventos/transições:**
  * `ligar`: `off → on`
  * `desligar`: `on → off`
* **Atributos / métricas:**
  * `potencia_w: int ≥ 0` (validado).
  * `consumo_wh` acumulado estimado com base nos **intervalos em que a tomada ficou `ligada`**:
    `consumo_wh += potência (W) × tempo_ligada (h)`
    (o tempo pode ser inferido por eventos do log e/ou registro interno de "momento em que ligou".)

> **Importante:** As FSMs acima devem seguir a estrutura conforme descrito acima. Para os **demais dispositivos**, a FSM é **livre**, podem projetar a FSM e eventos como acharem melhor (desde que coerente com o tipo escolhido). 

---

### 4. Hub de Automação

* Adicionar/listar/manipular dispositivos.
* Executar rotinas predefinidas.
* Enviar notificações com **Observer** (console, arquivo).
* Salvar/carregar configuração em JSON.

#### Rotinas

**Rotina** é uma **sequência de comandos** aplicada a um conjunto de dispositivos para configurar a casa para uma situação específica. Seguem dois exemplos hipotéticos (assumindo a presença dos dispositivos listados nas rotinas).

* **Exemplo 1 – modo\_noite**:

  * Porta de entrada → `trancar`
  * Todas as luzes → `desligar`
  * Alarme → `armar`

* **Exemplo 2 – acordar**:

  * Luz do quarto → `ligar` (brilho 50%)
  * Cafeteira → `preparar`
  * Persiana → `abrir`

A implementação deve **definir no mínimo 2 rotinas**, podendo criar outras de acordo com a imaginação (ex.: “sair\_de\_casa”, “fim\_de\_semana”).

---

### 5. Persistência e I/O

* Configuração em **JSON** (dispositivos + rotinas).
* Logs de eventos em **CSV** (transições).
* Relatórios em **CSV** (uso/consumo).

#### Exemplo de arquivo de configuração JSON

```json
{
  "hub": { "nome": "Casa Exemplo", "versao": "1.0" },
  "dispositivos": [
    { "id": "porta_entrada", "tipo": "DOOR", "nome": "Porta de Entrada", "estado": "trancada", "atributos": {} },
    { "id": "luz_sala", "tipo": "LIGHT", "nome": "Luz da Sala", "estado": "off", "atributos": { "brilho": 70, "cor": "WARM" } },
    { "id": "tomada_tv", "tipo": "OUTLET", "nome": "Tomada TV", "estado": "off", "atributos": { "potencia_w": 120 } },
    { "id": "cafeteira", "tipo": "COFFEE_MAKER", "nome": "Cafeteira", "estado": "idle", "atributos": {} }
  ],
  "rotinas": {
    "modo_noite": [
      { "id": "porta_entrada", "comando": "trancar" },
      { "id": "luz_sala", "comando": "desligar" }
    ],
    "acordar": [
      { "id": "luz_sala", "comando": "ligar", "argumentos": {"brilho": 50} },
      { "id": "cafeteira", "comando": "preparar" }
    ]
  }
}
```

#### Exemplo de logs de eventos em CSV

```csv
timestamp,id_dispositivo,evento,estado_origem,estado_destino
2025-09-02T08:00:01,porta_entrada,destrancar,trancada,destrancada
2025-09-02T18:30:00,luz_sala,ligar,off,on
2025-09-02T22:00:00,luz_sala,desligar,on,off
2025-09-03T07:00:00,cafeteira,preparar,idle,moendo
2025-09-03T07:00:02,cafeteira,timeout,moendo,aquecendo
2025-09-03T07:00:05,cafeteira,timeout,aquecendo,preparando
2025-09-03T07:00:10,cafeteira,timeout,preparando,pronta
```

#### Exemplo de relatórios em CSV

```csv
id_dispositivo,total_wh,inicio_periodo,fim_periodo
tomada_tv,240,2025-09-01T00:00:00,2025-09-01T23:59:59
```

---

### 6. Padrões de Projeto

* **Obrigatórios:** **Singleton** (ex.: registrador CSV) e **Observer** (ex.: observador de console/arquivo).
* **Bônus:** Factory, Strategy, Decorator, Facade, etc.

---

### 7. Programação Funcional

Usar **map**, **filter**, **reduce** e/ou **compreensões** em consultas/relatórios.

**Exemplos mínimos de relatórios/consultas a implementar:**

1. **Consumo por tomada inteligente** → total de energia consumida em um período (com `reduce` para somar).
2. **Tempo total em que cada luz permaneceu ligada** → com base nos logs de eventos (com `map`/`filter` + comprehensions).
3. **Dispositivos mais usados** → ordenar por número de eventos no log (com `sorted`).

Além disso, implementar **pelo menos 2 relatórios adicionais**, por exemplo:

* Horários de maior uso do **sensor de presença**.
* Quantidade de **cafés** preparados na semana.
* **Percentual médio** de abertura de persianas.
* Distribuição de **comandos por tipo** de dispositivo.

---

### 8. Exceções

* Criar exceções personalizadas (`TransicaoInvalida`, `ConfigInvalida`, `ValidacaoAtributo`).
* Tratar erros de entrada/saída e transições inválidas.

---

### 9. CLI (Menu Fixo em Português, sem acentos)

Todos os grupos devem implementar a mesma estrutura de menu:

```
=== SMART HOME HUB ===
1. Listar dispositivos
2. Mostrar dispositivo
3. Executar comando em dispositivo
4. Alterar atributo de dispositivo
5. Executar rotina
6. Gerar relatorio
7. Salvar configuracao
8. Adicionar dispositivo
9. Remover dispositivo
10. Sair
Escolha uma opcao:
```

* **1** → lista dispositivos cadastrados
* **2** → mostra detalhes de um dispositivo
* **3** → executa evento/comando de FSM em dispositivo
* **4** → altera atributo (com validação)
* **5** → executa rotina (configurada no JSON)
* **6** → gera relatório (tipo + opções)
* **7** → salva configuração em JSON
* **8** → adiciona dispositivo (tipo, id, nome, atributos)
* **9** → remove dispositivo pelo `id`
* **10** → salva configuração no JSON e encerra


#### Exemplos de uso (CLI)

**Executando o programa**

```
$ python -m smart_home.core.cli --config data/config.sample.json
```

**8) Adicionar dispositivo — uma nova luz**

```
Escolha uma opcao: 8
Tipos suportados: PORTA, LUZ, TOMADA, CAFETEIRA
tipo: LUZ
id (sem espacos): luz_cozinha
nome: Luz da Cozinha
brilho (0-100) [50]: 60
cor [QUENTE/FRIA/NEUTRA] [QUENTE]: FRIA
[EVENTO] DispositivoAdicionado: {'id': 'luz_cozinha', 'tipo': 'LUZ'}
dispositivo luz_cozinha adicionado.
```

**1) Listar (agora aparece a nova luz)**

```
Escolha uma opcao: 1
porta_entrada | PORTA | trancada
luz_sala | LUZ | desligada
tomada_tv | TOMADA | desligada
cafeteira | CAFETEIRA | ociosa
luz_cozinha | LUZ | desligada
```

**3) Executar comando na nova luz**

```
Escolha uma opcao: 3
id do dispositivo: luz_cozinha
comando: ligar
argumentos (k=v separados por espaco) ou ENTER:
[EVENTO] ComandoExecutado: {'id': 'luz_cozinha', 'comando': 'ligar', 'antes': 'desligada', 'depois': 'ligada'}
```

**9) Remover dispositivo**

```
Escolha uma opcao: 9
id do dispositivo: luz_cozinha
[EVENTO] DispositivoRemovido: {'id': 'luz_cozinha', 'tipo': 'LUZ'}
dispositivo removido
```

**7) Salvar configuracao**

```
Escolha uma opcao: 7
configuracao salva.
```

**10) Sair (tambem salva)**

```
Escolha uma opcao: 10
saindo...
```

---

### 10. Testes

* Testes básicos podem ser implementados diretamente nos módulos, usando blocos:

  ```python
  if __name__ == '__main__':
      # testes rapidos aqui
  ```
* Exemplos: testar transições de FSM (validar `brilho`, checar `porta.trancar` bloqueado quando `aberta`), validação de atributos, salvar/carregar JSON.

---

## Entregáveis

1. Código-fonte organizado.
2. `requirements.txt`.
3. `README.md` (execução, exemplos de CLI, formato JSON/CSV, rotinas definidas).
4. Arquivos-exemplo: JSON (configuração), CSV (logs), CSV (relatório).
5. **Video curto (até 5 minutos):**

> *“Prepare um vídeo curto (até 5 minutos) para mostrar a funcionalidade do seu sistema de casa inteligente. Explique e destaque as principais funcionalidades, os padrões de projeto utilizados e como as técnicas de programação vistas em sala foram aplicadas (FSM com transitions, descritores, exceptions, JSON/CSV, programação funcional).”*