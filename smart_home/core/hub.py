from smart_home.core.dispositivos import TipoDispositivo, Dispositivo
from smart_home.dispositivos.porta import Porta
from smart_home.dispositivos.luz import Luz
from smart_home.dispositivos.tomada import Tomada
# Importe os outros dispositivos que você criar aqui
from smart_home.core.logger import Logger
from smart_home.core.eventos import EventoDispositivo, EventoHub
from smart_home.core.observers import ConsoleObserver, FileObserver
from smart_home.core.erros import TransicaoInvalida, ValidacaoAtributo, ConfigInvalida
import datetime

class SmartHomeHub:
    def __init__(self):
        self.dispositivos = {}
        self.rotinas = {}
        self.logger = Logger() # Singleton
        self.observers = [ConsoleObserver(), FileObserver('data/eventos.log')] # Exemplo de observers

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
        # Adicione a lógica para instanciar outros tipos de dispositivos aqui
        # elif tipo == TipoDispositivo.CAFETEIRA:
        #     device = Cafeteira(dev_id, nome)
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
        self.logger.log_event(dev_id, "adicionado", "N/A", device.estado)


    def remover_dispositivo(self, dev_id: str):
        if dev_id not in self.dispositivos:
            raise ValueError(f"Dispositivo com ID '{dev_id}' nao encontrado.")
        device = self.dispositivos.pop(dev_id)
        self._notificar_observadores(EventoHub(f"DispositivoRemovido", {'id': dev_id, 'tipo': device.tipo.name}))
        self.logger.log_event(dev_id, "removido", device.estado, "N/A")

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
                dev_id, comando, estado_anterior, device.estado, **kwargs
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
                            self.dispositivos[dev_id].machine.set_state(estado_inicial)
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
            # Adicione a lógica para coletar atributos de outros dispositivos aqui

            dispositivos_config.append(dev_data)

        return {
            "hub": {"nome": "Casa Exemplo", "versao": "1.0"},
            "dispositivos": dispositivos_config,
            "rotinas": self.rotinas
        }

    # --- Implementação dos Relatórios (Programação Funcional) ---

    def gerar_relatorio_consumo_tomadas(self):
        # Este relatório precisará ler os logs de eventos para calcular o consumo
        # Por enquanto, um placeholder. A lógica real virá em persistencia.py ou logger.py
        # e usará map/filter/reduce sobre os dados do CSV.
        tomadas = filter(lambda d: d.tipo == TipoDispositivo.TOMADA, self.dispositivos.values())
        relatorio = []
        for tomada in tomadas:
            # Lógica para calcular consumo real a partir dos logs
            # Por simplicidade, aqui apenas retorna o consumo atual (que é acumulado)
            relatorio.append({
                'id_dispositivo': tomada.id,
                'total_wh': tomada.consumo_wh # Isso é um placeholder, precisa ser calculado dos logs
            })
        return relatorio

    def gerar_relatorio_tempo_luz_ligada(self):
        luzes = filter(lambda d: d.tipo == TipoDispositivo.LUZ, self.dispositivos.values())
        relatorio = []
        for luz in luzes:
            # calcular tempo ligada a partir dos logs
            relatorio.append({
                'id_dispositivo': luz.id,
                'tempo_total_horas': 0.0 
            })
        return relatorio

    def gerar_relatorio_dispositivos_mais_usados(self):
        event_counts = {} # {dev_id: count}

        for dev_id in self.dispositivos.keys():
            event_counts[dev_id] = 0 # Substituir por contagem real dos logs

        # Exemplo de uso de sorted com lambda
        sorted_devices = sorted(event_counts.items(), key=lambda item: item[1], reverse=True)
        return [{'id_dispositivo': dev_id, 'num_eventos': count} for dev_id, count in sorted_devices]

    # relatorio adicional