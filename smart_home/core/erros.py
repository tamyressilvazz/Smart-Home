 # exceções personalizadas
class SmartHomeError(Exception):
    """Classe base para todas as exceções"""
    pass

class TransicaoInvalida(SmartHomeError):
    """Exceção levantada quando uma transição de estado é inválida."""
    pass

class ConfigInvalida(SmartHomeError):
    """Exceção levantada quando a configuração carregada é inválida."""
    pass

class ValidacaoAtributo(SmartHomeError):
    """Exceção levantada quando a validação de um atributo falha."""
    pass