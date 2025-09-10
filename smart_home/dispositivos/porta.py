from smart_home.core.dispositivos import Dispositivo, TipoDispositivo
from smart_home.core.erros import TransicaoInvalida
from transitions import Machine

#Porta herda de dispostivo
class Porta(Dispositivo):
    def __init__(self, id: str, nome: str):
        super().__init__(id, nome, TipoDispositivo.PORTA)
        self.tentativas_invalidas = 0
        self._setup_fsm()

    def _setup_fsm(self):
        estados = ['trancada', 'destrancada', 'aberta']

        transitions = [
            {'trigger': 'destrancar', 'source': 'trancada', 'dest': 'destrancada'},
            {'trigger': 'trancar', 'source': 'destrancada', 'dest': 'trancada', 'before': 'check_if_closed'},
            {'trigger': 'abrir', 'source': 'destrancada', 'dest': 'aberta'},
            {'trigger': 'fechar', 'source': 'aberta', 'dest': 'destrancada'}
        ]

        self.machine = Machine(model=self, states=estados, initial='trancada', transitions=transitions,
                               after_transition='on_enter_state', before_transition='on_exit_state')
        
    def check_if_closed(self):
        """Verifica se a porta está fechada antes de trancar."""
        if self.estado == 'aberta':
            self.tentativas_invalidas += 1
            raise TransicaoInvalida("Nao e permitido trancar a porta se ela esta aberta.")
        return True # Permite a transição se não estiver aberta
    
    # Métodos destrancar/trancar/abrir/fechar
    def destrancar(self):
        try:
            self.machine.destrancar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao destrancar porta: {e}")
        
    def trancar(self):
        try:
            self.machine.trancar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao trancar porta: {e}")
        
    def abrir(self):
        try:
            self.machine.abrir()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao abrir porta: {e}")
        
    def fechar(self):
        try:
            self.machine.fechar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao fechar porta: {e}")



if __name__ == '__main__':
    porta = Porta("porta_principal", "Porta da Frente")
    print(f"Estado inicial: {porta.estado}") # trancada
    porta.destrancar()
    print(f"Estado apos destrancar: {porta.estado}") # destrancada
    porta.abrir()
    print(f"Estado apos abrir: {porta.estado}") # aberta
    try:
        porta.trancar() # Deve falhar
    except TransicaoInvalida as e:
        print(f"Erro ao tentar trancar porta aberta: {e}")
        print(f"Tentativas invalidas: {porta.tentativas_invalidas}") # 1
    porta.fechar()
    print(f"Estado apos fechar: {porta.estado}") # destrancada
    porta.trancar()
    print(f"Estado apos trancar: {porta.estado}") # trancada