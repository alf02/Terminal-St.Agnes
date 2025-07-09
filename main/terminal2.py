import pygame
import sys
import random
import os
import time
import socket # NOVO: Para comunicação de rede UDP

# Tentar forçar o driver de vídeo para Windows, pode ajudar com tela preta
os.environ['SDL_VIDEODRIVER'] = 'windows'

# --- Configurações do Terminal ---
LARGURA_TELA = 800
ALTURA_TELA = 600
COR_FUNDO = (0, 0, 0)
COR_TEXTO = (0, 255, 0)
COR_SCANLINE = (0, 50, 0)
COR_GLITCH = (0, 100, 0)

TAMANHO_FONTE = 24
INTERVALO_CURSOR_PISCAR = 500

# Caminho para sua fonte (certifique-se de que o arquivo .ttf esteja na mesma pasta)
NOME_ARQUIVO_FONTE = 'monofonto.ttf'

# --- Configurações de Glitch ---
GLITCH_PROBABILITY = 0.005
GLITCH_DURATION_MIN = 50
GLITCH_DURATION_MAX = 200
GLITCH_SHIFT_MAX = 5
GLITCH_NOISE_PIXELS = 100

glitch_ativo = False
glitch_tipo = None
glitch_tempo_inicio = 0
glitch_duracao = 0

# Declarando TODAS as variáveis globais que podem ser MODIFICADAS NESTE BLOCO de KEYDOWN.
# Esta deve ser a PRIMEIRA COISA dentro do elif evento.type == pygame.KEYDOWN:
global comando_atual, estado_terminal, usuario_tentando_logar, \
historico_comandos, historico_indice, \
hacking_game_ativo, hacking_palavras_possiveis, hacking_senha_correta, \
hacking_tentativas_restantes, hacking_likeness_ultima_tentativa, \
hacking_sequencias_ativas, \
purge_protocolo_ativo, purge_tempo_inicio_ticks, purge_mensagem_adicional 

# --- Variáveis do Jogo de Hacking ---
hacking_game_ativo = False
hacking_palavras_possiveis = []
hacking_senha_correta = ""
hacking_tentativas_restantes = 0
hacking_likeness_ultima_tentativa = -1 # -1 significa nenhum palpite ainda
hacking_max_tentativas = 4 # Tentativas iniciais
hacking_palavras_base = [
    "NEURONIO", "GENETICA", "VIROLOGIA", "MUTACAO", "CONTECAO",
    "ENZIMAS", "ANTIDOTO", "PATOGENO", "BIOHAZARD", "ANOMALIA",
    "CELULAR", "EXPERIMENTO", "INSTITUTO", "LABORATORIO", "PROJETO",
    "REATIVAR", "SEQUENCIA", "VACINAS", "VIRULENCIA", "GENOMA",
    "RAIZ", "CELULA", "VIRUS", "ARMA", "REDE", "SISTEMA", "PORTAL",
    "ALFA", "BETA", "GAMMA", "DELTA", "OMEGA", "CONTROLE", "CRITICO",
    "FUSION", "CORE", "ENCRIPT", "DECRYPT", "MALWARE", "FIREWALL",
    "PROTOCOLO", "ESPIAO", "INVASOR", "ACESSOS"
]

# Tipos de sequências especiais para o hacking game
hacking_tipos_especiais = [
    ("dud", "(", ")"),
    ("dud", "[", "]"),
    ("attempt", "{", "}"),
    ("attempt", "<", ">")
]
NUM_SEQUENCIAS_ESPECIAIS = 4

# --- Comando Secreto de Backdoor ---
COMANDO_BACKDOOR = "SYS.OVERRIDE(BIOPH@RMA_CORE)"

# --- STATUS DOS SISTEMAS ---
sistema_status = {
    "ENERGIA": {
        "nome_exibicao": "Sistema de Energia",
        "status": "Estável",
        "detalhes": ["Nível de energia: 95%", "Consumo: Normal"],
        "acesso_requerido": [] # Sem restrição de usuário logado
    },
    "SERVIDOR": {
        "nome_exibicao": "Servidor Principal",
        "status": "Operacional",
        "detalhes": ["Ping: 5ms", "Carga da CPU: 12%", "Acesso via rede local.", "Logs: Ultima entrada 01:23."],
        "acesso_requerido": ["marcus", "admin"] # Diretor e Admin
    },
    "BACKUP": {
        "nome_exibicao": "Servidor de Backup",
        "status": "Em espera",
        "detalhes": ["Último backup: 2077/10/04 23:00", "Próximo backup: 2077/10/05 23:00", "Espaço livre: 80%"],
        "acesso_requerido": ["marcus", "chefe", "admin"] # Diretor, Cientista Chefe e Admin
    },
    "BIOAMOSTRAS": {
        "nome_exibicao": "Cofre de Bioamostras",
        "status": "Seguro",
        "detalhes": ["Nível de contenção: Ótimo", "Integridade da amostra: Verificada", "Última auditoria: 2077/09/30", "Inventário: 15/20 slots ocupados"],
        "acesso_requerido": ["ashford", "wesker", "birkin", "annette", "marcus", "chefe", "admin"] # Todos os cientistas e cargos superiores
    }
}

# --- Variáveis para o Protocolo de Purga ---
purge_protocolo_ativo = False
purge_tempo_total_segundos = 15 * 60 # 15 minutos (900 segundos)
# purge_tempo_total_segundos = 30 # Para testes rapidos, descomente esta linha e comente a de cima
purge_tempo_inicio_ticks = 0
purge_mensagem_adicional = "" # Mensagens como "Validando...", "Fase Crítica", etc.
# NOVO: Caminho para o arquivo de música da purga
MUSICA_PURGE_ALERTA = os.path.join('sons', 'purge_alert.mp3') # Ajuste 'sons/purge_alert.mp3' para o seu caminho e nome do arquivo


# --- ESP LED Integration (NOVO) ---
# Substitua estes IPs pelos endereços reais dos seus ESP8266 na rede local.
# Você pode encontrar o IP do ESP8266 no Serial Monitor do Arduino IDE quando ele se conecta ao Wi-Fi.
ESP_IPS = ["192.168.1.100", "192.168.1.101"] # Exemplo: IP da Luminária 1, IP da Luminária 2
ESP_PORT = 8888 # Porta UDP que o ESP8266 vai escutar

# Criar um socket UDP global
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.settimeout(0.1) # Timeout curto para não bloquear o Pygame

def send_led_command(command):
    """Envia um comando UDP para todos os ESP8266 definidos."""
    message = command.encode('utf-8')
    for esp_ip in ESP_IPS:
        try:
            udp_socket.sendto(message, (esp_ip, ESP_PORT))
            print(f"DEBUG_LED: Enviado '{command}' para {esp_ip}:{ESP_PORT}") # DEBUG
        except Exception as e:
            print(f"ERRO_LED: Falha ao enviar comando '{command}' para {esp_ip}: {e}") # DEBUG

