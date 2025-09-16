from smart_home.core.dispositivos import Dispositivo, TipoDispositivo, ValidarInteiro, ValidarEnum
from smart_home.core.erros import TransicaoInvalida
from transitions import Machine
from enum import Enum

class ModoTermostato(Enum):
    REFRIGERACAO = "REFRIGERACAO"
    AQUECIMENTO = "AQUECIMENTO"
    DESATIVADO = "DESATIVADO"

class Termostato(Dispositivo):
    temperatura = ValidarInteiro(min_val=-20, max_val=40)
    modo = ValidarEnum(ModoTermostato)

    def __init__(self, id: str, nome: str):
        super().__init__(id, nome, TipoDispositivo.TERMOSTATO)
        self._temperatura = 20 # Valor padrão antes da validação
        self._modo = ModoTermostato.DESATIVADO # Valor padrão antes da validação
        self._setup_fsm()
        # Definir valores iniciais após a FSM ser configurada e descritores estarem prontos
        self.temperatura = 20
        self.modo = ModoTermostato.DESATIVADO

    def _setup_fsm(self):
        states = ['desativado', 'refrigeracao', 'aquecimento']
        transitions = [
            {'trigger': 'ativar_refrigeracao', 'source': 'desativado', 'dest': 'refrigeracao'},
            {'trigger': 'ativar_aquecimento', 'source': 'desativado', 'dest': 'aquecimento'},
            {'trigger': 'desativar', 'source': ['refrigeracao', 'aquecimento'], 'dest': 'desativado'},
            {'trigger': 'alternar_modo', 'source': 'refrigeracao', 'dest': 'aquecimento'},
            {'trigger': 'alternar_modo', 'source': 'aquecimento', 'dest': 'refrigeracao'}
        ]
        self.machine = Machine(model=self, states=states, initial='desativado', transitions=transitions,
                               after='on_enter_state', before='on_exit_state')


    def ativar_refrigeracao(self):
        try:
            self.machine.ativar_refrigeracao()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao ativar refrigeracao: {e}")

    def ativar_aquecimento(self):
        try:
            self.machine.ativar_aquecimento()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao ativar aquecimento: {e}")

    def desativar(self):
        try:
            self.machine.desativar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao desativar termostato: {e}")

    def alternar_modo(self):
        try:
            self.machine.alternar_modo()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao alternar modo: {e}")

    def definir_temperatura(self, temperatura: int):
        if self.estado == 'desativado':
            raise TransicaoInvalida("Nao e possivel definir temperatura com o termostato desativado.")
        try:
            self.temperatura = temperatura # A validação ocorre via descritor
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao definir temperatura: {e}")

# Exemplo de uso (para testes rápidos)
if __name__ == '__main__':
    termostato = Termostato("termostato_sala", "Termostato da Sala")
    print(f"Estado inicial: {termostato.estado}, Modo: {termostato.modo.name}, Temperatura: {termostato.temperatura}°C")

    termostato.ativar_refrigeracao()
    print(f"Estado apos ativar refrigeracao: {termostato.estado}")

    termostato.definir_temperatura(22)
    print(f"Temperatura definida: {termostato.temperatura}°C")

    termostato.alternar_modo()
    print(f"Estado apos alternar modo: {termostato.estado}")

    termostato.desativar()
    print(f"Estado apos desativar: {termostato.estado}")
