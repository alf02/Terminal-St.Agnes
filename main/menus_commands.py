import random

# Importa os módulos necessários
import config
import systems # Para acessar SistemaLogin e SistemaArquivos

# --- Funções para os Menus (adaptadas para não serem métodos de classe) ---
def get_menu_cientista():
    return [
        "",
        "--- MENU CIENTISTA ---",
        "  PESQUISAS            | Acessa relatórios de pesquisa (CD PESQUISAS)",
        "  ARQUIVO              | Navega por arquivos do projeto (CD ARQUIVO)",
        "  COFRE BIOLOGICO      | Gerencia amostras biológicas (CD COFRE_BIOLOGICO)",
        "  LS                   | Lista o conteúdo da pasta atual",
        "  CD ..                | Volta para a pasta anterior",
        "  VIEW [arquivo]       | Exibe o conteúdo de um arquivo",
        "  LOGOUT               | Sai da sessão atual",
        "----------------------",
        ""
    ]

def get_menu_cientista_chefe():
    return [
        "",
        "--- MENU CIENTISTA CHEFE ---",
        "  PESQUISAS            | Acessa relatórios de pesquisa (CD PESQUISAS)",
        "  ARQUIVO              | Navega por arquivos de projeto (CD ARQUIVO)",
        "  COFRE BIOLOGICO      | Gerencia amostras biológicas (CD COFRE_BIOLOGICO)",
        "  LS                   | Lista o conteúdo da pasta atual",
        "  CD ..                | Volta para a pasta anterior",
        "  VIEW [arquivo]       | Exibe o conteúdo de um arquivo",
        "  HACK                 | Inicia o mini-game de hacking",
        "  LOGOUT               | Sai da sessão atual",
        "--------------------------",
        ""
    ]

def get_menu_diretor():
    return [
        "",
        "--- MENU DIRETOR ---",
        "  PESQUISAS            | Acessa relatórios de pesquisa (CD PESQUISAS)",
        "  ARQUIVO              | Navega por arquivos do projeto (CD ARQUIVO)",
        "  COFRE BIOLOGICO      | Gerencia amostras biológicas (CD COFRE_BIOLOGICO)",
        "  SERVIDOR             | Gerencia o servidor principal (CD SERVIDOR)",
        "  LS                   | Lista o conteúdo da pasta atual",
        "  CD ..                | Volta para a pasta anterior",
        "  VIEW [arquivo]       | Exibe o conteúdo de um arquivo",
        "  HACK                 | Inicia o mini-game de hacking",
        "  LOGOUT               | Sai da sessão atual",
        "--------------------",
        ""
    ]

def get_menu_tech():
    return [
        "",
        "--- MENU TÉCNICO DE SISTEMAS ---",
        "  COFRE BIOLOGICO      | Gerencia amostras biológicas (CD COFRE_BIOLOGICO)",
        "  SERVIDOR             | Gerencia o servidor principal (CD SERVIDOR)",
        "  LS                   | Lista o conteúdo da pasta atual",
        "  CD ..                | Volta para a pasta anterior",
        "  VIEW [arquivo]       | Exibe o conteúdo de um arquivo",
        "  HACK                 | Inicia o mini-game de hacking",
        "  LOGOUT               | Sai da sessão atual",
        "------------------------------",
        ""
    ]

def get_menu_admin():
    return [
        "",
        "--- MENU ADMINISTRADOR ---",
        "  PESQUISAS            | Acessa relatórios de pesquisa (CD PESQUISAS)",
        "  ARQUIVO              | Navega por arquivos do projeto (CD ARQUIVO)",
        "  COFRE BIOLOGICO      | Gerencia amostras biológicas (CD COFRE_BIOLOGICO)",
        "  SERVIDOR             | Gerencia o servidor principal (CD SERVIDOR)",
        "  LS                   | Lista o conteúdo da pasta atual",
        "  CD ..                | Volta para a pasta anterior",
        "  VIEW [arquivo]       | Exibe o conteúdo de um arquivo",
        "  HACK                 | Inicia o mini-game de hacking",
        "  LOGOUT               | Sai da sessão atual",
        "--------------------------",
        ""
    ]