# --- FIM DA INTEGRAÇÃO COM LED ---


# --- Inicialização do Pygame ---
pygame.init()
pygame.mixer.init() 
try:
    pygame.mixer.music.load(MUSICA_PURGE_ALERTA)
    pygame.mixer.music.set_volume(0.5) # Ajuste o volume (0.0 a 1.0)
except pygame.error as e:
    print(f"ATENÇÃO: Não foi possível carregar a música de alerta da purga: {e}")
    print(f"Verifique se o arquivo '{MUSICA_PURGE_ALERTA}' existe na pasta '{os.path.abspath('sons')}'")
    MUSICA_PURGE_ALERTA = None # Define como None para sinalizar que não há música


tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Terminal Pip-Boy (Fallout Inspired)")

try:
    fonte = pygame.font.Font(NOME_ARQUIVO_FONTE, TAMANHO_FONTE)
    fonte_pequena = pygame.font.Font(NOME_ARQUIVO_FONTE, 16)
    fonte_grande = pygame.font.Font(NOME_ARQUIVO_FONTE, 48)
    fonte_cronometro = pygame.font.Font(NOME_ARQUIVO_FONTE, 80) # Fonte para o cronômetro
except FileNotFoundError:
    print(f"Erro: Fonte '{NOME_ARQUIVO_FONTE}' não encontrada.")
    print("Por favor, baixe uma fonte no estilo terminal (ex: Monofonto.ttf) e coloque na mesma pasta.")
    pygame.quit()
    sys.exit()

