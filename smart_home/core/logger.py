# Singleton para logging em CSV
import csv
import datetime
import os
from threading import Lock

class Logger:
    _instance = None
    _lock = Lock()

    def __new__(cls, filename='data/eventos.csv'):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.filename = filename
                cls._instance._initialize_csv()
            return cls._instance

    def _initialize_csv(self):
        # Cria o arquivo CSV com cabeçalho se ele não existir
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'id_dispositivo', 'evento', 'estado_origem', 'estado_destino', 'sucesso', 'erro'])

    def log_event(self, id_dispositivo: str, evento: str, estado_origem: str, estado_destino: str, sucesso: bool = True, erro: str = ""):
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')
        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, id_dispositivo, evento, estado_origem, estado_destino, sucesso, erro])

    def read_events(self):
        """Lê todos os eventos do arquivo CSV."""
        events = []
        if not os.path.exists(self.filename):
            return events
        with open(self.filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(row)
        return events

# testes
if __name__ == '__main__':
    logger1 = Logger('data/test_events.csv')
    logger2 = Logger('data/test_events.csv')

    print(f"Logger 1 is Logger 2: {logger1 is logger2}")

    logger1.log_event("luz_sala", "ligar", "off", "on")
    logger2.log_event("porta_entrada", "abrir", "destrancada", "aberta", sucesso=False, erro="Porta travada")

    print("\nEventos registrados:")
    for event in logger1.read_events():
        print(event)
