import random
import os
import pygame # Import pygame para pygame.mixer.Sound e pygame.error

# Importa as configurações globais
import config

class SistemaLogin:
    def __init__(self):
        self.usuarios = {
            "ashford": "t-virus",
            "wesker": "umbrellacorp",
            "marcus": "omega789",
            "birkin": "g-virus",
            "annette": "researcher",
            "chefe": "nucleoalpha",
            "admin": "root",
            "tech": "datacore"
        }
        self.usuario_logado = None

    def verificar_credenciais(self, usuario, senha):
        if usuario in self.usuarios and self.usuarios[usuario] == senha:
            self.usuario_logado = usuario
            return True
        self.usuario_logado = None
        return False

    def esta_logado(self):
        return self.usuario_logado is not None

    def deslogar(self):
        self.usuario_logado = None

    def get_nome_exibicao(self, usuario):
        if usuario == "ashford":
            return "Dr. Charles Ashford"
        elif usuario == "wesker":
            return "Dr. Albert Wesker"
        elif usuario == "marcus":
            return "Dr. James Marcus"
        elif usuario == "birkin":
            return "Dr. William Birkin"
        elif usuario == "annette":
            return "Dra. Annette Birkin"
        elif usuario == "chefe":
            return "Dr. [Nome do Chefe] (Cientista Chefe)"
        elif usuario == "admin":
            return "Administrator"
        elif usuario == "tech":
            return "Técnico de Sistemas"
        return usuario.capitalize()

