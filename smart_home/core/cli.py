import argparse
from smart_home.core.hub import SmartHomeHub
from smart_home.core.persistencia import Persistencia
from smart_home.core.erros import TransicaoInvalida, ValidacaoAtributo, ConfigInvalida
from smart_home.core.dispositivos import TipoDispositivo #enums de tipo de dispositivo

