import os
import config 

class SistemaLogin:
    def __init__(self):
        # Usuários e senhas com nomes de exibição e níveis de acesso
        self.usuarios = {
            "ashford": {"senha": "t-virus", "nome_exibicao": "Dr. Charles Ashford", "acesso": "cientista"},
            "wesker": {"senha": "umbrellacorp", "nome_exibicao": "Dr. Albert Wesker", "acesso": "cientista"},
            "marcus": {"senha": "omega789", "nome_exibicao": "Dr. James Marcus", "acesso": "diretor"},
            "birkin": {"senha": "g-virus", "nome_exibicao": "Dr. William Birkin", "acesso": "cientista"},
            "annette": {"senha": "researcher", "nome_exibicao": "Dra. Annette Birkin", "acesso": "cientista"},
            "chefe": {"senha": "nucleoalpha", "nome_exibicao": "Dr. [Nome do Chefe] (Cientista Chefe)", "acesso": "cientista_chefe"},
            "admin": {"senha": "root", "nome_exibicao": "Administrator", "acesso": "admin"},
            "tech": {"senha": "datacore", "nome_exibicao": "Técnico de Sistemas", "acesso": "tech"}
        }
        self.usuario_logado = None
        self.tentativas_falhas = {} # Para controle de bloqueio por IP (não implementado ainda)

    def verificar_credenciais(self, usuario, senha):
        if usuario in self.usuarios and self.usuarios[usuario]["senha"] == senha:
            self.usuario_logado = usuario
            return True
        return False

    def esta_logado(self):
        return self.usuario_logado is not None

    def deslogar(self):
        self.usuario_logado = None

    def get_nome_exibicao(self, usuario):
        if usuario in self.usuarios:
            return self.usuarios[usuario]["nome_exibicao"]
        return usuario.capitalize() # Fallback, embora todos os usuários devam ter nome_exibicao


