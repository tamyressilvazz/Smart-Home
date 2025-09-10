from smart_home.core.dispositivos import Dispositivo, TipoDispositivo, ValidarInteiro
from smart_home.core.erros import TransicaoInvalida
from transitions import Machine
import datetime, time

class Tomada(Dispositivo):
    potencia_w = ValidarInteiro(min_val=0)
    def __init__(self, id: str, nome: str):
        super().__init__(id, nome, TipoDispositivo.TOMADA)
        self._potencia_w = 0 # Valor padrão antes da validação
        self.consumo_wh = 0.0
        self._tempo_ligada_inicio = None # Para calcular o consumo
        self._setup_fsm()
        self.potencia_w = 0 # Define o valor inicial via descritor

    def _setup_fsm(self):
        estados = ['off', 'on']
        transicoes = [
            {'trigger': 'ligar', 'source': 'off', 'dest': 'on', 'after': 'on_ligar'},
            {'trigger': 'desligar', 'source': 'on', 'dest': 'off', 'after': 'on_desligar'}
        ]
        self.machine = Machine(model=self, states=estados, initial='off', transitions=transicoes,
                               after_transition='on_enter_state', before_transition='on_exit_state')
        
    def on_ligar(self):
        """Registra o tempo de início quando a tomada é ligada."""
        self._tempo_ligada_inicio = datetime.datetime.now()

    def on_desligar(self):
        """Calcula o consumo quando a tomada é desligada."""
        if self._tempo_ligada_inicio:
            tempo_ligada_fim = datetime.datetime.now()
            duracao_segundos = (tempo_ligada_fim - self._tempo_ligada_inicio).total_seconds()
            duracao_horas = duracao_segundos / 3600
            consumo_periodo = self.potencia_w * duracao_horas
            self.consumo_wh += consumo_periodo
            self._tempo_ligada_inicio = None # Reseta para o próximo ciclo

    # Métodos ligar/desligar
    def ligar(self):
        try:
            self.machine.ligar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao ligar tomada: {e}")
    def desligar(self):
        try:
            self.machine.desligar()
        except Exception as e:
            raise TransicaoInvalida(f"Falha ao desligar tomada: {e}")

#teste
if __name__ == '__main__':

    tomada = Tomada("tomada_geladeira", "Tomada da Geladeira")
    print(f"Estado inicial: {tomada.estado}, Potencia: {tomada.potencia_w}W, Consumo: {tomada.consumo_wh}Wh")
    
    tomada.potencia_w = 100 # Define a potência da geladeira
    print(f"Potencia definida: {tomada.potencia_w}W")
    
    tomada.ligar()
    print(f"Estado apos ligar: {tomada.estado}")
    print("Aguardando 2 segundos para simular uso...")
    time.sleep(2) # 2 segundos de uso

    tomada.desligar()
    print(f"Estado apos desligar: {tomada.estado}")
    print(f"Consumo acumulado: {tomada.consumo_wh:.4f}Wh") # Deve ser aproximadamente 100W * (2/3600)h

    # Ligar novamente para acumular mais consumo
    tomada.ligar()
    print(f"Estado apos ligar novamente: {tomada.estado}")
    time.sleep(1) # 1 segundo de uso
    tomada.desligar()
    print(f"Consumo acumulado final: {tomada.consumo_wh:.4f}Wh")