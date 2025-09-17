
from abc import ABC, abstractmethod
from enum import Enum
from transitions import Machine
from .erros import ValidacaoAtributo

# Enum para tipos de dispositivos
class TipoDispositivo(Enum):
    PORTA = "PORTA"
    LUZ = "LUZ"
    TOMADA = "TOMADA"
    CAIXA_SOM = "CAIXA_SOM"
    TERMOSTATO = "TERMOSTATO"
    AR_CONDICIONADO = "AR_CONDICIONADO"

# Descritor - validação de atributos
class ValidarInteiro:
    def __init__(self, min_val=None, max_val=None):
        self.min_val = min_val
        self.max_val = max_val
        self.name = None 

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise ValidacaoAtributo(f"O atributo '{self.name}' deve ser um numero inteiro.")
        if self.min_val is not None and value < self.min_val:
            raise ValidacaoAtributo(f"O atributo '{self.name}' deve ser maior ou igual a {self.min_val}.")
        if self.max_val is not None and value > self.max_val:
            raise ValidacaoAtributo(f"O atributo '{self.name}' deve ser menor ou igual a {self.max_val}.")
        instance.__dict__[self.name] = value

class ValidarEnum:
    def __init__(self, enum_class):
        self.enum_class = enum_class
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if isinstance(value, self.enum_class):
            instance.__dict__[self.name] = value
        elif isinstance(value, str):
            try:
                instance.__dict__[self.name] = self.enum_class[value.upper()]
            except KeyError:
                raise ValidacaoAtributo(f"Valor '{value}' invalido para o atributo '{self.name}'. Valores permitidos: {[e.name for e in self.enum_class]}.")
        else:
            raise ValidacaoAtributo(f"O atributo '{self.name}' deve ser um membro de {self.enum_class.__name__} ou uma string correspondente.")


# Classe base abstrata para todos os dispositivos
class Dispositivo(ABC):
    def __init__(self, id: str, nome: str, tipo: TipoDispositivo):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.estado = None 
        self.machine = None 

    @abstractmethod
    def _setup_fsm(self):
        """Configura a máquina de estados para o dispositivo."""
        pass

    def __repr__(self):
        return f"{self.tipo.name}(id='{self.id}', nome='{self.nome}', estado='{self.estado}')"

    def on_enter_state(self, event):
        """Callback genérico para quando um estado é entrado."""
        print(f"[{self.id}] Entrou no estado: {self.estado}")


    def on_exit_state(self, event):
        """Callback genérico para quando um estado é saído."""
        print(f"[{self.id}] Saiu do estado: {event.state.name}")


    # Propriedade para acessar o estado da FSM
    @property
    def estado(self):
        return self._estado

    @estado.setter
    def estado(self, value):
        self._estado = value