def get_menu_inicial_mensagens():
    """Retorna as mensagens iniciais exibidas no terminal."""
    return [
        "Digite 'HELP' para uma lista de comandos.",
        "Para iniciar, digite 'LOGON [seu usuario]'."
    ]

# --- Função para Processar Comandos (AGORA RETORNA SUGESTÕES DE ESTADO) ---
def processar_comando(comando, sistema_login_instance, sistema_arquivos_instance, play_sound_callback):
    # sistema_login_instance e sistema_arquivos_instance são instâncias de suas respectivas classes
    # play_sound_callback é a função play_sound do main.py (passada como callback para evitar dependência circular)
    
    comando_limpo = comando.strip().upper()
    respostas = []
    
    sugestao_proximo_estado = None 
    dados_proximo_estado = None
    sugestao_som_tocar = None 

    if comando_limpo == "HELP":
        respostas.append("")
        respostas.append("  logon [usuario]      | Entrar com um usuário específico")
        if sistema_login_instance.esta_logado():
            respostas.append("  logout               | Sair da sessão atual")
        respostas.append("  shutdown             | Desliga o sistema operacional")
        respostas.append("  help                 | Exibe os comandos de ajuda")
        respostas.append("  menu                 | Exibe o menu de opções do usuário")
        respostas.append("  status [sistema]     | Exibe o status de um sistema (energia, servidor, etc.)")
        respostas.append("  cd [diretorio]       | Muda para o diretório especificado")
        respostas.append("  ls                   | Lista o conteúdo do diretório atual")
        respostas.append("  view [arquivo]       | Exibe o conteúdo de um arquivo")
        respostas.append("  exec [arquivo]       | Executa/Exibe o conteúdo de um arquivo")
        respostas.append("  hack                 | Inicia o mini-game de hacking")
        respostas.append("  clear                | Limpa a tela do terminal")
        respostas.append("")
        sugestao_som_tocar = "valid"
    elif comando_limpo == "MENU":
        if sistema_login_instance.esta_logado():
            if sistema_login_instance.usuario_logado == "admin":
                respostas.extend(get_menu_admin())
            elif sistema_login_instance.usuario_logado == "marcus":
                respostas.extend(get_menu_diretor())
            elif sistema_login_instance.usuario_logado == "chefe":
                respostas.extend(get_menu_cientista_chefe())
            elif sistema_login_instance.usuario_logado == "tech":
                respostas.extend(get_menu_tech())
            else:
                respostas.extend(get_menu_cientista())
            sugestao_som_tocar = "valid"
        else:
            respostas.append("Nenhum usuário logado. Faça login para acessar o menu de opções.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo.startswith("CD "):
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                diretorio_alvo = partes[1].strip()
                respostas.extend(sistema_arquivos_instance.cd(diretorio_alvo, sistema_login_instance))
                sugestao_som_tocar = "valid"
            else:
                respostas.append("Uso: CD [diretorio]")
                sugestao_som_tocar = "invalid"
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo == "CD..": # Tratamento específico para CD.. (sem espaço)
        if sistema_login_instance.esta_logado():
            respostas.extend(sistema_arquivos_instance.cd("..", sistema_login_instance))
            sugestao_som_tocar = "valid"
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo == "LS":
        if sistema_login_instance.esta_logado():
            respostas.extend(sistema_arquivos_instance.ls(sistema_login_instance))
            sugestao_som_tocar = "valid"
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo.startswith("VIEW "):
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                nome_arquivo_alvo = partes[1].strip()
                # A função view agora recebe sistema_login_instance
                view_respostas, view_sugestao = sistema_arquivos_instance.view(nome_arquivo_alvo, sistema_login_instance)
                respostas.extend(view_respostas)
                if view_sugestao:
                    sugestao_proximo_estado = view_sugestao
                    sugestao_som_tocar = "valid"
                else:
                    sugestao_som_tocar = "valid"
            else:
                respostas.append("Uso: VIEW [arquivo]")
                sugestao_som_tocar = "invalid"
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo.startswith("EXEC "):
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                nome_arquivo_alvo = partes[1].strip()
                # A função view agora recebe sistema_login_instance
                exec_respostas, exec_sugestao = sistema_arquivos_instance.view(nome_arquivo_alvo, sistema_login_instance)
                respostas.extend(exec_respostas)
                if exec_sugestao:
                    sugestao_proximo_estado = exec_sugestao
                    sugestao_som_tocar = "valid"
                else:
                    sugestao_som_tocar = "valid"
            else:
                respostas.append("Uso: EXEC [arquivo]")
                sugestao_som_tocar = "invalid"
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo == "HACK":
        if sistema_login_instance.esta_logado() and \
           sistema_login_instance.usuario_logado in ["marcus", "chefe", "admin", "tech"]:
            
            sugestao_proximo_estado = "HACKING"
            
            dados_hacking = {}
            comprimento_alvo = random.choice([6, 7, 8, 9])
            palavras_filtradas = [p for p in config.HACKING_PALAVRAS_BASE if len(p) == comprimento_alvo]
            
            if len(palavras_filtradas) < config.HACKING_MAX_TENTATIVAS * 2:
                palavras_filtradas = [p for p in config.HACKING_PALAVRAS_BASE if len(p) >= 6]

            sequencias_geradas = []
            for _ in range(config.NUM_SEQUENCIAS_ESPECIAIS):
                tipo_seq_info = random.choice(config.HACKING_TIPOS_ESPECIAIS)
                open_char = tipo_seq_info[1]
                close_char = tipo_seq_info[2]
                junk_content = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(1, 3)))
                sequencia_completa = f"{open_char}{junk_content}{close_char}"
                sequencias_geradas.append((sequencia_completa, tipo_seq_info[0]))
            
            todas_opcoes = list(palavras_filtradas)
            for seq_str, _ in sequencias_geradas:
                todas_opcoes.append(seq_str)
            random.shuffle(todas_opcoes)
            
            if len(todas_opcoes) < 10 and len(config.HACKING_PALAVRAS_BASE) > len(todas_opcoes):
                while len(todas_opcoes) < 10:
                    palavra_nova = random.choice(config.HACKING_PALAVRAS_BASE)
                    if len(palavra_nova) == comprimento_alvo and palavra_nova not in todas_opcoes:
                        todas_opcoes.append(palavra_nova)
            
            dados_hacking['palavras'] = todas_opcoes
            
            palavras_sem_sequencias = [p for p in todas_opcoes if p not in [s[0] for s in sequencias_geradas]]
            if palavras_sem_sequencias:
                dados_hacking['senha_correta'] = random.choice(palavras_sem_sequencias)
            else:
                dados_hacking['senha_correta'] = random.choice(palavras_filtradas)
            
            dados_hacking['tentativas_restantes'] = config.HACKING_MAX_TENTATIVAS
            dados_hacking['likeness_ultima_tentativa'] = -1
            dados_hacking['sequencias_ativas'] = {seq_str: tipo_ef for seq_str, tipo_ef in sequencias_geradas}
            
            dados_proximo_estado = dados_hacking
            
            respostas.append("Iniciando Hacking Protocol...")
            sugestao_som_tocar = "valid"
            
        else:
            respostas.append("Acesso negado: Somente o Diretor, Cientista Chefe, Técnico ou Admin podem iniciar o Hacking.")
            respostas.append("Faça login com um usuário autorizado.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo.startswith("STATUS"):
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            sistema_alvo = partes[1].upper() if len(partes) > 1 else "OVERVIEW"
            
            if sistema_alvo in config.SISTEMA_STATUS:
                status_obj = config.SISTEMA_STATUS[sistema_alvo]
                if not status_obj["acesso_requerido"] or \
                   sistema_login_instance.usuario_logado in status_obj["acesso_requerido"]:
                    respostas.append(f"--- STATUS DE {status_obj['nome_exibicao'].upper()} ---")
                    respostas.append(f"  Status: {status_obj['status']}")
                    for detalhe in status_obj['detalhes']:
                        respostas.append(f"  - {detalhe}")
                    respostas.append("----------------------------")
                    sugestao_som_tocar = "valid"
                else:
                    respostas.append(f"Acesso negado: Você não tem permissão para ver o status de {status_obj['nome_exibicao']}.")
                    sugestao_som_tocar = "invalid"
            elif sistema_alvo == "OVERVIEW":
                respostas.append("--- STATUS GERAL DO SISTEMA ---")
                for sys_key, sys_info in config.SISTEMA_STATUS.items():
                    if not sys_info["acesso_requerido"] or \
                       sistema_login_instance.usuario_logado in sys_info["acesso_requerido"]:
                        respostas.append(f"  {sys_info['nome_exibicao']}: {sys_info['status']}")
                    else:
                        respostas.append(f"  {sys_info['nome_exibicao']}: Acesso Restrito")
                respostas.append("----------------------------")
                sugestao_som_tocar = "valid"
            else:
                respostas.append(f"Sistema '{sistema_alvo}' não reconhecido.")
                respostas.append("Sistemas disponíveis: ENERGIA, SERVIDOR, BACKUP, BIOAMOSTRAS, SERVER_DESTRUCT, PURGE_PROTOCOLO.")
                sugestao_som_tocar = "invalid"
        else:
            respostas.append("Acesso negado. Por favor, faça login (LOGON [user]).")
            sugestao_som_tocar = "invalid"
    elif comando_limpo == "DIR":
        if sistema_login_instance.esta_logado():
            respostas.append("Este comando foi substituído por 'LS'.")
            respostas.extend(sistema_arquivos_instance.ls(sistema_login_instance))
            sugestao_som_tocar = "valid"
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo == "CLEAR":
        sugestao_proximo_estado = "CLEAR_SCREEN"
        sugestao_som_tocar = "valid"
    elif comando_limpo == "EXIT":
        respostas.append("Desligando terminal...")
        sugestao_proximo_estado = "EXIT_GAME"
        sugestao_som_tocar = "shutdown"
    elif comando_limpo == "SHUTDOWN": # Alias para EXIT
        respostas.append("Desligando terminal...")
        sugestao_proximo_estado = "EXIT_GAME"
        sugestao_som_tocar = "shutdown"
    elif comando_limpo == "LOGOUT":
        if sistema_login_instance.esta_logado():
            sistema_login_instance.deslogar()
            sistema_arquivos_instance.caminho_atual = ["ST.AGNES"]
            respostas.append("Logout bem-sucedido.")
            respostas.append("Sistema aguardando login.")
            sugestao_som_tocar = "login_success"
        else:
            respostas.append("Nenhum usuário logado.")
            sugestao_som_tocar = "invalid"
    elif comando_limpo.startswith("LOGON"):
        if sistema_login_instance.esta_logado():
            respostas.append(f"Usuário '{sistema_login_instance.get_nome_exibicao(sistema_login_instance.usuario_logado)}' já está logado.")
            respostas.append("Faça LOGOUT antes de tentar um novo login.")
            sugestao_som_tocar = "invalid"
        else:
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                usuario_tentativa = partes[1].lower()
                if usuario_tentativa in sistema_login_instance.usuarios:
                    respostas.append(f"Tentando logon como '{usuario_tentativa}'...")
                    respostas.append("Enter password now:")
                    sugestao_proximo_estado = "AGUARDANDO_SENHA"
                    dados_proximo_estado = usuario_tentativa
                    sugestao_som_tocar = "valid"
                else:
                    respostas.append(f"Usuário '{usuario_tentativa}' não encontrado.")
                    respostas.append("Digite 'HELP' para ver os comandos disponíveis.")
                    sugestao_som_tocar = "invalid"
            else:
                respostas.append("Uso: LOGON [user]")
                sugestao_som_tocar = "invalid"
    else:
        respostas.append(f"Comando '{comando}' não reconhecido.")
        respostas.append("Digite 'HELP' para ver os comandos disponíveis.")
        sugestao_som_tocar = "invalid"
    
    return (respostas, sugestao_proximo_estado, dados_proximo_estado, sugestao_som_tocar)