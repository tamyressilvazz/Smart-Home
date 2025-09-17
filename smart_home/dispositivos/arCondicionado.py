from smart_home.core.dispositivos import Dispositivo, TipoDispositivo, ValidarInteiro, ValidarEnum
from smart_home.core.erros import TransicaoInvalida
from transitions import Machine

from smart_home.core.eventos import EventoDispositivo

class ArCondicionado:
    def __init__(self, id_dispositivo: str, temperatura: int = 24, ligado: bool = False, modo: str = "frio"):
        self.id_dispositivo = id_dispositivo
        self.temperatura = temperatura
        self.ligado = ligado
        self.modo = modo

    def ligar(self):
        if not self.ligado:
            evento = EventoDispositivo(
                id_dispositivo=self.id_dispositivo,
                comando="ligar",
                estado_origem="desligado",
                estado_destino="ligado",
                args={"temperatura": self.temperatura, "modo": self.modo}
            )
            self.ligado = True
            return evento

    def desligar(self):
        if self.ligado:
            evento = EventoDispositivo(
                id_dispositivo=self.id_dispositivo,
                comando="desligar",
                estado_origem="ligado",
                estado_destino="desligado",
                args={"temperatura": self.temperatura, "modo": self.modo}
            )
            self.ligado = False
            return evento

    def alterar_temperatura(self, nova_temp: int):
        evento = EventoDispositivo(
            id_dispositivo=self.id_dispositivo,
            comando="alterar_temperatura",
            estado_origem=f"{self.temperatura}°C",
            estado_destino=f"{nova_temp}°C",
            args={"modo": self.modo}
        )
        self.temperatura = nova_temp
        return evento

    def alterar_modo(self, novo_modo: str):
        evento = EventoDispositivo(
            id_dispositivo=self.id_dispositivo,
            comando="alterar_modo",
            estado_origem=self.modo,
            estado_destino=novo_modo,
            args={"temperatura": self.temperatura}
        )
        self.modo = novo_modo
        return evento