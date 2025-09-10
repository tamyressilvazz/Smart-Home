# tipos de eventos do hub
import datetime
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class Evento:
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    tipo: str
    dados: Dict[str, Any]

@dataclass
class EventoDispositivo(Evento):
    id_dispositivo: str
    comando: str
    estado_origem: str
    estado_destino: str

    args: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.tipo = "Dispositivo"
        self.dados = {
            "id_dispositivo": self.id_dispositivo,
            "comando": self.comando,
            "estado_origem": self.estado_origem,
            "estado_destino": self.estado_destino,
            "args": self.args
        }

@dataclass
class EventoHub(Evento):
    # Eventos adicionar/remover dispositivo, executar rotina
    def __post_init__(self):
        pass