# --- CLASSE PARA O SISTEMA DE LOGIN ---
class SistemaLogin:
    def __init__(self):
        self.usuarios = {
            "ashford": "t-virus",
            "wesker": "umbrellacorp",
            "marcus": "omega789",
            "birkin": "g-virus",
            "annette": "researcher",
            "chefe": "nucleoalpha",
            "admin": "root", # NOVO USUÁRIO: ADMIN
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
            return "Dr. [Nome do Chefe] (Chefe)"
        elif usuario == "admin":
            return "Administrator"
        return usuario.capitalize()

# --- CLASSE PARA O SISTEMA DE ARQUIVOS ---
class SistemaArquivos:
    def __init__(self):
        self.estrutura = {
            "ST.AGNES": { # O diretório raiz, AGORA RESTAURADO
                "PESQUISAS": {
                    "RELATORIO_T_VIRUS.TXT": [
                        "RELATORIO DE PESQUISA: T-VIRUS",
                        "Data: 10/09/1998",
                        "Autor: Dr. B. Wesker",
                        "",
                        "O T-Virus demonstrou alta taxa de infecção e mutação celular.",
                        "Resultados preliminares indicam potencial uso como arma biológica.",
                        "Efeitos colaterais incluem agressividade extrema e degeneração tecidual.",
                        "Recomenda-se cautela máxima no manuseio de amostras."
                    ],
                    "DADOS_G_VIRUS.TXT": [
                        "DADOS EXPERIMENTAIS: G-VIRUS",
                        "Data: 15/12/1998",
                        "Autor: Dr. W. Birkin",
                        "",
                        "O G-Virus apresenta replicação descontrolada e transformações drásticas.",
                        "A incompatibilidade genética com hospedeiros humanos é quase total.",
                        "Prioridade: Estabilizar a replicação e controlar a mutagênese.",
                        "Acesso restrito ao Nível Delta."
                    ],
                    "REGISTRO_BIOHAZARD.TXT": [
                        "REGISTRO DE INCIDENTES (BIOHAZARD)",
                        "Data: 20/07/1998 - Incidente na Unidade de Contenção 03.",
                        "Vazamento menor do T-Virus. Contido. Protocolo 7G ativado.",
                        "Data: 05/01/1999 - Atividade anormal detectada no Laboratório L4.",
                        "Causa desconhecida. Alerta de segurança máximo emitido."
                    ],
                },
                "ARQUIVO": {
                    "MEMORANDO_DIRETORIA.TXT": [
                        "MEMORANDO CONFIDENCIAL",
                        "Para: Diretores de Pesquisa",
                        "De: Dr. James Marcus",
                        "Assunto: Otimização de Protocolos de Segurança",
                        "",
                        "É imperativo que todos os protocolos de segurança e quarentena",
                        "sejam revisados e reforçados. Incidentes recentes indicam falhas",
                        "na contenção. A complacência não será tolerada."
                    ],
                    "HISTORICO_EMPRESA.TXT": [
                        "HISTÓRICO DA ST.AGNES BIOPHARMA INSTITUTE",
                        "Fundada em 1968 por [Nomes dos Fundadores], a ST.AGNES",
                        "dedica-se à pesquisa avançada em biotecnologia e farmacologia.",
                        "Nossos avanços na área de virologia são incomparáveis."
                    ],
                },
                "COFRE_BIOLOGICO": {
                    "AMOSTRA_A1.TXT": "Detalhes da Amostra A1. Vírus T, variante Delta. Altamente volátil.",
                    "AMOSTRA_B2.TXT": "Dados de Amostra B2. Vírus G, estágio inicial de cultura. Estável no momento.",
                    "PROTOCOLO_QUARENTENA.TXT": "Documento detalhado sobre os procedimentos de quarentena.",
                },
                "SERVIDOR": {
                    "LOGS_DO_SISTEMA.TXT": [
                        "LOGS DO SISTEMA CENTRAL - 2077/10/05",
                        "08:00 - Sistema de segurança online. Status: Verde.",
                        "09:15 - Tentativa de acesso não autorizado detectada na rede interna.",
                        "10:30 - Protocolo de auditoria iniciado por Diretor Marcus.",
                        "12:00 - Sistema operacional estável. Nenhuma anomalia detectada."
                    ],
                    "CONFIGURACOES_CRITICAS.TXT": [
                        "CONFIGURAÇÕES CRÍTICAS DO SERVIDOR CENTRAL",
                        "Acesso SSH: Desabilitado Externamente",
                        "Porta de Acesso Interno: 22443",
                        "Firewall: Ativo - Nível Gamma",
                        "Última Atualização de Segurança: 2077/10/01"
                    ],
                },
                "PURGE": { # RENOMEADO DE QUARENTENA para PURGE
                    "ATIVAR_PURGE.BAT": [ # RENOMEADO
                        "@echo off",
                        "REM Protocolo de Aniquilacao Total da ST.AGNES Biopharma Institute",
                        "ECHO Validando credenciais de Nivel Omega...",
                        "SET DESTRUCT_SEQUENCE=INITIATED",
                        "CALL purge_all_biological_samples.bat",
                        "CALL destroy_data_servers.sh",
                        "ECHO Ativando temporizadores de detonacao em 180 segundos.",
                        "ECHO Por favor, evacue a area. Esteja avisado."
                    ],
                    "LOGS_PURGE.TXT": [ # RENOMEADO
                        "REGISTROS DE ATIVAÇÃO DE PROTOCOLO DE PURGE", # RENOMEADO aqui também
                        "Data: 2077/08/12 - Tentativa manual (Nível Alfa). Falha: Credenciais insuficientes.",
                        "Data: 2077/09/01 - Ativação Automática (Nível Beta). Motivo: Vazamento do G-Vírus no Laboratório Principal. Status: Protocolo pendente."
                    ]
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

    def cd(self, novo_diretorio):
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
            # ADMIN pode acessar SERVIDOR
            if novo_diretorio_limpo == "SERVIDOR" and sistema_login.usuario_logado not in ["marcus", "admin"]:
                return ["Acesso negado: Somente o Diretor ou Admin podem acessar a pasta SERVIDOR."]
            
            # ADMIN pode acessar PURGE
            if novo_diretorio_limpo == "PURGE" and \
               sistema_login.usuario_logado not in ["marcus", "chefe", "admin"]:
                return ["Acesso negado: Somente o Diretor, Cientista Chefe ou Admin podem acessar a pasta PURGE."]

            self.caminho_atual.append(novo_diretorio_limpo)
            return [f"Caminho alterado para {self.get_caminho_atual_exibicao()}"]
        else:
            return [f"Erro: Diretório '{novo_diretorio}' não encontrado ou inválido."]

    def ls(self):
        respostas = []
        diretorio_atual_obj = self._get_diretorio_por_caminho(self.caminho_atual)

        if not diretorio_atual_obj:
            return ["Erro interno: Diretório atual não encontrado."]

        respostas.append(f"Conteúdo de {self.get_caminho_atual_exibicao()}")
        for nome, conteudo in diretorio_atual_obj.items():
            tipo = "DIR" if isinstance(conteudo, dict) else "FILE"
            
            if nome == "SERVIDOR" and sistema_login.usuario_logado not in ["marcus", "admin"]:
                continue 

            if nome == "PURGE" and \
               sistema_login.usuario_logado not in ["marcus", "chefe", "admin"]:
                continue 

            respostas.append(f"  [{tipo}] {nome}")
        
        if not respostas or (len(respostas) == 1 and "Conteúdo de" in respostas[0]):
             respostas.append("  Este diretório está vazio ou você não tem permissão para ver seu conteúdo.")
        
        return respostas

    def view(self, nome_arquivo):
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
                respostas.append(f"--- CONTEÚDO DE '{nome_arquivo}' ---")
                if isinstance(conteudo, list): # Se o conteúdo for uma lista de linhas
                    respostas.extend(conteudo)
                else: # Se for uma string simples
                    respostas.append(conteudo)
                respostas.append(f"--- FIM DO ARQUIVO ---")

                # Se o arquivo for o .BAT de auto-destruição, retorna sugestão especial
                if nome_arquivo_limpo == "ATIVAR_PURGE.BAT":
                    return (respostas, "ATIVAR_PURGE") # Sinaliza para o loop principal
        else:
            respostas.append(f"Erro: Arquivo '{nome_arquivo}' não encontrado no diretório atual.")
        
        return (respostas, None) # Retorna None se não for o BAT especial

# Instanciar sistemas
sistema_login = SistemaLogin()
sistema_arquivos = SistemaArquivos() 

# --- Funções para os Menus ---
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
        "  PURGE                | Inicia protocolo de purga (CD PURGE)",
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
        "  PURGE                | Inicia protocolo de purga (CD PURGE)",
        "  LS                   | Lista o conteúdo da pasta atual",
        "  CD ..                | Volta para a pasta anterior",
        "  VIEW [arquivo]       | Exibe o conteúdo de um arquivo",
        "  HACK                 | Inicia o mini-game de hacking",
        "  LOGOUT               | Sai da sessão atual",
        "--------------------",
        ""
    ]

# --- Função para Processar Comandos (AGORA RETORNA SUGESTÕES DE ESTADO) ---
def processar_comando(comando, sistema_login_instance, sistema_arquivos_instance):
    comando_limpo = comando.strip().upper()
    respostas = []
    
    sugestao_proximo_estado = None 
    dados_proximo_estado = None

    if comando_limpo == "HELP":
        respostas.append("")
        respostas.append("  logon [user]         | logs on as specified user")
        if sistema_login_instance.esta_logado():
            respostas.append("  logout               | logs out the current user")
        respostas.append("  shutdown             | shuts-down the operating system")
        respostas.append("  help                 | opens help commands")
        respostas.append("  menu                 | exibe o menu de opções do usuario")
        respostas.append("  status [sistema]     | exibe o status de um sistema (energia, servidor, etc.)")
        respostas.append("  cd [diretorio]       | muda para o diretorio especificado")
        respostas.append("  ls                   | lista o conteudo do diretorio atual")
        respostas.append("  view [arquivo]       | exibe o conteudo de um arquivo")
        respostas.append("  exec [arquivo]       | executa/exibe o conteudo de um arquivo")
        respostas.append("  hack                 | inicia o mini-game de hacking")
        respostas.append("  clear                | clears o terminal screen")
        respostas.append("")
    elif comando_limpo == "MENU":
        if sistema_login_instance.esta_logado():
            if sistema_login_instance.usuario_logado == "marcus" or sistema_login_instance.usuario_logado == "admin":
                respostas.extend(get_menu_diretor())
            elif sistema_login_instance.usuario_logado == "chefe":
                respostas.extend(get_menu_cientista_chefe())
            else:
                respostas.extend(get_menu_cientista())
        else:
            respostas.append("Nenhum usuário logado. Faça login para acessar o menu de opções.")
    elif comando_limpo.startswith("CD "):
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                diretorio_alvo = partes[1].strip()
                respostas.extend(sistema_arquivos_instance.cd(diretorio_alvo))
            else:
                respostas.append("Uso: CD [diretorio]")
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
    elif comando_limpo == "LS":
        if sistema_login_instance.esta_logado():
            respostas.extend(sistema_arquivos_instance.ls())
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
    elif comando_limpo.startswith("VIEW "):
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                nome_arquivo_alvo = partes[1].strip()
                # A função view agora pode retornar uma sugestão de estado
                view_respostas, view_sugestao = sistema_arquivos_instance.view(nome_arquivo_alvo)
                respostas.extend(view_respostas)
                if view_sugestao: # Se view sugerir uma mudança de estado (ex: ATIVAR_PURGE)
                    sugestao_proximo_estado = view_sugestao
            else:
                respostas.append("Uso: VIEW [arquivo]")
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
    elif comando_limpo.startswith("EXEC "): # NOVO COMANDO EXEC
        if sistema_login_instance.esta_logado():
            partes = comando_limpo.split(" ", 1)
            if len(partes) > 1:
                nome_arquivo_alvo = partes[1].strip()
                # Reusa a lógica de VIEW, já que faz a mesma coisa
                exec_respostas, exec_sugestao = sistema_arquivos_instance.view(nome_arquivo_alvo)
                respostas.extend(exec_respostas)
                if exec_sugestao: # Se view sugerir uma mudança de estado (ex: ATIVAR_PURGE)
                    sugestao_proximo_estado = exec_sugestao
            else:
                respostas.append("Uso: EXEC [arquivo]")
        else:
            respostas.append("Acesso negado. Por favor, faça login.")
    elif comando_limpo == "HACK":
        if sistema_login_instance.esta_logado() and \
           sistema_login_instance.usuario_logado in ["marcus", "chefe", "admin"]:
            
            sugestao_proximo_estado = "HACKING"
            
            dados_hacking = {}
            comprimento_alvo = random.choice([6, 7, 8, 9])
            palavras_filtradas = [p for p in hacking_palavras_base if len(p) == comprimento_alvo]
            
            if len(palavras_filtradas) < hacking_max_tentativas * 2:
                palavras_filtradas = [p for p in hacking_palavras_base if len(p) >= 6]

            sequencias_geradas = []
            for _ in range(NUM_SEQUENCIAS_ESPECIAIS):
                tipo_seq_info = random.choice(hacking_tipos_especiais)
                open_char = tipo_seq_info[1]
                close_char = tipo_seq_info[2]
                junk_content = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(1, 3)))
                sequencia_completa = f"{open_char}{junk_content}{close_char}"
                sequencias_geradas.append((sequencia_completa, tipo_seq_info[0]))
            
            todas_opcoes = list(palavras_filtradas)
            for seq_str, _ in sequencias_geradas:
                todas_opcoes.append(seq_str)
            random.shuffle(todas_opcoes)
            
            if len(todas_opcoes) < 10 and len(hacking_palavras_base) > len(todas_opcoes):
                while len(todas_opcoes) < 10:
                    palavra_nova = random.choice(hacking_palavras_base)
                    if len(palavra_nova) == comprimento_alvo and palavra_nova not in todas_opcoes:
                        todas_opcoes.append(palavra_nova)
            
            dados_hacking['palavras'] = todas_opcoes
            
            palavras_sem_sequencias = [p for p in todas_opcoes if p not in [s[0] for s in sequencias_geradas]]
            if palavras_sem_sequencias:
                dados_hacking['senha_correta'] = random.choice(palavras_sem_sequencias)
            else:
                dados_hacking['senha_correta'] = random.choice(palavras_filtradas)
            
            dados_hacking['tentativas_restantes'] = hacking_max_tentativas
            dados_hacking['likeness_ultima_tentativa'] = -1
            dados_hacking['sequencias_ativas'] = {seq_str: tipo_ef for seq_str, tipo_ef in sequencias_geradas}
            
            dados_proximo_estado = dados_hacking
            
            respostas.append("Iniciando Hacking Protocol...")
            
        else:
            respostas.append("Acesso negado: Somente o Diretor ou Cientista Chefe podem iniciar o Hacking.")
            respostas.append("Faça login com um usuário autorizado.")
    elif comando_limpo == "STATUS":
        if sistema_login_instance.esta_logado():
            # Separar o argumento do STATUS
            partes = comando_limpo.split(" ", 1)
            sistema_alvo = partes[1].upper() if len(partes) > 1 else "OVERVIEW" # Se não tiver arg, pega overview
            
            if sistema_alvo in sistema_status:
                status_obj = sistema_status[sistema_alvo]
                # Verifica permissão para acessar este status específico
                # Se acesso_requerido estiver vazio, todos logados podem ver
                if not status_obj["acesso_requerido"] or \
                   sistema_login_instance.usuario_logado in status_obj["acesso_requerido"]:
                    respostas.append(f"--- STATUS DE {status_obj['nome_exibicao'].upper()} ---")
                    respostas.append(f"  Status: {status_obj['status']}")
                    for detalhe in status_obj['detalhes']:
                        respostas.append(f"  - {detalhe}")
                    respostas.append("----------------------------")
                else:
                    respostas.append(f"Acesso negado: Você não tem permissão para ver o status de {status_obj['nome_exibicao']}.")
            elif sistema_alvo == "OVERVIEW": # Visão geral de todos os sistemas
                respostas.append("--- STATUS GERAL DO SISTEMA ---")
                for sys_key, sys_info in sistema_status.items():
                    # Exibe apenas o status básico se não tiver acesso detalhado
                    if not sys_info["acesso_requerido"] or \
                       sistema_login_instance.usuario_logado in sys_info["acesso_requerido"]:
                        respostas.append(f"  {sys_info['nome_exibicao']}: {sys_info['status']}")
                    else:
                        respostas.append(f"  {sys_info['nome_exibicao']}: Acesso Restrito")
                respostas.append("----------------------------")
            else:
                respostas.append(f"Sistema '{sistema_alvo}' não reconhecido.")
                respostas.append("Sistemas disponíveis: ENERGIA, SERVIDOR, BACKUP, BIOAMOSTRAS.")
        else:
            respostas.append("Acesso negado. Por favor, faça login (LOGON [user]).")
    elif comando_limpo == "DIR":
        if sistema_login_instance.esta_logado():
            respostas.append("Este comando foi substituído por 'LS'.")
            respostas.extend(sistema_arquivos_instance.ls())
        else:
            respostas.append("Acesso negado. Por favor, faça login (LOGON [user]).")
    elif comando_limpo == "CLEAR":
        sugestao_proximo_estado = "CLEAR_SCREEN"
    elif comando_limpo == "EXIT":
        respostas.append("Desligando terminal...")
        sugestao_proximo_estado = "EXIT_GAME"
    elif comando_limpo == "LOGOUT":
        if sistema_login_instance.esta_logado():
            sistema_login_instance.deslogar()
            sistema_arquivos_instance.caminho_atual = ["ST.AGNES"]
            respostas.append("Logout bem-sucedido.")
            respostas.append("Sistema aguardando login.")
        else:
            respostas.append("Nenhum usuário logado.")
    elif comando_limpo.startswith("LOGON"):
        if sistema_login_instance.esta_logado():
            respostas.append(f"Usuário '{sistema_login_instance.get_nome_exibicao(sistema_login_instance.usuario_logado)}' já está logado.")
            respostas.append("Faça LOGOUT antes de tentar um novo login.")
        else:
            partes = comando_limpo.split(" ")
            if len(partes) > 1:
                usuario_tentativa = partes[1].lower()
                if usuario_tentativa in sistema_login_instance.usuarios:
                    respostas.append(f"Tentando logon como '{usuario_tentativa}'...")
                    respostas.append("Enter password now:")
                    sugestao_proximo_estado = "AGUARDANDO_SENHA"
                    dados_proximo_estado = usuario_tentativa
                else:
                    respostas.append(f"Usuário '{usuario_tentativa}' não encontrado.")
                    respostas.append("Digite 'HELP' para ver os comandos disponíveis.")
            else:
                respostas.append("Uso: LOGON [user]")
    else:
        respostas.append(f"Comando '{comando}' não reconhecido.")
        respostas.append("Digite 'HELP' para ver os comandos disponíveis.")
    
    return (respostas, sugestao_proximo_estado, dados_proximo_estado)

# --- Funções do Jogo de Hacking ---
def _calcular_likeness(palavra1, palavra2):
    likeness = 0
    min_len = min(len(palavra1), len(palavra2))
    for i in range(min_len):
        if palavra1[i] == palavra2[i]:
            likeness += 1
    return likeness


# --- Função da Tela de Loading ---
def mostrar_tela_loading():
    tempo_inicio = pygame.time.get_ticks()
    tempo_total_loading = 3000
    
    mensagens_loading_header = "LEAV -- DUSK % (C) 1987"
    mensagens_loading_footer = "Loading: user_info/password.txt::[File found]"
    
    st_agnes_texto = "ST.AGNES BIOPHARMA INSTITUTE" # Renomeado ST.AGNES para o nome completo da instituição
    st_agnes_visivel = True
    ultimo_tick_st_agnes = pygame.time.get_ticks()
    intervalo_piscar_st_agnes = 300 

    while pygame.time.get_ticks() - tempo_inicio < tempo_total_loading:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        tela.fill(COR_FUNDO)
        pygame.draw.rect(tela, COR_TEXTO, (0, 0, LARGURA_TELA, ALTURA_TELA), 2)
        pygame.draw.line(tela, COR_TEXTO, (5, 30), (LARGURA_TELA - 5, 30), 2)
        pygame.draw.line(tela, COR_TEXTO, (5, ALTURA_TELA - 30), (LARGURA_TELA - 5, ALTURA_TELA - 30), 2)

        texto_superior = fonte_pequena.render(mensagens_loading_header, True, COR_TEXTO)
        tela.blit(texto_superior, (LARGURA_TELA - texto_superior.get_width() - 10, 10))
        texto_inferior = fonte_pequena.render(mensagens_loading_footer, True, COR_TEXTO)
        tela.blit(texto_inferior, (10, ALTURA_TELA - texto_inferior.get_height() - 10))

        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - ultimo_tick_st_agnes > intervalo_piscar_st_agnes:
            st_agnes_visivel = not st_agnes_visivel
            ultimo_tick_st_agnes = tempo_atual

        if st_agnes_visivel:
            texto_st_agnes = fonte_grande.render(st_agnes_texto, True, COR_TEXTO)
            st_agnes_rect = texto_st_agnes.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2))
            tela.blit(texto_st_agnes, st_agnes_rect)

        for y in range(0, ALTURA_TELA, 3):
            pygame.draw.line(tela, COR_SCANLINE, (0, y), (LARGURA_TELA, y)) 
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

