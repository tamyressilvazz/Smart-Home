from smart_home.core.dispositivos import Dispositivo, TipoDispositivo, ValidarInteiro, ValidarEnum
from smart_home.core.erros import TransicaoInvalida
from transitions import Machine
from enum import Enum


class CorLuz(Enum):
    QUENTE = "QUENTE"
    FRIA = "FRIA"
    NEUTRA = "NEUTRA"

class Luz(Dispositivo):
    brilho = ValidarInteiro(min_val=0, max_val=100)
    cor = ValidarEnum(CorLuz)

    def __init__(self, id: str, nome: str):
            super().__init__(id, nome, TipoDispositivo.LUZ)
            self._brilho = 0 # Valor padrão antes da validação
            self._cor = CorLuz.NEUTRA # Valor padrão antes da validação
            self._setup_fsm()
            # Definir valores iniciais após a FSM ser configurada e descritores estarem prontos
            self.brilho = 50
            self.cor = CorLuz.NEUTRA

    def _setup_fsm(self):
        estados = ['off', 'on']

        transicoes = [
            {'trigger': 'ligar', 'source': 'off', 'dest': 'on'},
            {'trigger': 'desligar', 'source': 'on', 'dest': 'off'},
            {'trigger': 'definir_brilho', 'source': 'on', 'dest': 'on'}, # Permanece no estado 'on'
            {'trigger': 'definir_cor', 'source': 'on', 'dest': 'on'} # Permanece no estado 'on'
        ]
        self.machine = Machine(model=self, states=estados, initial='off', transitions=transicoes,
                               after_transition='on_enter_state', before_transition='on_exit_state')
    
    # Métodos ligar/desligar/definir_brilho
    def ligar(self):
        try:
            self.machine.ligar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao ligar luz: {e}")
        
    def desligar(self):
        try:
            self.machine.desligar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao desligar luz: {e}")
        
    def definir_brilho(self, brilho: int):
        if self.estado != 'on':
            raise TransicaoInvalida("Nao e possivel definir brilho com a luz desligada.")
        try:
            self.brilho = brilho # A validação ocorre via descritor
            self.machine.definir_brilho() # Dispara a transição para registrar o evento
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao definir brilho: {e}")
        
    def definir_cor(self, cor: str):
        if self.estado != 'on':
            raise TransicaoInvalida("Não e possivel definir cor com a luz desligada.")
        try:
            self.cor = cor # validação com descriptor
            self.machine.definir_cor() # Dispara a transição para registrar o evento
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao definir cor: {e}")
        
#teste
if __name__ == '__main__':
    luz = Luz("luz_quarto", "Luz do Quarto")
    print(f"Estado inicial: {luz.estado}, Brilho: {luz.brilho}, Cor: {luz.cor.name}") # off, 50, NEUTRA
    luz.ligar()
    print(f"Estado apos ligar: {luz.estado}") # on
    luz.definir_brilho(80)
    print(f"Brilho apos definir: {luz.brilho}") # 80

    try:
        luz.definir_brilho(120) 
    except TransicaoInvalida as e:
        print(f"Erro ao definir brilho invalido: {e}")

    luz.definir_cor("FRIA")
    print(f"Cor apos definir: {luz.cor.name}") # FRIA

    try:
        luz.definir_cor("ROXA") 
    except TransicaoInvalida as e:
        print(f"Erro ao definir cor invalida: {e}")

    luz.desligar()
    print(f"Estado apos desligar: {luz.estado}") # off

    try:
        luz.definir_brilho(30) 
    except TransicaoInvalida as e:
        print(f"Erro ao tentar definir brilho com luz desligada: {e}")