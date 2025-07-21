import os

# --- Configurações do Terminal ---
LARGURA_TELA = 800
ALTURA_TELA = 600
COR_FUNDO = (0, 0, 0)
COR_TEXTO = (0, 255, 0)
COR_SCANLINE = (0, 50, 0)
COR_GLITCH = (0, 100, 0)
COR_ALARME_CLARO = (255, 100, 0) # Laranja para alarmes não críticos
COR_ALARME_CRITICO = (255, 0, 0) # Vermelho para alarmes críticos

TAMANHO_FONTE = 24
INTERVALO_CURSOR_PISCAR = 500

# Caminho para sua fonte (certifique-se de que o arquivo .ttf esteja na pasta 'fontes')
NOME_ARQUIVO_FONTE = os.path.join('fontes', 'monofonto.ttf') 

# --- Configurações de Glitch ---
GLITCH_PROBABILITY = 0.005 # Probabilidade de um glitch ocorrer em um frame (0.0 a 1.0)
GLITCH_DURATION_MIN = 50   # Duração mínima de um glitch em milissegundos
GLITCH_DURATION_MAX = 200  # Duração máxima de um glitch em milissegundos
GLITCH_SHIFT_MAX = 5     # Deslocamento máximo em pixels para o glitch tipo 'shift'
GLITCH_NOISE_PIXELS = 100  # Número de pixels de ruído para o glitch tipo 'noise'

# --- Variáveis do Jogo de Hacking ---
HACKING_MAX_TENTATIVAS = 4 
HACK_RESTART_DURATION_MS = 10 * 1000 # Duração do atraso de reinício em milissegundos (10 segundos)

# Palavras base para o jogo de hacking
HACKING_PALAVRAS_BASE = [
    "ACIDO", "ALFA", "AMPLIFICAR", "ANALISE", "ARMA", "AMOSTRA", "ANTIVIRUS", "APOCALIPSE",
    "BACTERIA", "BETA", "BIOLOGICO", "CADEIA", "CELULA", "CLONE", "CODIGO", "CONTAMINAR",
    "CRIPTO", "DADOS", "DEFEITO", "DELTA", "DESATIVAR", "DOENCA", "ENZIMA", "EPIDEMIA",
    "ERRO", "EVOLUIR", "EXPERIMENTO", "FATOR", "FUNGOS", "GENOMA", "HIBRIDO", "IMUNE",
    "INFECCAO", "LABORATORIO", "MUTACAO", "NUCLEO", "OMEGA", "PARASITA", "PATOGENO",
    "PESQUISA", "PLASMIDEO", "QUIMICO", "RADIACAO", "REATIVAR", "REPLICA", "SANGUE",
    "SEGURANCA", "SINTESE", "SISTEMA", "SORO", "TOXINA", "VACINA", "VIRUS", "ZETA"
]

# Tipos de sequências especiais para o hacking game
HACKING_TIPOS_ESPECIAIS = [
    ("dud", "(", ")"),
    ("dud", "[", "]"),
    ("attempt", "{", "}"),
    ("attempt", "<", ">")
]
NUM_SEQUENCIAS_ESPECIAIS = 4

# --- Comando Secreto de Backdoor ---
COMANDO_BACKDOOR = ">>>OVERRIDE<<<" # A string exata para o backdoor

# --- STATUS DOS SISTEMAS (detalhes e permissões) ---
SISTEMA_STATUS = {
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
        "acesso_requerido": ["marcus", "admin", "tech"] # Diretor, Admin e Tech
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
    },
    "PURGE_PROTOCOLO": {
        "nome_exibicao": "Protocolo de Purga Geral",
        "status": "Inativo",
        "detalhes": ["Aguardando ativação.", "Requer credenciais de Nível Omega."],
        "acesso_requerido": ["marcus", "chefe", "admin"]
    },
    "SERVER_DESTRUCT": { 
        "nome_exibicao": "Protocolo de Destruição de Servidor",
        "status": "Inativo",
        "detalhes": ["Aguardando ativação.", "Requer credenciais de Nível Omega."],
        "acesso_requerido": ["tech", "admin"]
    }
}

# --- Caminhos dos Arquivos de Som ---
SOM_BOOT_UP = os.path.join('sons', 'boot_up.mp3')
SOM_ENTER_KEY = os.path.join('sons', 'enter_key.mp3')
SOM_VALID_COMMAND = os.path.join('sons', 'command_valid.mp3')
SOM_INVALID_COMMAND = os.path.join('sons', 'command_invalid.mp3')
SOM_LOGIN_SUCCESS = os.path.join('sons', 'login_success.mp3')
SOM_LOGIN_FAIL = os.path.join('sons', 'login_fail.mp3')
SOM_SHUTDOWN = os.path.join('sons', 'shutdown.mp3')
MUSICA_PURGE_ALERTA = os.path.join('sons', 'purge_alert.mp3')

# ALTERADO AQUI: Agora é uma lista de caminhos para as 3 músicas de SERVER_DESTRUCT
MUSICAS_SERVER_DESTRUCT_ALERTA = [os.path.join('sons', f'server_destruct_alert_{i}.mp3') for i in range(3)]


# --- Configurações de Protocolo de Autodestruição (Purge/Server Destruct) ---
PURGE_TEMPO_TOTAL_SEGUNDOS = 15 * 60 # 15 minutos (900 segundos)
# PURGE_TEMPO_TOTAL_SEGUNDOS = 30 # Para testes rapidos

# --- Configurações para a exibição das telas ---
TEMPO_TELA_INICIAL = 2 # Segundos que a tela inicial "Laboratório St.Agnes" fica visível antes de aguardar input
TEMPO_TELA_LOADING = 3 # Segundos que a tela de "Loading" fica visível

# --- Configurações das Luminárias ---
IP_LUMINARIA = "192.168.1.100" # <--- SUBSTITUA PELO IP DO SEU ESP8266/LUMINÁRIA (ex: "192.168.1.100")
PORTA_LUMINARIA = 8888        # Porta UDP que o ESP8266 estará escutando (ex: 8888)