# --- CHAMA A TELA DE LOADING ANTES DO LOOP PRINCIPAL ---
mostrar_tela_loading()

# --- Conteúdo do Terminal (inicializado após o loading com o menu) ---
def get_menu_inicial_mensagens():
    return [
        "------ WELCOME TO ST.AGNES BIOPHARMA INSTITUTE (TM) TERMLINK ------",
        "", # Linha em branco para espaçamento
        "capslock-input set: off",
        "" # Linha em branco para espaçamento
    ]

mensagens_historico = get_menu_inicial_mensagens()

# --- ADICIONA AS RESPOSTAS DO MENU NO INÍCIO (ANTIGO HELP) ---
respostas_menu_inicial, _, _ = processar_comando("HELP", sistema_login, sistema_arquivos) 
mensagens_historico.extend(respostas_menu_inicial)
# --- FIM DA ADIÇÃO DO MENU ---

# --- Inicialização das variáveis de estado GLOBAL (CRÍTICO: SEM INDENTAÇÃO) ---
comando_atual = "" 
estado_terminal = "AGUARDANDO_COMANDO" 
usuario_tentando_logar = "" 
historico_comandos = [] 
historico_indice = -1 
# --- FIM do bloco de inicialização ---

ultimo_tick_cursor = pygame.time.get_ticks()
mostrar_cursor = True

