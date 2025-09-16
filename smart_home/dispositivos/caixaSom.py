
from transitions import Machine
from core import Dispositivo, TipoDispositivo, ValidarInteiro
from smart_home.core.erros import TransicaoInvalida


class CaixaSom(Dispositivo):
    volume = ValidarInteiro(min_val=0, max_val=100)

    def __init__(self, id: str, nome: str):
        super().__init__(id, nome, TipoDispositivo.CAIXA_SOM)  # Corrigir TipoDispositivo abaixo
        self._volume = 50  # Valor padrão antes da validação
        self._setup_fsm()
        self.volume = 50

    def _setup_fsm(self):
        states = ['desligado', 'ligado', 'tocando']
        transitions = [
            {'trigger': 'ligar', 'source': 'desligado', 'dest': 'ligado'},
            {'trigger': 'desligar', 'source': ['ligado', 'tocando'], 'dest': 'desligado'},
            {'trigger': 'tocar', 'source': 'ligado', 'dest': 'tocando'},
            {'trigger': 'parar', 'source': 'tocando', 'dest': 'ligado'},
            {'trigger': 'aumentar_volume', 'source': ['ligado', 'tocando'], 'dest': None, 'after': 'incrementar_volume'},
            {'trigger': 'diminuir_volume', 'source': ['ligado', 'tocando'], 'dest': None, 'after': 'decrementar_volume'}
        ]
        self.machine = Machine(model=self, states=states, initial='desligado', transitions=transitions,
                               after_transition='on_enter_state', before_transition='on_exit_state')

    # Métodos de comando: ligar/desligar/tocar/parar/...
    def ligar(self):
        try:
            self.machine.ligar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao ligar caixa de som: {e}")

    def desligar(self):
        try:
            self.machine.desligar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao desligar caixa de som: {e}")

    def tocar(self):
        try:
            self.machine.tocar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao iniciar reprodução: {e}")

    def parar(self):
        try:
            self.machine.parar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao parar reprodução: {e}")

    def aumentar_volume(self):
        try:
            self.machine.aumentar_volume()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao aumentar volume: {e}")

    def diminuir_volume(self):
        try:
            self.machine.diminuir_volume()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao diminuir volume: {e}")

    #  ajustar volume
    def incrementar_volume(self):
        if self.volume < 100:
            self.volume += 5
            if self.volume > 100:
                self.volume = 100

    def decrementar_volume(self):
        if self.volume > 0:
            self.volume -= 5
            if self.volume < 0:
                self.volume = 0

#teste
if __name__ == '__main__':
    caixa = CaixaSom("caixa_sala", "Caixa de Som da Sala")
    print(f"Estado inicial: {caixa.estado}, Volume: {caixa.volume}")

    caixa.ligar()
    print(f"Estado apos ligar: {caixa.estado}")

    caixa.tocar()
    print(f"Estado apos tocar: {caixa.estado}")

    caixa.aumentar_volume()
    print(f"Volume apos aumentar: {caixa.volume}")

    caixa.diminuir_volume()
    print(f"Volume apos diminuir: {caixa.volume}")

    caixa.parar()
    print(f"Estado apos parar: {caixa.estado}")

    caixa.desligar()
    print(f"Estado apos desligar: {caixa.estado}")
