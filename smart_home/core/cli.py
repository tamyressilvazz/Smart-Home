import argparse
from smart_home.core.hub import SmartHomeHub
from .persistencia import Persistencia
from .erros import TransicaoInvalida, ValidacaoAtributo, ConfigInvalida
from smart_home.dispositivos import Dispositivo, TipoDispositivo, ValidacaoAtributo
class CLI:
    def __init__(self, config_path):
        self.persistencia = Persistencia(config_path)
        self.hub = SmartHomeHub()
        self._carregar_configuracao()

    def _carregar_configuracao(self):
        try:
            config = self.persistencia.carregar_configuracao()
            self.hub.carregar_configuracao(config)
            print(f"Configuracao carregada de {self.persistencia.config_path}")
        except FileNotFoundError:
            print(f"Arquivo de configuracao '{self.persistencia.config_path}' nao encontrado. Iniciando com configuracao vazia.")
        except ConfigInvalida as e:
            print(f"Erro ao carregar configuracao: {e}. Iniciando com configuracao vazia.")

    def _salvar_configuracao(self):
        try:
            config = self.hub.obter_configuracao()
            self.persistencia.salvar_configuracao(config)
            print("Configuracao salva.")
        except Exception as e:
            print(f"Erro ao salvar configuracao: {e}")

    def _listar_dispositivos(self):
        print("\n--- Dispositivos Cadastrados ---")
        if not self.hub.dispositivos:
            print("Nenhum dispositivo cadastrado.")
            return
        for dev_id, device in self.hub.dispositivos.items():
            print(f"{dev_id} | {device.tipo.name} | {device.estado}")

    def _mostrar_dispositivo(self):
        dev_id = input("ID do dispositivo: ").strip()
        device = self.hub.obter_dispositivo(dev_id)
        if device:
            print(f"\n--- Detalhes do Dispositivo: {device.nome} ({device.id}) ---")
            print(f"Tipo: {device.tipo.name}")
            print(f"Estado: {device.estado}")
            if hasattr(device, 'atributos') and device.atributos:
                print("Atributos:")
                for attr, value in device.atributos.items():
                    print(f"  - {attr}: {value}")
            if hasattr(device, 'tentativas_invalidas'): # Porta
                print(f"  - Tentativas invalidas: {device.tentativas_invalidas}")
            if hasattr(device, 'potencia_w'):
                print(f"  - Potencia (W): {device.potencia_w}")
                print(f"  - Consumo (Wh): {device.consumo_wh:.2f}")
        else:
            print(f"Dispositivo com ID '{dev_id}' nao encontrado.")

    def _executar_comando(self):
        dev_id = input("ID do dispositivo: ").strip()
        comando = input("Comando: ").strip()
        args_str = input("Argumentos (k=v separados por espaco) ou ENTER: ").strip()
        args = {}
        if args_str:
            try:
                args = dict(item.split("=") for item in args_str.split())
                # Tentar converter valores para tipos apropriados (int, float, bool)
                for k, v in args.items():
                    if v.isdigit():
                        args[k] = int(v)
                    elif v.replace('.', '', 1).isdigit():
                        args[k] = float(v)
                    elif v.lower() in ['true', 'false']:
                        args[k] = v.lower() == 'true'
            except ValueError:
                print("Formato de argumentos invalido. Use 'chave=valor'.")
                return

        try:
            self.hub.executar_comando(dev_id, comando, **args)
            print(f"[EVENTO] ComandoExecutado: {{'id': '{dev_id}', 'comando': '{comando}', 'args': {args}}}")
        except TransicaoInvalida as e:
            print(f"Erro: {e}")
        except AttributeError:
            print(f"Comando '{comando}' nao disponivel para o dispositivo '{dev_id}'.")
        except Exception as e:
            print(f"Erro inesperado ao executar comando: {e}")

    def _alterar_atributo(self):
        dev_id = input("ID do dispositivo: ").strip()
        atributo = input("Nome do atributo: ").strip()
        valor_str = input("Novo valor: ").strip()

        device = self.hub.obter_dispositivo(dev_id)
        if not device:
            print(f"Dispositivo com ID '{dev_id}' nao encontrado.")
            return

        try:
            # Tentar converter o valor para o tipo correto
            if hasattr(device, atributo):
                current_value = getattr(device, atributo)
                if isinstance(current_value, int):
                    valor = int(valor_str)
                elif isinstance(current_value, float):
                    valor = float(valor_str)
                elif isinstance(current_value, bool):
                    valor = valor_str.lower() == 'true'
                else: # Enums/strings
                    valor = valor_str
            else:
                valor = valor_str # Se o atributo não existe ainda, assume string ou tenta inferir

            setattr(device, atributo, valor)
            print(f"Atributo '{atributo}' do dispositivo '{dev_id}' alterado para '{valor}'.")
        except ValidacaoAtributo as e:
            print(f"Erro de validacao: {e}")
        except AttributeError:
            print(f"Atributo '{atributo}' nao encontrado ou nao pode ser alterado para o dispositivo '{dev_id}'.")
        except ValueError:
            print(f"Valor '{valor_str}' invalido para o atributo '{atributo}'.")
        except Exception as e:
            print(f"Erro inesperado ao alterar atributo: {e}")

    def _executar_rotina(self):
        rotina_nome = input("Nome da rotina: ").strip()
        try:
            self.hub.executar_rotina(rotina_nome)
            print(f"Rotina '{rotina_nome}' executada.")
        except ValueError as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado ao executar rotina: {e}")

    def _gerar_relatorio(self):
        print("\n--- Gerar Relatorio ---")
        print("Tipos de relatorio disponiveis:")
        print("1. Consumo por tomada inteligente")
        print("2. Tempo total de luz ligada")
        print("3. Caixa de Som")
        print("4. Ar condicionado")
        print("5. Termostato")
        print("6. Dispositivos mais usados")
        opcao = input("Escolha o tipo de relatorio: ").strip()

        try:
            if opcao == '1':
                relatorio = self.hub.gerar_relatorio_consumo_tomadas()
                print("\n--- Relatorio de Consumo por Tomada ---")
                for item in relatorio:
                    print(f"ID: {item['id_dispositivo']}, Consumo Total: {item['total_wh']:.2f} Wh")
            elif opcao == '2':
                relatorio = self.hub.gerar_relatorio_tempo_luz_ligada()
                print("\n--- Relatorio de Tempo de Luz Ligada ---")
                for item in relatorio:
                    print(f"ID: {item['id_dispositivo']}, Tempo Ligado: {item['tempo_total_horas']:.2f} horas")
            elif opcao == '3':
                relatorio = self.hub.gerar_relatorio_tempo_tocando_caixa_som()
                print("\n--- Relatorio de Tempo de Caixa de Som ---")
                for item in relatorio:
                    print(f"ID: {item['id_dispositivo']}, Tempo Ligado: {item['tempo_total_horas']:.2f} horas")
            elif opcao == '4':
                relatorio = self.hub.gerar_relatorio_modos_ar_condicionado()
                print("\n---  Relatorio de Modos de Ar Condicionado ---")
                if relatorio:
                    for modo, count in relatorio.items():
                        print(f"Modo: {modo}, Usos: {count}")
                else:
                    print("Nenhum dado de modos de ar condicionado encontrado.")
            elif opcao == '5':
                relatorio = self.hub.gerar_relatorio_temperatura_media_termostato()
                print("\n--- Relatorio de Temperatura Media de Termostato ---")
                if relatorio['temperatura_media'] is not None:
                    print(f"Temperatura Média: {relatorio['temperatura_media']:.2f}°C")
                else:
                    print("Nenhum termostato encontrado ou dados de temperatura.")
            elif opcao == '6':
                relatorio = self.hub.gerar_relatorio_dispositivos_mais_usados()
                print("\n--- Relatorio de Dispositivos Mais Usados ---")
                for item in relatorio:
                    print(f"ID: {item['id_dispositivo']}, Eventos: {item['num_eventos']}")
            else:
                print("Opcao de relatorio invalida.")
        except Exception as e:
            print(f"Erro ao gerar relatorio: {e}")


    def _adicionar_dispositivo(self):
        print("\n--- Adicionar Dispositivo ---")
        print(f"Tipos suportados: {', '.join([t.name for t in TipoDispositivo])}")
        tipo_str = input("tipo: ").strip().upper()
        try:
            tipo = TipoDispositivo[tipo_str]
        except KeyError:
            print(f"Tipo de dispositivo '{tipo_str}' invalido.")
            return

        dev_id = input("id (sem espacos): ").strip()
        nome = input("nome: ").strip()

        atributos = {}
        #coletar atributos específicos de cada tipo de dispositivo
        if tipo == TipoDispositivo.LUZ:
            brilho_str = input("brilho (0-100) [50]: ").strip()
            atributos['brilho'] = int(brilho_str) if brilho_str else 50
            cor_str = input("cor [QUENTE/FRIA/NEUTRA] [QUENTE]: ").strip().upper()
            atributos['cor'] = cor_str if cor_str else "QUENTE"
        elif tipo == TipoDispositivo.TOMADA:
            potencia_str = input("potencia_w (int >= 0): ").strip()
            atributos['potencia_w'] = int(potencia_str) if potencia_str else 0

        try:
            self.hub.adicionar_dispositivo(dev_id, tipo, nome, atributos)
            print(f"[EVENTO] DispositivoAdicionado: {{'id': '{dev_id}', 'tipo': '{tipo.name}'}}")
            print(f"dispositivo {dev_id} adicionado.")
        except ValueError as e:
            print(f"Erro ao adicionar dispositivo: {e}")
        except ValidacaoAtributo as e:
            print(f"Erro de validacao de atributo: {e}")
        except Exception as e:
            print(f"Erro inesperado ao adicionar dispositivo: {e}")

    def _remover_dispositivo(self):
        dev_id = input("ID do dispositivo: ").strip()
        try:
            self.hub.remover_dispositivo(dev_id)
            print(f"[EVENTO] DispositivoRemovido: {{'id': '{dev_id}'}}")
            print("dispositivo removido")
        except ValueError as e:
            print(f"Erro ao remover dispositivo: {e}")
        except Exception as e:
            print(f"Erro inesperado ao remover dispositivo: {e}")

    def run(self):
        while True:
            print("\n=== SMART HOME HUB ===")
            print("1. Listar dispositivos")
            print("2. Mostrar dispositivo")
            print("3. Executar comando em dispositivo")
            print("4. Alterar atributo de dispositivo")
            print("5. Executar rotina")
            print("6. Gerar relatorio")
            print("7. Salvar configuracao")
            print("8. Adicionar dispositivo")
            print("9. Remover dispositivo")
            print("10. Sair")
            opcao = input("Escolha uma opcao: ").strip()

            if opcao == '1':
                self._listar_dispositivos()
            elif opcao == '2':
                self._mostrar_dispositivo()
            elif opcao == '3':
                self._executar_comando()
            elif opcao == '4':
                self._alterar_atributo()
            elif opcao == '5':
                self._executar_rotina()
            elif opcao == '6':
                self._gerar_relatorio()
            elif opcao == '7':
                self._salvar_configuracao()
            elif opcao == '8':
                self._adicionar_dispositivo()
            elif opcao == '9':
                self._remover_dispositivo()
            elif opcao == '10':
                self._salvar_configuracao()
                print("saindo...")
                break
            else:
                print("Opcao invalida. Tente novamente.")

"""if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Smart Home Hub CLI")
    parser.add_argument('--config', type=str, default='data/configuracao.json',
                        help='Caminho para o arquivo de configuracao JSON.')
    args = parser.parse_args()

    cli = CLI(args.config)
    cli.run()"""
