from datetime import datetime
from smart_home.core.dispositivos import TipoDispositivo, Dispositivo
from smart_home.core.logger import Logger
from smart_home.core.eventos import EventoDispositivo, EventoHub
from smart_home.core.observers import ConsoleObserver, FileObserver
from smart_home.core.erros import TransicaoInvalida, ValidacaoAtributo, ConfigInvalida

from smart_home.dispositivos import ArCondicionado
from smart_home.dispositivos.caixaSom import CaixaSom
from smart_home.dispositivos.luz import Luz
from smart_home.dispositivos.porta import Porta
from smart_home.dispositivos.termostato import Termostato
from smart_home.dispositivos.tomada import Tomada

from collections import Counter # Adicionado para gerar relatórios

class SmartHomeHub:
    def __init__(self):
        self.dispositivos = {}
        self.rotinas = {}
        self.logger = Logger() # Singleton
        self.observers = [ConsoleObserver(), FileObserver('data/eventos.log.csv')] 

    def _notificar_observadores(self, evento):
        for observer in self.observers:
            observer.update(evento)

    def adicionar_dispositivo(self, dev_id: str, tipo: TipoDispositivo, nome: str, atributos: dict = None):
        if dev_id in self.dispositivos:
            raise ValueError(f"Dispositivo com ID '{dev_id}' ja existe.")

        device = None
        if tipo == TipoDispositivo.PORTA:
            device = Porta(dev_id, nome)
        elif tipo == TipoDispositivo.LUZ:
            device = Luz(dev_id, nome)
        elif tipo == TipoDispositivo.TOMADA:
            device = Tomada(dev_id, nome)
        
        elif tipo == TipoDispositivo.TERMOSTATO:
            device = Termostato(dev_id, nome)
        elif tipo == TipoDispositivo.AR_CONDICIONADO:
            device = ArCondicionado(dev_id, nome) 
        elif tipo == TipoDispositivo.CAIXA_SOM:
            device = CaixaSom(dev_id, nome)
        else:
            raise ValueError(f"Tipo de dispositivo '{tipo.name}' nao suportado.")

        # Aplicar atributos iniciais, se houver
        if atributos:
            for attr, value in atributos.items():
                try:
                    setattr(device, attr, value)
                except ValidacaoAtributo as e:
                    raise ValidacaoAtributo(f"Erro ao definir atributo '{attr}' para {dev_id}: {e}")
                except AttributeError:
                    print(f"Aviso: Atributo '{attr}' nao existe para o dispositivo '{tipo.name}'.")

        self.dispositivos[dev_id] = device
        self._notificar_observadores(EventoHub(f"DispositivoAdicionado", {'id': dev_id, 'tipo': tipo.name}))
        self.logger.log_event(dev_id, "adicionado", "N/A", device.estado if device.estado else "N/A") # Estado pode ser None inicialmente


    def remover_dispositivo(self, dev_id: str):
        if dev_id not in self.dispositivos:
            raise ValueError(f"Dispositivo com ID '{dev_id}' nao encontrado.")
        device = self.dispositivos.pop(dev_id)
        self._notificar_observadores(EventoHub(f"DispositivoRemovido", {'id': dev_id, 'tipo': device.tipo.name}))
        self.logger.log_event(dev_id, "removido", device.estado if device.estado else "N/A", "N/A")

    def obter_dispositivo(self, dev_id: str) -> Dispositivo:
        return self.dispositivos.get(dev_id)

    def executar_comando(self, dev_id: str, comando: str, **kwargs):
        device = self.obter_dispositivo(dev_id)
        if not device:
            raise ValueError(f"Dispositivo com ID '{dev_id}' nao encontrado.")

        estado_anterior = device.estado
        try:
            # Tenta chamar o método correspondente ao comando no dispositivo
            method = getattr(device, comando)
            method(**kwargs)
            self._notificar_observadores(EventoDispositivo(
                dev_id, comando, estado_anterior, device.estado, args=kwargs # Passar kwargs como args
            ))
            self.logger.log_event(dev_id, comando, estado_anterior, device.estado)
        except AttributeError:
            raise AttributeError(f"Comando '{comando}' nao disponivel para o dispositivo '{dev_id}'.")
        except TransicaoInvalida as e:
            self.logger.log_event(dev_id, comando, estado_anterior, device.estado, sucesso=False, erro=str(e))
            raise TransicaoInvalida(f"Falha ao executar comando '{comando}' em '{dev_id}': {e}")
        except Exception as e:
            self.logger.log_event(dev_id, comando, estado_anterior, device.estado, sucesso=False, erro=str(e))
            raise Exception(f"Erro inesperado ao executar comando '{comando}' em '{dev_id}': {e}")

    def executar_rotina(self, rotina_nome: str):
        if rotina_nome not in self.rotinas:
            raise ValueError(f"Rotina '{rotina_nome}' nao encontrada.")

        print(f"Executando rotina: {rotina_nome}")
        self._notificar_observadores(EventoHub(f"RotinaIniciada", {'nome': rotina_nome}))

        for acao in self.rotinas[rotina_nome]:
            dev_id = acao['id']
            comando = acao['comando']
            argumentos = acao.get('argumentos', {})
            try:
                self.executar_comando(dev_id, comando, **argumentos)
                print(f"  - Executado: {comando} em {dev_id}")
            except Exception as e:
                print(f"  - Falha ao executar {comando} em {dev_id}: {e}")
                # Decide se a rotina deve parar ou continuar em caso de erro

        self._notificar_observadores(EventoHub(f"RotinaFinalizada", {'nome': rotina_nome}))

    def carregar_configuracao(self, config: dict):
        self.dispositivos = {}
        self.rotinas = {}

        if 'dispositivos' in config:
            for dev_data in config['dispositivos']:
                try:
                    dev_id = dev_data['id']
                    tipo = TipoDispositivo[dev_data['tipo']]
                    nome = dev_data['nome']
                    estado_inicial = dev_data.get('estado')
                    atributos = dev_data.get('atributos', {})
                    self.adicionar_dispositivo(dev_id, tipo, nome, atributos)
                    # Se houver estado inicial, tentar aplicá-lo
                    if estado_inicial and self.dispositivos[dev_id].estado != estado_inicial:
                        try:
                            # A máquina de estados precisa ser configurada antes de setar o estado
                            if self.dispositivos[dev_id].machine:
                                self.dispositivos[dev_id].machine.set_state(estado_inicial)
                            else:
                                print(f"Aviso: Máquina de estados não configurada para {dev_id}. Não foi possível definir o estado inicial.")
                        except Exception as e:
                            print(f"Aviso: Nao foi possivel definir estado inicial '{estado_inicial}' para {dev_id}: {e}")
                except KeyError as e:
                    raise ConfigInvalida(f"Configuracao de dispositivo invalida: faltando chave {e} em {dev_data}")
                except ValueError as e:
                    raise ConfigInvalida(f"Configuracao de dispositivo invalida: {e} em {dev_data}")
                except ValidacaoAtributo as e:
                    raise ConfigInvalida(f"Erro de validacao de atributo ao carregar dispositivo {dev_id}: {e}")

        if 'rotinas' in config:
            self.rotinas = config['rotinas']

    def obter_configuracao(self) -> dict:
        dispositivos_config = []
        for dev_id, device in self.dispositivos.items():
            dev_data = {
                "id": dev_id,
                "tipo": device.tipo.name,
                "nome": device.nome,
                "estado": device.estado,
                "atributos": {}
            }
            # Coletar atributos específicos que devem ser persistidos
            if isinstance(device, Luz):
                dev_data["atributos"]["brilho"] = device.brilho
                dev_data["atributos"]["cor"] = device.cor.name
            elif isinstance(device, Tomada):
                dev_data["atributos"]["potencia_w"] = device.potencia_w
                # O consumo_wh é uma métrica, não um atributo de configuração
            elif isinstance(device, Porta):
                # Porta não tem atributos adicionais para persistir além do estado
                pass
            elif isinstance(device, Termostato):
                dev_data["atributos"]["temperatura"] = device.temperatura
                dev_data["atributos"]["modo"] = device.modo.name
            elif isinstance(device, ArCondicionado):
                dev_data["atributos"]["temperatura"] = device.temperatura
                dev_data["atributos"]["ligado"] = device.ligado
                dev_data["atributos"]["modo"] = device.modo.name
            elif isinstance(device, CaixaSom):
                dev_data["atributos"]["volume"] = device.volume

            dispositivos_config.append(dev_data)

        return {
            "hub": {"nome": "Casa Exemplo", "versao": "1.0"},
            "dispositivos": dispositivos_config,
            "rotinas": self.rotinas
        }

    # --- Implementação dos Relatórios ---

    def gerar_relatorio_consumo_tomadas(self):
        events = self.logger.read_events()
        consumo_por_tomada = {}

        for event in events:
            if event['id_dispositivo'] in self.dispositivos and self.dispositivos[event['id_dispositivo']].tipo == TipoDispositivo.TOMADA:
                if event['evento'] == 'ligar' and event['sucesso'] == 'True':
                    # Registra o timestamp de ligar
                    self.dispositivos[event['id_dispositivo']]._tempo_ligada_inicio = datetime.datetime.fromisoformat(event['timestamp'])
                elif event['evento'] == 'desligar' and event['sucesso'] == 'True':
                    # Calcula o consumo se a tomada estava ligada
                    tomada = self.dispositivos[event['id_dispositivo']]
                    if tomada._tempo_ligada_inicio:
                        tempo_ligada_fim = datetime.datetime.fromisoformat(event['timestamp'])
                        duracao_segundos = (tempo_ligada_fim - tomada._tempo_ligada_inicio).total_seconds()
                        duracao_horas = duracao_segundos / 3600
                        consumo_periodo = tomada.potencia_w * duracao_horas
                        consumo_por_tomada.setdefault(tomada.id, 0.0)
                        consumo_por_tomada[tomada.id] += consumo_periodo
                        tomada._tempo_ligada_inicio = None # Reseta

        relatorio = []
        for dev_id, total_wh in consumo_por_tomada.items():
            relatorio.append({
                'id_dispositivo': dev_id,
                'total_wh': total_wh
            })
        return relatorio

    def gerar_relatorio_tempo_luz_ligada(self):
        events = self.logger.read_events()
        tempo_ligado_por_luz = {} # {id_luz: {'start_time': datetime, 'total_seconds': 0}}

        for event in events:
            if event['id_dispositivo'] in self.dispositivos and self.dispositivos[event['id_dispositivo']].tipo == TipoDispositivo.LUZ:
                dev_id = event['id_dispositivo']
                timestamp = datetime.datetime.fromisoformat(event['timestamp'])

                if dev_id not in tempo_ligado_por_luz:
                    tempo_ligado_por_luz[dev_id] = {'start_time': None, 'total_seconds': 0.0}

                if event['evento'] == 'ligar' and event['sucesso'] == 'True':
                    tempo_ligado_por_luz[dev_id]['start_time'] = timestamp
                elif event['evento'] == 'desligar' and event['sucesso'] == 'True':
                    if tempo_ligado_por_luz[dev_id]['start_time']:
                        duration = (timestamp - tempo_ligado_por_luz[dev_id]['start_time']).total_seconds()
                        tempo_ligado_por_luz[dev_id]['total_seconds'] += duration
                        tempo_ligado_por_luz[dev_id]['start_time'] = None # Resetar para o próximo ciclo

        relatorio = []
        for dev_id, data in tempo_ligado_por_luz.items():
            # Se a luz ainda estiver ligada no final dos logs, adiciona o tempo até agora
            if data['start_time']:
                duration = (datetime.datetime.now() - data['start_time']).total_seconds()
                data['total_seconds'] += duration
            
            relatorio.append({
                'id_dispositivo': dev_id,
                'tempo_total_horas': data['total_seconds'] / 3600
            })
        return relatorio

    def gerar_relatorio_temperatura_media_termostato(self):
        termostatos = [d for d in self.dispositivos.values() if d.tipo == TipoDispositivo.TERMOSTATO]
        temperaturas = list(map(lambda t: t.temperatura, termostatos))
        if temperaturas:
            media = sum(temperaturas) / len(temperaturas)
            return {"temperatura_media": media}
        return {"temperatura_media": None}

    def gerar_relatorio_tempo_tocando_caixa_som(self):
        events = self.logger.read_events()
        tempo_tocando_por_caixa = {} # {id_caixa: {'start_time': datetime, 'total_seconds': 0}}

        for event in events:
            if event['id_dispositivo'] in self.dispositivos and self.dispositivos[event['id_dispositivo']].tipo == TipoDispositivo.CAIXA_SOM:
                dev_id = event['id_dispositivo']
                timestamp = datetime.datetime.fromisoformat(event['timestamp'])

                if dev_id not in tempo_tocando_por_caixa:
                    tempo_tocando_por_caixa[dev_id] = {'start_time': None, 'total_seconds': 0.0}

                if event['evento'] == 'tocar' and event['sucesso'] == 'True':
                    tempo_tocando_por_caixa[dev_id]['start_time'] = timestamp
                elif event['evento'] == 'parar' and event['sucesso'] == 'True':
                    if tempo_tocando_por_caixa[dev_id]['start_time']:
                        duration = (timestamp - tempo_tocando_por_caixa[dev_id]['start_time']).total_seconds()
                        tempo_tocando_por_caixa[dev_id]['total_seconds'] += duration
                        tempo_tocando_por_caixa[dev_id]['start_time'] = None # Resetar

        relatorio = []
        for dev_id, data in tempo_tocando_por_caixa.items():
            if data['start_time']: # Se ainda estiver tocando
                duration = (datetime.datetime.now() - data['start_time']).total_seconds()
                data['total_seconds'] += duration
            relatorio.append({
                'id_dispositivo': dev_id,
                'tempo_total_segundos': data['total_seconds']
            })
        return relatorio

    def gerar_relatorio_modos_ar_condicionado(self):
        events = self.logger.read_events()
        modos_ar_condicionado = []
        for event in events:
            if event['id_dispositivo'] in self.dispositivos and self.dispositivos[event['id_dispositivo']].tipo == TipoDispositivo.AR_CONDICIONADO:
                if event['evento'] == 'alterar_modo' and event['sucesso'] == 'True':
                    # O estado_destino do evento 'alterar_modo' contém o novo modo
                    modos_ar_condicionado.append(event['estado_destino'])
        
        contagem = Counter(modos_ar_condicionado)
        return dict(contagem)
    
    def gerar_relatorio_dispositivos_mais_usados(self):
        events = self.logger.read_events()
        event_counts = {}

        for event in events:
            dev_id = event['id_dispositivo']
            if dev_id in self.dispositivos: # Garante que o dispositivo ainda existe
                event_counts.setdefault(dev_id, 0)
                event_counts[dev_id] += 1

        sorted_devices = sorted(event_counts.items(), key=lambda item: item[1], reverse=True)
        return [{'id_dispositivo': dev_id, 'num_eventos': count} for dev_id, count in sorted_devices]