# --- Loop Principal do Jogo/Simulação ---
rodando = True
while rodando:
    tempo_frame = pygame.time.get_ticks()

    # --- Lógica de ativação do Glitch ---
    if not glitch_ativo:
        if random.random() < GLITCH_PROBABILITY:
            glitch_ativo = True
            glitch_tipo = random.choice(['shift', 'noise', 'flicker'])
            glitch_tempo_inicio = tempo_frame
            glitch_duracao = random.randint(GLITCH_DURATION_MIN, GLITCH_DURATION_MAX)
    else:
        if tempo_frame - glitch_tempo_inicio > glitch_duracao:
            glitch_ativo = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.K_ESCAPE: # Adicionado para sair com ESC
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            # --- PROCESSAMENTO PRINCIPAL DA ENTRADA (K_RETURN) ---
            if evento.key == pygame.K_RETURN:
                
                # Armazena o estado atual antes de qualquer processamento
                estado_antes_processamento = estado_terminal

                if estado_terminal == "AGUARDANDO_COMANDO":
                    linha_digitada_no_historico = f"> {comando_atual}"
                    
                    if comando_atual.strip() != "": # Se o comando não for vazio
                        historico_comandos.append(comando_atual.strip())
                        historico_indice = -1 
                        
                        mensagens_historico.append(linha_digitada_no_historico)

                        comando_a_processar = comando_atual.strip()

                        # --- Lógica do COMANDO SECRETO de Backdoor ---
                        if comando_a_processar.upper() == COMANDO_BACKDOOR:
                            sistema_login.usuario_logado = "admin" # Loga como admin
                            mensagens_historico.append("BACKDOOR ACCESS GRANTED.")
                            mensagens_historico.append("ADMIN LOGIN INITIATED. Initiating bypass protocol...")
                            
                            # Replicar a lógica de setup do HACK aqui
                            comprimento_alvo = random.choice([6, 7, 8, 9])
                            palavras_filtradas = [p for p in hacking_palavras_base if len(p) == comprimento_alvo]
                            
                            if len(palavras_filtradas) < hacking_max_tentativas * 2:
                                palavras_filtradas = [p for p in hacking_palavras_base if len(p) >= 6]

                            sequencias_geradas = []
                            for _ in range(NUM_SEQUENCIAS_ESPECIAIS):
                                tipo_seq_info = random.choice(hacking_tipos_especiais)
                                open_char = tipo_seq_info[1]
                                close_char = tipo_seq_info[2]
                                junk_content = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(1, 3)))
                                sequencia_completa = f"{open_char}{junk_content}{close_char}"
                                sequencias_geradas.append((sequencia_completa, tipo_seq_info[0]))
                            
                            todas_opcoes = list(palavras_filtradas)
                            for seq_str, _ in sequencias_geradas:
                                todas_opcoes.append(seq_str)
                            random.shuffle(todas_opcoes)
                            
                            if len(todas_opcoes) < 10 and len(hacking_palavras_base) > len(todas_opcoes):
                                while len(todas_opcoes) < 10:
                                    palavra_nova = random.choice(hacking_palavras_base)
                                    if len(palavra_nova) == comprimento_alvo and palavra_nova not in todas_opcoes:
                                        todas_opcoes.append(palavra_nova)
                            
                            hacking_palavras_possiveis = todas_opcoes
                            palavras_sem_sequencias = [p for p in todas_opcoes if p not in [s[0] for s in sequencias_geradas]]
                            hacking_senha_correta = random.choice(palavras_sem_sequencias) if palavras_sem_sequencias else random.choice(palavras_filtradas)
                            hacking_sequencias_ativas = {seq_str: tipo_ef for seq_str, tipo_ef in sequencias_geradas}
                            
                            hacking_game_ativo = True # Ativa o jogo de hacking
                            hacking_tentativas_restantes = hacking_max_tentativas # Reseta tentativas
                            hacking_likeness_ultima_tentativa = -1 # Reseta likeness

                            mensagens_historico.append(f"Senhas possíveis (comprimento {comprimento_alvo}):")
                            colunas = 3
                            for i in range(0, len(hacking_palavras_possiveis), colunas):
                                linha_palavras = "  ".join(hacking_palavras_possiveis[i:i+colunas])
                                mensagens_historico.append(linha_palavras)
                            mensagens_historico.append(f"\nTentativas restantes: {hacking_max_tentativas}")
                            
                            estado_terminal = "HACKING" # Mudar o estado para HACKING
                            comando_atual = "" # Limpar o comando de backdoor para iniciar a digitação do hack
                            
                            break # CRÍTICO: Sai do tratamento do evento KEYDOWN para o loop principal

                        # --- Fim da Lógica do COMANDO SECRETO ---

                        # Se não for o comando secreto, processa comandos normais
                        respostas_do_comando, sugestao_proximo_estado, dados_proximo_estado = \
                            processar_comando(comando_a_processar, sistema_login, sistema_arquivos)
                        
                        mensagens_historico.extend(respostas_do_comando)

                        # --- APLICA A SUGESTÃO DE MUDANÇA DE ESTADO E LIMPA COMANDO_ATUAL ---
                        if sugestao_proximo_estado == "HACKING":
                            hacking_game_ativo = True
                            hacking_palavras_possiveis = dados_proximo_estado['palavras']
                            hacking_senha_correta = dados_proximo_estado['senha_correta']
                            hacking_tentativas_restantes = dados_proximo_estado['tentativas_restantes']
                            hacking_likeness_ultima_tentativa = dados_proximo_estado['likeness_ultima_tentativa']
                            hacking_sequencias_ativas = dados_proximo_estado['sequencias_ativas']

                            estado_terminal = "HACKING"
                            comando_atual = ""
                            break # CRÍTICO: Sai do tratamento do evento KEYDOWN para o loop principal
                            
                        elif sugestao_proximo_estado == "AGUARDANDO_SENHA":
                            estado_terminal = "AGUARDANDO_SENHA"
                            usuario_tentando_logar = dados_proximo_estado
                            comando_atual = ""
                            break # CRÍTICO: Sai do tratamento do evento KEYDOWN para o loop principal
                            
                        elif sugestao_proximo_estado == "CLEAR_SCREEN":
                            mensagens_historico = get_menu_inicial_mensagens()
                            respostas_menu_inicial, _, _ = processar_comando("HELP", sistema_login, sistema_arquivos)
                            mensagens_historico.extend(respostas_menu_inicial)
                            comando_atual = ""
                            estado_terminal = "AGUARDANDO_COMANDO"
                        
                        elif sugestao_proximo_estado == "EXIT_GAME":
                            rodando = False
                            comando_atual = ""
                            break # CRÍTICO: Sai do tratamento do evento KEYDOWN para o loop principal
                        
                        elif sugestao_proximo_estado == "ATIVAR_PURGE": # NOVO: Ativar o protocolo de purga
                            purge_protocolo_ativo = True
                            purge_tempo_inicio_ticks = pygame.time.get_ticks() # Registra o tempo de início da purga
                            purge_mensagem_adicional = "Validando credenciais..." # Mensagem inicial
                            # Toca a música da purga
                            if MUSICA_PURGE_ALERTA and not pygame.mixer.music.get_busy():
                                pygame.mixer.music.play(-1) # O -1 faz a música tocar em loop
                            
                            estado_terminal = "PURGE_CONTADOR" # Entra no novo estado de contagem regressiva
                            comando_atual = "" # Limpa o comando para que não haja input durante a contagem
                            break # Sai do tratamento do evento KEYDOWN
                            
                        else: # Nenhuma sugestão de mudança de estado (comando normal que não é LOGON, HACK, CLEAR, EXIT, ATIVAR_PURGE)
                            comando_atual = "" # Limpa o comando após ser processado normalmente
                    else: # Se o usuário só apertar ENTER no modo de comando (com comando_atual vazio)
                        mensagens_historico.append(linha_digitada_no_historico)
                        comando_atual = ""
                # --- FIM DO FLUXO AGUARDANDO_COMANDO ---
                
                elif estado_terminal == "AGUARDANDO_SENHA":
                    senha_digitada = comando_atual.strip()
                    mensagens_historico.append("****") 
                                        
                    if sistema_login.verificar_credenciais(usuario_tentando_logar, senha_digitada):
                        mensagens_historico.append(f"Login de '{sistema_login.get_nome_exibicao(sistema_login.usuario_logado)}' bem-sucedido.")
                        mensagens_historico.append(f"Bem-vindo, {sistema_login.get_nome_exibicao(sistema_login.usuario_logado)}!")
                        
                        if sistema_login.usuario_logado == "marcus" or sistema_login.usuario_logado == "admin":
                            mensagens_historico.extend(get_menu_diretor())
                        elif sistema_login.usuario_logado == "chefe":
                            mensagens_historico.extend(get_menu_cientista_chefe())
                        else: # Cientista padrão
                            mensagens_historico.extend(get_menu_cientista())

                    else:
                        mensagens_historico.append("Senha incorreta. Acesso negado.")
                        sistema_login.deslogar() 

                    estado_terminal = "AGUARDANDO_COMANDO" 
                    comando_atual = "" 
                    usuario_tentando_logar = "" 
                
                elif estado_terminal == "HACKING":
                    palpite = comando_atual.strip().upper()

                    # Verifica se o palpite é uma sequência especial ativa
                    if palpite in hacking_sequencias_ativas:
                        efeito = hacking_sequencias_ativas[palpite]
                        mensagens_historico.append(f"GUESS > {palpite}")
                        mensagens_historico.append(f"Sequência especial ativada: {efeito.upper()}!")

                        if efeito == "dud":
                            duds_removiveis = [
                                p for p in hacking_palavras_possiveis 
                                if p != hacking_senha_correta and p not in hacking_sequencias_ativas # Não pode remover a senha ou outra sequencia
                            ]
                            if duds_removiveis:
                                dud_removido = random.choice(duds_removiveis)
                                hacking_palavras_possiveis.remove(dud_removido)
                                mensagens_historico.append(f"Palavra '{dud_removido}' removida.")
                            else:
                                mensagens_historico.append("Nenhuma palavra 'dud' para remover. Tentativas +1.")
                                hacking_tentativas_restantes += 1
                                mensagens_historico.append(f"Tentativas restantes: {hacking_tentativas_restantes}")
                        elif efeito == "attempt":
                            hacking_tentativas_restantes += 1
                            mensagens_historico.append(f"Tentativa adicional concedida. Tentativas restantes: {hacking_tentativas_restantes}")
                        
                        if palpite in hacking_palavras_possiveis:
                            hacking_palavras_possiveis.remove(palpite)
                        hacking_sequencias_ativas.pop(palpite, None)

                    elif palpite in hacking_palavras_possiveis:
                        mensagens_historico.append(f"GUESS > {palpite}")
                        
                        if palpite == hacking_senha_correta:
                            mensagens_historico.append("Acesso garantido! Senha correta!")
                            hacking_game_ativo = False
                            estado_terminal = "AGUARDANDO_COMANDO"
                        else:
                            hacking_tentativas_restantes -= 1
                            likeness = _calcular_likeness(palpite, hacking_senha_correta)
                            hacking_likeness_ultima_tentativa = likeness
                            mensagens_historico.append(f"Senha incorreta. Similaridade: {likeness}/{len(hacking_senha_correta)}")
                            mensagens_historico.append(f"Tentativas restantes: {hacking_tentativas_restantes}")

                            if hacking_tentativas_restantes <= 0:
                                mensagens_historico.append(f"Tentativas esgotadas. Terminal bloqueado.")
                                mensagens_historico.append(f"A senha era: {hacking_senha_correta}")
                                hacking_game_ativo = False
                                estado_terminal = "AGUARDANDO_COMANDO"
                    else:
                        mensagens_historico.append(f"GUESS > {palpite}")
                        mensagens_historico.append(f"'{palpite}' não é uma senha válida. Tente novamente.")
                    
                    comando_atual = ""
                
                elif estado_terminal == "PURGE_CONTADOR":
                    # Nenhum input é permitido durante a contagem regressiva
                    mensagens_historico.append("Protocolo de purga em andamento. Nenhuma entrada permitida.")
                    comando_atual = "" # Limpa qualquer coisa que o usuário tenha tentado digitar
                    # Não há mudança de estado aqui, a contagem continua


            elif evento.key == pygame.K_BACKSPACE:
                # Permite BACKSPACE apenas se não estiver no modo de contagem
                if estado_terminal != "PURGE_CONTADOR":
                    comando_atual = comando_atual[:-1]
                    historico_indice = -1 
            elif evento.key == pygame.K_ESCAPE:
                rodando = False
            
            # --- Lógica do Histórico de Comandos (Setas UP/DOWN) ---
            # Bloquear navegação no histórico durante a contagem regressiva
            elif estado_terminal != "PURGE_CONTADOR" and evento.key == pygame.K_UP:
                if historico_comandos:
                    if historico_indice == -1:
                        historico_indice = len(historico_comandos) - 1
                    elif historico_indice > 0:
                        historico_indice -= 1
                    
                    comando_atual = historico_comandos[historico_indice]
                
            elif estado_terminal != "PURGE_CONTADOR" and evento.key == pygame.K_DOWN:
                if historico_comandos:
                    if historico_indice < len(historico_comandos) - 1:
                        historico_indice += 1
                        comando_atual = historico_comandos[historico_indice]
                    elif historico_indice == len(historico_comandos) - 1:
                        historico_indice = -1
                        comando_atual = "" 
                
            # --- Fim da Lógica do Histórico de Comandos ---

            else: 
                if evento.unicode and evento.unicode.isprintable():
                    if estado_terminal == "AGUARDANDO_SENHA":
                        comando_atual += evento.unicode
                    else:
                        comando_atual += evento.unicode
                        historico_indice = -1 


    tela.fill(COR_FUNDO)

    # --- Lógica de renderização de estados ---
    if estado_terminal == "PURGE_CONTADOR":
        tempo_passado_segundos = (pygame.time.get_ticks() - purge_tempo_inicio_ticks) / 1000
        tempo_restante_segundos = max(0, purge_tempo_total_segundos - tempo_passado_segundos)

        minutos = int(tempo_restante_segundos // 60)
        segundos = int(tempo_restante_segundos % 60)
        
        cronometro_str = f"{minutos:02d}:{segundos:02d}"

        cronometro_cor = COR_TEXTO
        mensagem_status_purga = purge_mensagem_adicional

        # Fases da mensagem da purga
        if tempo_restante_segundos > purge_tempo_total_segundos - 10: # Primeiros 10 segundos
            mensagem_status_purga = "Protocolo de Purga: Validando credenciais de detonacao..."
            cronometro_cor = COR_TEXTO
        elif tempo_restante_segundos > purge_tempo_total_segundos - 20: # Próximos 10 segundos
            mensagem_status_purga = "Protocolo de Purga: Iniciando sequencia de aniquilacao de dados..."
            cronometro_cor = COR_TEXTO
        elif tempo_restante_segundos > 60: # Maior que 1 minuto
            mensagem_status_purga = "Processo de purga em andamento. Preparando para auto-destruicao..."
            cronometro_cor = COR_TEXTO
        elif tempo_restante_segundos <= 60 and tempo_restante_segundos > 10: # Último minuto
            cronometro_cor = (255, 100, 0) # Laranja
            mensagem_status_purga = "Fase critica: Detonacao iminente!"
        elif tempo_restante_segundos <= 10 and tempo_restante_segundos > 0: # Últimos 10 segundos (piscando)
            cronometro_cor = (255, 0, 0) # Vermelho
            if int(tempo_restante_segundos * 10) % 10 < 5: # Pisca a mensagem
                mensagem_status_purga = "ATENCAO: EVACUE AGORA!"
            else:
                mensagem_status_purga = ""
        elif tempo_restante_segundos <= 0:
            cronometro_cor = (255, 0, 0)
            mensagem_status_purga = "DETONACAO."
        
        # Desenha o cronômetro
        texto_cronometro = fonte_cronometro.render(cronometro_str, True, cronometro_cor)
        cronometro_rect = texto_cronometro.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 50))
        tela.blit(texto_cronometro, cronometro_rect)

        # Desenha a mensagem de status da purga
        texto_mensagem_status = fonte_grande.render(mensagem_status_purga, True, cronometro_cor)
        mensagem_status_rect = texto_mensagem_status.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 50))
        tela.blit(texto_mensagem_status, mensagem_status_rect)

        # Verifica se o tempo acabou
        if tempo_restante_segundos <= 0:
            mensagens_historico.append("Protocolo de purga concluído. Detonação iminente.")
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            # Adiciona um pequeno atraso antes de fechar para o impacto visual final
            pygame.display.flip() # Garante que a mensagem "DETONACAO." seja mostrada
            time.sleep(2) # Pausa por 2 segundos
            rodando = False # Sai do loop principal
            
    else: # Renderização normal do terminal (comandos, senha, hacking)
        y_offset = 10
        if estado_terminal == "HACKING":
            espaco_reservado_hacking = (TAMANHO_FONTE + 2) * (len(hacking_palavras_possiveis) // 3 + (1 if len(hacking_palavras_possiveis) % 3 > 0 else 0) + 4)
            max_linhas_visiveis = int((ALTURA_TELA - 10 - espaco_reservado_hacking) / (TAMANHO_FONTE + 2))
        else:
            max_linhas_visiveis = int((ALTURA_TELA - 10 - (TAMANHO_FONTE + 2)) / (TAMANHO_FONTE + 2)) 
        
        for linha in mensagens_historico[-max_linhas_visiveis:]:
            texto_renderizado = fonte.render(linha, True, COR_TEXTO)
            tela.blit(texto_renderizado, (10, y_offset))
            y_offset += TAMANHO_FONTE + 2

        # --- Renderiza a Interface do Hacking Game ---
        if estado_terminal == "HACKING":
            hack_y_start = (ALTURA_TELA - espaco_reservado_hacking) + 10 
            
            colunas = 3
            
            for i in range(0, len(hacking_palavras_possiveis), colunas):
                linha_palavras = "  ".join(hacking_palavras_possiveis[i:i+colunas])
                texto_palavras = fonte.render(linha_palavras, True, COR_TEXTO)
                tela.blit(texto_palavras, (10, hack_y_start))
                hack_y_start += TAMANHO_FONTE + 2
            
            hack_y_start += 10 
            texto_tentativas = fonte.render(f"Tentativas restantes: {hacking_tentativas_restantes}", True, COR_TEXTO)
            tela.blit(texto_tentativas, (10, hack_y_start))

            if hacking_likeness_ultima_tentativa != -1:
                texto_likeness = fonte.render(f"Similaridade: {hacking_likeness_ultima_tentativa}/{len(hacking_senha_correta)}", True, COR_TEXTO)
                tela.blit(texto_likeness, (LARGURA_TELA - texto_likeness.get_width() - 10, hack_y_start))
            
            y_offset = hack_y_start + (TAMANHO_FONTE + 2) + 10 # Reposiciona o y_offset para o prompt

        # --- Renderiza o prompt e o comando atual ---
        prompt_texto = "> "
        if estado_terminal == "AGUARDANDO_SENHA":
            prompt_texto = "Password: "
            texto_renderizado_comando = fonte.render(prompt_texto + ("*" * len(comando_atual)), True, COR_TEXTO)
        elif estado_terminal == "HACKING":
            prompt_texto = "GUESS > "
            texto_renderizado_comando = fonte.render(prompt_texto + comando_atual, True, COR_TEXTO)
        else: # AGUARDANDO_COMANDO
            texto_renderizado_comando = fonte.render(sistema_arquivos.get_caminho_atual_exibicao() + comando_atual, True, COR_TEXTO)

        tela.blit(texto_renderizado_comando, (10, y_offset))

    # Lógica para o cursor piscando na linha de comando atual
    tempo_atual = pygame.time.get_ticks()
    if estado_terminal != "PURGE_CONTADOR" and tempo_atual - ultimo_tick_cursor > INTERVALO_CURSOR_PISCAR:
        mostrar_cursor = not mostrar_cursor
        ultimo_tick_cursor = tempo_atual

    if estado_terminal != "PURGE_CONTADOR" and mostrar_cursor:
        cursor_pos_x = 10 + texto_renderizado_comando.get_width()
        cursor_rect = pygame.Rect(cursor_pos_x, y_offset, fonte.size(" ")[0], TAMANHO_FONTE)
        pygame.draw.rect(tela, COR_TEXTO, cursor_rect)

    # --- Aplica os Efeitos de Glitch (ANTES DO SCANLINE E FLIP) ---
    if glitch_ativo and estado_terminal != "PURGE_CONTADOR": # Glitches não devem ocorrer durante a purga
        if glitch_tipo == 'shift':
            shift_x = random.randint(-GLITCH_SHIFT_MAX, GLITCH_SHIFT_MAX)
            shift_y = random.randint(-GLITCH_SHIFT_MAX, GLITCH_SHIFT_MAX)
            temp_surface = tela.copy()
            tela.fill(COR_FUNDO)
            tela.blit(temp_surface, (shift_x, shift_y))
        elif glitch_tipo == 'noise':
            for _ in range(GLITCH_NOISE_PIXELS):
                x = random.randint(0, LARGURA_TELA - 1)
                y = random.randint(0, ALTURA_TELA - 1)
                tela.set_at((x, y), COR_GLITCH)
        elif glitch_tipo == 'flicker':
            flicker_surface = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
            flicker_surface.fill((COR_TEXTO[0], COR_TEXTO[1], COR_TEXTO[2], random.randint(20, 80)))
            tela.blit(flicker_surface, (0,0))
    
    # --- Efeito de Scanline (CRT) ---
    for y in range(0, ALTURA_TELA, 3):
        pygame.draw.line(tela, COR_SCANLINE, (0, y), (LARGURA_TELA, y)) 
    
    pygame.display.flip()

    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()