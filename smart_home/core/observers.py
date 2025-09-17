
from abc import ABC, abstractmethod
from smart_home.core.eventos import Evento, EventoDispositivo, EventoHub
import json

class Observer(ABC):
    @abstractmethod
    def update(self, event: Evento):
        pass

class ConsoleObserver(Observer):
    def update(self, event: Evento):
        if isinstance(event, EventoDispositivo):
            print(f"[EVENTO] Dispositivo: {event.id_dispositivo} | Comando: {event.comando} | De: {event.estado_origem} | Para: {event.estado_destino} | Args: {event.args}")
        elif isinstance(event, EventoHub):
            print(f"[EVENTO] Hub: {event.tipo} | Dados: {event.detalhes}") # Corrigido para usar event.detalhes
        else:
            print(f"[EVENTO] Generico: {event.tipo} | Dados: {event.dados}")

class FileObserver(Observer):
    def __init__(self, filename: str):
        self.filename = filename

    def update(self, event: Evento):
        with open(self.filename, 'a') as f:
            # Formato JSON para facilitar a leitura e parsing
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "tipo": event.tipo,
                "dados": event.dados
            }
            f.write(json.dumps(log_entry) + '\n')