class SistemaArquivos:
    def __init__(self):
        self.estrutura = {
            "ST.AGNES": { # O diretório raiz
                "PESQUISAS": {
                    "RELATORIO_T_VIRUS.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "DADOS_G_VIRUS.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "REGISTRO_BIOHAZARD.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "ATIVAR_PURGE.BAT": [
                        "@echo off",
                        "REM Protocolo de Aniquilacao Total da ST.AGNES Biopharma Institute",
                        "ECHO Validando credenciais de Nivel Omega...",
                        "SET DESTRUCT_SEQUENCE=INITIATED",
                        "CALL purge_all_biological_samples.bat",
                        "CALL destroy_data_servers.sh",
                        "ECHO Ativando temporizadores de detonacion em 180 segundos.",
                        "ECHO Por favor, evacue a area. Este seja avisado."
                    ],
                    "LOGS_PURGE.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código."
                },
                "ARQUIVO": {
                    "MEMORANDO_DIRETORIA.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "HISTORICO_EMPRESA.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                },
                "COFRE_BIOLOGICO": {
                    "AMOSTRA_A1.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "AMOSTRA_B2.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "PROTOCOLO_QUARENTENA.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                },
                "SERVIDOR": {
                    "LOGS_DO_SISTEMA.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "CONFIGURACOES_CRITICAS.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código.",
                    "ATIVAR_SERVER_DESTRUCT.BAT": [
                        "@echo off",
                        "REM Protocolo de Destruicao de Servidores da ST.AGNES Biopharma Institute",
                        "ECHO Validando credenciais de Nivel Omega para destruicao de servidor...",
                        "SET SERVER_DESTRUCT_SEQUENCE=INITIATED",
                        "CALL destroy_main_server_data.bat",
                        "CALL wipe_backup_server.sh",
                        "ECHO Ativando temporizadores de detonacion em 180 segundos para servidores.",
                        "ECHO ALERTA: Todos os dados do servidor serao permanentemente apagados."
                    ],
                    "LOGS_SERVER_DESTRUCT.TXT": "Arquivo de texto. Conteúdo removido para reduzir tamanho do código."
                }
            }
        }
        self.caminho_atual = ["ST.AGNES"]

    def get_caminho_atual_exibicao(self):
        return "C:\\" + "\\".join(self.caminho_atual) + ">"

    def _get_diretorio_por_caminho(self, caminho_lista):
        ponto_atual = self.estrutura
        for parte in caminho_lista:
            if parte in ponto_atual and isinstance(ponto_atual[parte], dict):
                ponto_atual = ponto_atual[parte]
            else:
                return None
        return ponto_atual

    def cd(self, novo_diretorio, sistema_login_instance):
        # O sistema_login_instance é passado como argumento agora
        novo_diretorio_limpo = novo_diretorio.strip().upper()
        
        if novo_diretorio_limpo == "..":
            if len(self.caminho_atual) > 1:
                self.caminho_atual.pop()
                return [f"Caminho alterado para {self.get_caminho_atual_exibicao()}"]
            else:
                return ["Você já está no diretório raiz. Não pode ir mais acima."]
        
        caminho_para_testar = self.caminho_atual + [novo_diretorio_limpo]
        diretorio_alvo = self._get_diretorio_por_caminho(caminho_para_testar)

        if diretorio_alvo:
            # Verifica as permissões de acesso para pastas específicas usando SISTEMA_STATUS
            # Acesso para a pasta SERVIDOR
            if novo_diretorio_limpo == "SERVIDOR" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVIDOR"]["acesso_requerido"]:
                return ["Acesso negado: Somente o Diretor, Técnico ou Admin podem acessar a pasta SERVIDOR."]
            
            # Acesso para a pasta PESQUISAS (onde PURGE.BAT está agora)
            # A pasta PESQUISAS não tem restrição direta de CD, mas os arquivos dentro dela sim
            
            # Acesso para a pasta SERVER_DESTRUCT (que não existe mais como pasta, mas se estivesse, seria assim)
            # if novo_diretorio_limpo == "SERVER_DESTRUCT" and \
            #    sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
            #    return ["Acesso negado: Somente o Técnico de Sistemas ou Admin podem acessar a pasta SERVER_DESTRUCT."]

            self.caminho_atual.append(novo_diretorio_limpo)
            return [f"Caminho alterado para {self.get_caminho_atual_exibicao()}"]
        else:
            return [f"Erro: Diretório '{novo_diretorio}' não encontrado ou inválido."]

    def ls(self, sistema_login_instance):
        # O sistema_login_instance é passado como argumento agora
        respostas = []
        diretorio_atual_obj = self._get_diretorio_por_caminho(self.caminho_atual)

        if not diretorio_atual_obj:
            return ["Erro interno: Diretório atual não encontrado."]

        respostas.append(f"Conteúdo de {self.get_caminho_atual_exibicao()}")
        for nome, conteudo in diretorio_atual_obj.items():
            tipo = "DIR" if isinstance(conteudo, dict) else "FILE"
            
            # Verifica permissões para exibir pastas ou arquivos específicos no LS
            if nome == "SERVIDOR" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVIDOR"]["acesso_requerido"]:
                continue 

            # PURGE.BAT está em PESQUISAS agora
            if nome == "ATIVAR_PURGE.BAT" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                continue
            if nome == "LOGS_PURGE.TXT" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                continue
            
            # SERVER_DESTRUCT.BAT está em SERVIDOR agora
            if nome == "ATIVAR_SERVER_DESTRUCT.BAT" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
                continue
            if nome == "LOGS_SERVER_DESTRUCT.TXT" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
                continue
            
            respostas.append(f"  [{tipo}] {nome}")
        
        if not respostas or (len(respostas) == 1 and "Conteúdo de" in respostas[0]):
             respostas.append("  Este diretório está vazio ou você não tem permissão para ver seu conteúdo.")
        
        return respostas

    def view(self, nome_arquivo, sistema_login_instance):
        # O sistema_login_instance é passado como argumento agora
        respostas = []
        diretorio_atual_obj = self._get_diretorio_por_caminho(self.caminho_atual)

        if not diretorio_atual_obj:
            return ["Erro interno: Diretório atual não encontrado."]

        nome_arquivo_limpo = nome_arquivo.strip().upper()
        
        if nome_arquivo_limpo in diretorio_atual_obj:
            conteudo = diretorio_atual_obj[nome_arquivo_limpo]
            if isinstance(conteudo, dict):
                respostas.append(f"Erro: '{nome_arquivo}' é um diretório, não um arquivo. Use 'CD' para entrar nele.")
            else: # É um arquivo
                # Verifica permissões para ver arquivos específicos
                if nome_arquivo_limpo == "ATIVAR_PURGE.BAT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                if nome_arquivo_limpo == "LOGS_PURGE.TXT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                if nome_arquivo_limpo == "ATIVAR_SERVER_DESTRUCT.BAT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                if nome_arquivo_limpo == "LOGS_SERVER_DESTRUCT.TXT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                respostas.append(f"--- CONTEÚDO DE '{nome_arquivo}' ---")
                if isinstance(conteudo, list): # Se o conteúdo for uma lista de linhas
                    respostas.extend(conteudo)
                else: # Se for uma string simples
                    respostas.append(conteudo)
                respostas.append(f"--- FIM DO ARQUIVO ---")

                if nome_arquivo_limpo == "ATIVAR_PURGE.BAT":
                    return (respostas, "ATIVAR_PURGE") # Sinaliza para o loop principal
                elif nome_arquivo_limpo == "ATIVAR_SERVER_DESTRUCT.BAT":
                    return (respostas, "ATIVAR_SERVER_DESTRUCT")
        else:
            respostas.append(f"Erro: Arquivo '{nome_arquivo}' não encontrado no diretório atual.")
        
        return (respostas, None)