class SistemaArquivos:
    def __init__(self):
        self.caminho_atual = ["ST.AGNES"] 
        
        # Mapeamento de arquivos virtuais para arquivos TXT reais na pasta 'txt'
        self.TEXT_FILES_MAP = {
            "RELATORIO_T_VIRUS.TXT": "relatorio_t_virus.txt",
            "DADOS_G_VIRUS.TXT": "dados_g_virus.txt",
            "REGISTRO_BIOHAZARD.TXT": "registro_biohazard.txt",
            "MEMORANDO_DIRETORIA.TXT": "memorando_diretoria.txt",
            "HISTORICO_EMPRESA.TXT": "historico_empresa.txt",
            "AMOSTRA_A1.TXT": "amostra_a1.txt",
            "AMOSTRA_B2.TXT": "amostra_b2.txt",
            "PROTOCOLO_QUARENTENA.TXT": "protocolo_quarentena.txt",
            "LOGS_DO_SISTEMA.TXT": "logs_do_sistema.txt",
            "CONFIGURACOES_CRITICAS.TXT": "configuracoes_criticas.txt",
            "LOGS_PURGE.TXT": "logs_purge.txt",
            "LOGS_SERVER_DESTRUCT.TXT": "logs_server_destruct.txt",
            
            "PURGE.BAT": "ativar_purge.bat", 
            "DESTROY.BAT": "ativar_server_destruct.bat", 
            "NAKATOMI_5.BAT": "nakatomi_5_ad_content.txt", # <--- NOVO: Mapeamento para o arquivo do anúncio
        }
        
        # Adiciona 8 relatórios de incidente e 8 de progresso
        for i in range(1, 9): 
            self.TEXT_FILES_MAP[f"RELATORIO_INCIDENTE_{i:03d}.TXT"] = f"relatorio_incidente_{i:03d}.txt"
            self.TEXT_FILES_MAP[f"RELATORIO_DE_PROGRESSO_{i:03d}.TXT"] = f"relatorio_de_progresso_{i:03d}.txt"

        self.estrutura = {
            "ST.AGNES": { # O diretório raiz
                "PESQUISAS": {
                    "RELATORIO_T_VIRUS.TXT": "LOAD_FROM_FILE", 
                    "DADOS_G_VIRUS.TXT": "LOAD_FROM_FILE",
                    "REGISTRO_BIOHAZARD.TXT": "LOAD_FROM_FILE",
                    "PURGE.BAT": [ 
                        "@echo off",
                        "REM Protocolo de Aniquilacao Total da ST.AGNES Biopharma Institute",
                        "ECHO Validando credenciais de Nivel Omega...",
                        "SET DESTRUCT_SEQUENCE=INITIATED",
                        "CALL purge_all_biological_samples.bat",
                        "CALL destroy_data_servers.sh",
                        "ECHO Ativando temporizadores de detonacion em 180 segundos.",
                        "ECHO Por favor, evacue a area. Esteja avisado."
                    ],
                    "LOGS_PURGE.TXT": "LOAD_FROM_FILE",
                    "NAKATOMI_5.BAT": "LOAD_FROM_FILE_SPECIAL_AD", # <--- NOVO: Flag para exibicao especial
                },
                "ARQUIVO": {
                    "MEMORANDO_DIRETORIA.TXT": "LOAD_FROM_FILE",
                    "HISTORICO_EMPRESA.TXT": "LOAD_FROM_FILE",
                },
                "COFRE_BIOLOGICO": {
                    "AMOSTRA_A1.TXT": "LOAD_FROM_FILE",
                    "AMOSTRA_B2.TXT": "LOAD_FROM_FILE",
                    "PROTOCOLO_QUARENTENA.TXT": "LOAD_FROM_FILE",
                },
                "SERVIDOR": {
                    "LOGS_DO_SISTEMA.TXT": "LOAD_FROM_FILE",
                    "CONFIGURACOES_CRITICAS.TXT": "LOAD_FROM_FILE",
                    "DESTROY.BAT": [ 
                        "@echo off",
                        "REM Protocolo de Destruicao de Servidores da ST.AGNES Biopharma Institute",
                        "ECHO Validando credenciais de Nivel Omega para destruicao de servidor...",
                        "SET SERVER_DESTRUCT_SEQUENCE=INITIATED",
                        "CALL destroy_main_server_data.bat",
                        "CALL wipe_backup_server.sh",
                        "ECHO Ativando temporizadores de detonacion em 180 segundos para servidores.",
                        "ECHO ALERTA: Todos os dados do servidor serao permanentemente apagados."
                    ],
                    "LOGS_SERVER_DESTRUCT.TXT": "LOAD_FROM_FILE",
                }
            }
        }

        # Adiciona os relatórios de incidente e progresso aos seus respectivos diretórios
        for i in range(1, 9):
            self.estrutura["ST.AGNES"]["PESQUISAS"][f"RELATORIO_INCIDENTE_{i:03d}.TXT"] = "LOAD_FROM_FILE"
            self.estrutura["ST.AGNES"]["ARQUIVO"][f"RELATORIO_DE_PROGRESSO_{i:03d}.TXT"] = "LOAD_FROM_FILE" 

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
            if novo_diretorio_limpo == "SERVIDOR" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVIDOR"]["acesso_requerido"]:
                return ["Acesso negado: Somente o Diretor, Técnico ou Admin podem acessar a pasta SERVIDOR."]
            
            self.caminho_atual.append(novo_diretorio_limpo)
            return [f"Caminho alterado para {self.get_caminho_atual_exibicao()}"]
        else:
            return [f"Erro: Diretório '{novo_diretorio}' não encontrado ou inválido."]

    def ls(self, sistema_login_instance):
        respostas = []
        diretorio_atual_obj = self._get_diretorio_por_caminho(self.caminho_atual)

        if not diretorio_atual_obj:
            return ["Erro interno: Diretório atual não encontrado."]

        respostas.append(f"Conteúdo de {self.get_caminho_atual_exibicao()}")
        for nome, conteudo in diretorio_atual_obj.items():
            tipo = "DIR" if isinstance(conteudo, dict) else "FILE"
            
            if nome == "SERVIDOR" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVIDOR"]["acesso_requerido"]:
                continue 

            if nome == "PURGE.BAT" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                continue
            if nome == "LOGS_PURGE.TXT" and \
               sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                continue
            
            if nome == "DESTROY.BAT" and \
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
        respostas = []
        diretorio_atual_obj = self._get_diretorio_por_caminho(self.caminho_atual)

        if not diretorio_atual_obj:
            return ["Erro interno: Diretório atual não encontrado."]

        nome_arquivo_limpo = nome_arquivo.strip().upper()
        
        if nome_arquivo_limpo in diretorio_atual_obj:
            conteudo_armazenado = diretorio_atual_obj[nome_arquivo_limpo]

            if isinstance(conteudo_armazenado, dict):
                respostas.append(f"Erro: '{nome_arquivo}' é um diretório, não um arquivo. Use 'CD' para entrar nele.")
            else: # É um arquivo
                # Verifica permissões para ver arquivos específicos
                if nome_arquivo_limpo == "PURGE.BAT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                if nome_arquivo_limpo == "LOGS_PURGE.TXT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["PURGE_PROTOCOLO"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                if nome_arquivo_limpo == "DESTROY.BAT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                if nome_arquivo_limpo == "LOGS_SERVER_DESTRUCT.TXT" and \
                   sistema_login_instance.usuario_logado not in config.SISTEMA_STATUS["SERVER_DESTRUCT"]["acesso_requerido"]:
                    return ([f"Acesso negado: Você não tem permissão para visualizar '{nome_arquivo}'."], None)
                
                # --- NOVO: Lógica para ativar display especial para NAKATOMI_5.BAT ---
                if conteudo_armazenado == "LOAD_FROM_FILE_SPECIAL_AD":
                    if nome_arquivo_limpo == "NAKATOMI_5.BAT": 
                        return (respostas, "DISPLAY_NAKATOMI_AD") # Retorna o estado especial
                    else:
                        respostas.append(f"Erro: Tipo de exibicao especial para '{nome_arquivo}' nao implementado.")
                        return (respostas, None)
                # --- FIM NOVO ---

                elif conteudo_armazenado == "LOAD_FROM_FILE":
                    if nome_arquivo_limpo in self.TEXT_FILES_MAP:
                        file_name_in_txt_folder = self.TEXT_FILES_MAP[nome_arquivo_limpo]
                        file_path = os.path.join('txt', file_name_in_txt_folder)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                file_content = f.readlines() 
                            respostas.append(f"--- CONTEÚDO DE '{nome_arquivo}' ---")
                            respostas.extend([line.strip() for line in file_content])
                            respostas.append(f"--- FIM DO ARQUIVO ---")
                            
                            if nome_arquivo_limpo == "PURGE.BAT": 
                                return (respostas, "ATIVAR_PURGE") 
                            elif nome_arquivo_limpo == "DESTROY.BAT": 
                                return (respostas, "ATIVAR_SERVER_DESTRUCT") 
                            return (respostas, None) 
                        except FileNotFoundError:
                            respostas.append(f"Erro: Arquivo '{file_name_in_txt_folder}' não encontrado na pasta 'txt'.")
                            return (respostas, None)
                        except Exception as e:
                            respostas.append(f"Erro ao ler '{file_name_in_txt_folder}': {e}")
                            return (respostas, None)
                    else:
                        respostas.append(f"Erro interno: Mapeamento de arquivo '{nome_arquivo}' ausente para leitura de TXT.")
                        return (respostas, None)
                else: # Conteúdo embutido (para arquivos .BAT por exemplo)
                    respostas.append(f"--- CONTEÚDO DE '{nome_arquivo}' ---")
                    if isinstance(conteudo_armazenado, list): 
                        respostas.extend(conteudo_armazenado)
                    else: 
                        respostas.append(conteudo_armazenado)
                    respostas.append(f"--- FIM DO ARQUIVO ---")

                    if nome_arquivo_limpo == "PURGE.BAT": 
                        return (respostas, "ATIVAR_PURGE") 
                    elif nome_arquivo_limpo == "DESTROY.BAT": 
                        return (respostas, "ATIVAR_SERVER_DESTRUCT") 
        else:
            respostas.append(f"Erro: Arquivo '{nome_arquivo}' não encontrado no diretório atual.")
        
        return (respostas, None)