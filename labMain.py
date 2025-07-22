import pygame
import sys
import random
import os
import time

# Tentar forçar o driver de vídeo para Windows, pode ajudar com tela preta
os.environ['SDL_VIDEODRIVER'] = 'windows'

# Importar os módulos personalizados
import config
import systems
import menus_commands
import screens
import hacking_logic
import luz_api 

# --- Inicialização do Pygame e Sons ---
pygame.init()
pygame.mixer.init()

# Carregar fontes (passadas como dicionário para as funções de tela/renderização)
try:
    fonts = {
        'normal': pygame.font.Font(config.NOME_ARQUIVO_FONTE, config.TAMANHO_FONTE),
        'pequena': pygame.font.Font(config.NOME_ARQUIVO_FONTE, 16),
        'media': pygame.font.Font(config.NOME_ARQUIVO_FONTE, 36),
        'grande': pygame.font.Font(config.NOME_ARQUIVO_FONTE, 48),
        'cronometro': pygame.font.Font(config.NOME_ARQUIVO_FONTE, 80)
    }
except FileNotFoundError:
    print(f"Erro: Fonte '{config.NOME_ARQUIVO_FONTE}' não encontrada.")
    print("Por favor, baixe uma fonte no estilo terminal (ex: Monofonto.ttf) e coloque na pasta 'fontes'.")
    pygame.quit()
    sys.exit()

# Carregar sons (passados como dicionário para as funções de tela/renderização)
sounds = {}
try:
    sounds['boot_up'] = pygame.mixer.Sound(config.SOM_BOOT_UP)
    sounds['boot_up'].set_volume(0.6)
    sounds['enter_key'] = pygame.mixer.Sound(config.SOM_ENTER_KEY)
    sounds['enter_key'].set_volume(0.3)
    sounds['valid_command'] = pygame.mixer.Sound(config.SOM_VALID_COMMAND)
    sounds['valid_command'].set_volume(0.4)
    sounds['invalid_command'] = pygame.mixer.Sound(config.SOM_INVALID_COMMAND)
    sounds['invalid_command'].set_volume(0.4)
    sounds['login_success'] = pygame.mixer.Sound(config.SOM_LOGIN_SUCCESS)
    sounds['login_success'].set_volume(0.5)
    sounds['login_fail'] = pygame.mixer.Sound(config.SOM_LOGIN_FAIL)
    sounds['login_fail'].set_volume(0.5)
    sounds['shutdown'] = pygame.mixer.Sound(config.SOM_SHUTDOWN)
    sounds['shutdown'].set_volume(0.7)
    
    sounds['purge_alert'] = pygame.mixer.Sound(config.MUSICA_PURGE_ALERTA)
    sounds['purge_alert'].set_volume(0.5) 
    
    # NÃO CARREGAMOS TODAS as músicas de server_destruct aqui para otimização.
    # Elas serão carregadas dinamicamente quando play_sound('server_destruct_alert_random') for chamado.
    
except pygame.error as e:
    print(f"ATENÇÃO: Um ou mais sons não puderam ser carregados: {e}")
    print(f"Verifique se os arquivos de som existem na pasta '{os.path.abspath('sons')}'")
    # Define sons como None para evitar erros se não carregados
    for key in ['boot_up', 'enter_key', 'valid_command', 'invalid_command', 'login_success', 'login_fail', 'shutdown', 'purge_alert']:
        if key not in sounds:
            sounds[key] = None 

# Configurar tela
screen = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
pygame.display.set_caption("Terminal Pip-Boy (Fallout Inspired)")

# Funções auxiliares para tocar sons (usadas como callback para evitar dependências circulares)
def play_sound(sound_type):
    """
    Toca um som específico se ele foi carregado.
    Para 'server_destruct_alert_random', sorteia uma música e a carrega dinamicamente.
    """
    if sound_type == 'server_destruct_alert_random': 
        if config.MUSICAS_SERVER_DESTRUCT_ALERTA: # Verifica se a lista de caminhos não está vazia
            random_music_path = random.choice(config.MUSICAS_SERVER_DESTRUCT_ALERTA)
            try:
                if pygame.mixer.music.get_busy(): # Para a música atual se estiver tocando
                    pygame.mixer.music.stop()
                pygame.mixer.music.load(random_music_path) # Carrega a música aleatória
                pygame.mixer.music.play(-1) # Toca em loop
                print(f"DEBUG: Tocando música de SERVER_DESTRUCT aleatória: {random_music_path}") # Debug para confirmar qual tocou
            except pygame.error as e:
                print(f"AVISO: Não foi possível carregar ou tocar a música '{random_music_path}': {e}")
        else:
            print("AVISO: Nenhuma música de server_destruct definida em config.MUSICAS_SERVER_DESTRUCT_ALERTA para tocar.")
    elif sound_type == 'purge_alert': 
        if sounds.get('purge_alert'):
            if pygame.mixer.music.get_busy(): 
                pygame.mixer.music.stop()
            pygame.mixer.music.load(config.MUSICA_PURGE_ALERTA) 
            pygame.mixer.music.play(-1)
        else:
            print("AVISO: Música de purge_alert não carregada para tocar.")
    elif sounds.get(sound_type): # Para todos os outros sons (boot_up, enter_key, etc.)
        if pygame.mixer.music.get_busy(): # Para a música de fundo se estiver tocando (para outros sons pequenos)
            pygame.mixer.music.stop()
        sounds[sound_type].play()
    # Todas as variáveis globais que podem ser MODIFICADAS NESTE BLOCO de KEYDOWN.
    global comando_atual, estado_terminal, usuario_tentando_logar, \
    historico_comandos, historico_indice, \
    hacking_game_ativo, hacking_palavras_possiveis, hacking_senha_correta, \
    hacking_tentativas_restantes, hacking_likeness_ultima_tentativa, hacking_sequencias_ativas, \
    purge_protocolo_ativo, purge_tempo_inicio_ticks, purge_mensagem_adicional, protocolo_atual_nome, \
    shutdown_start_time, hack_initiated_by_backdoor, hack_restart_delay_start_time
# --- LOOP PRINCIPAL DO PROGRAMA (ENGLOBANDO TUDO PARA REINICIALIZAÇÃO) ---
while True: # Loop externo para reiniciar o terminal completamente

    # --- Variáveis de Estado do Jogo (Resetadas a cada reinício do terminal) ---
    comando_atual = "" 
    estado_terminal = "AGUARDANDO_COMANDO" # Estado inicial após o boot
    usuario_tentando_logar = "" 
    historico_comandos = [] # Armazena comandos digitados
    historico_indice = -1 # Para navegação no histórico (UP/DOWN)
    
    # Variáveis do Hacking Game
    hacking_game_ativo = False
    hacking_palavras_possiveis = []
    hacking_senha_correta = ""
    hacking_tentativas_restantes = 0
    hacking_likeness_ultima_tentativa = -1 
    hack_initiated_by_backdoor = False # True se o hack foi iniciado via backdoor
    hack_restart_delay_start_time = 0 
    hacking_sequencias_ativas = {} 
    
    # Variáveis de Glitch
    glitch_ativo = False
    glitch_tipo = None
    glitch_tempo_inicio = 0
    glitch_duracao = 0

    # Variáveis do Protocolo de Purga
    purge_protocolo_ativo = False
    purge_tempo_inicio_ticks = 0
    purge_mensagem_adicional = "" 
    protocolo_atual_nome = "" 
    
    # Variáveis de Desligamento
    shutdown_start_time = 0 

    # Re-instanciar sistemas para garantir estado limpo
    sistema_login = systems.SistemaLogin()
    sistema_arquivos = systems.SistemaArquivos() 

    # --- Mensagens iniciais do histórico para LAB MAIN (ST.AGNES) ---
    mensagens_historico = [
        "ST.AGNES BIOPHARMA INSTITUTE - TERMINAL INTERFACE V2.0",
        "COPYRIGHT (C) 2077 UMBRELLA CORP. ALL RIGHTS RESERVED.",
        "", # Espaço entre o cabeçalho e as instruções
    ]
    # Adiciona as mensagens de HELP e LOGON da função menus_commands
    mensagens_historico.extend(menus_commands.get_menu_inicial_mensagens()) 
    mensagens_historico.append("") # Adiciona uma linha em branco final para espaçamento

    # --- Chamada das Telas Iniciais ---
    screens.mostrar_tela_inicial(screen, fonts, "ST.AGNES BIOPHARMA INSTITUTE") # Título específico do Laboratório
    screens.mostrar_tela_loading(screen, fonts, sounds)

    # CRÍTICO: Limpar a fila de eventos APÓS as telas iniciais
    pygame.event.clear() 
    print("DEBUG_MAIN: Fila de eventos do Pygame limpa após telas iniciais. Pronto para input do usuário.") 

    ultimo_tick_cursor = pygame.time.get_ticks()
    mostrar_cursor = True

    rodando = True # Flag para o loop interno do jogo (sessão atual do terminal)

    while rodando:
        tempo_frame = pygame.time.get_ticks()

        # --- Lógica de ativação do Glitch ---
        if not glitch_ativo:
            if random.random() < config.GLITCH_PROBABILITY:
                glitch_ativo = True
                glitch_tipo = random.choice(['shift', 'noise', 'flicker'])
                glitch_tempo_inicio = tempo_frame
                glitch_duracao = random.randint(config.GLITCH_DURATION_MIN, config.GLITCH_DURATION_MAX)
        else:
            if tempo_frame - glitch_tempo_inicio > glitch_duracao:
                glitch_ativo = False

        for evento in pygame.event.get():
            # Processamento de eventos globais (QUIT, ESCAPE)
            if evento.type == pygame.QUIT:
                rodando = False # Sai do loop interno
            elif evento.type == pygame.K_ESCAPE: # Atalho para sair (ESC)
                if estado_terminal in ["DESLIGANDO", "TERMINAL_BLOQUEADO"]:
                    rodando = False # Sai do loop interno
                else:
                    rodando = False # Sai do loop interno
            elif evento.type == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_ALT: # Alt+Left para sair
                rodando = False
            elif evento.type == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_ALT: # Alt+Right para sair
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                # --- Processamento de Entrada de Usuário (Baseado no Estado do Terminal) ---
                if estado_terminal not in ["PURGE_CONTADOR", "DESLIGANDO", "TERMINAL_BLOQUEADO", "HACK_RESTART_DELAY"]:
                    if evento.key == pygame.K_RETURN:
                        play_sound("enter_key") # Som de ENTER
                        
                        # Processar o comando ou a senha
                        if estado_terminal == "AGUARDANDO_COMANDO":
                            linha_digitada_no_historico = f"{sistema_arquivos.get_caminho_atual_exibicao()}{comando_atual}" # Adiciona o prompt ao histórico
                            if comando_atual.strip() != "": # Apenas adiciona ao histórico se algo foi digitado
                                historico_comandos.append(comando_atual.strip())
                                historico_indice = -1 
                                mensagens_historico.append(linha_digitada_no_historico)
                                
                                comando_a_processar = comando_atual.strip()

                                if comando_a_processar.upper() == config.COMANDO_BACKDOOR: # Comando secreto
                                    sistema_login.usuario_logado = "admin"
                                    mensagens_historico.append("BACKDOOR ACCESS GRANTED.")
                                    mensagens_historico.append("ADMIN LOGIN INITIATED. Initiating bypass protocol...")
                                    
                                    # Inicializa o hacking game para o backdoor
                                    dados_hacking = hacking_logic.initialize_hacking_game_data()
                                    hacking_game_ativo = True
                                    hacking_palavras_possiveis = dados_hacking['palavras']
                                    hacking_senha_correta = dados_hacking['senha_correta']
                                    hacking_tentativas_restantes = dados_hacking['tentativas_restantes']
                                    hacking_likeness_ultima_tentativa = dados_hacking['likeness_ultima_tentativa']
                                    hacking_sequencias_ativas = dados_hacking['sequencias_ativas']
                                    hack_initiated_by_backdoor = True # Flag para indicar hack por backdoor

                                    mensagens_historico.append(f"Senhas possíveis (comprimento {len(hacking_senha_correta)}):")
                                    colunas = 3
                                    for i in range(0, len(hacking_palavras_possiveis), colunas):
                                        linha_palavras = "  ".join(hacking_palavras_possiveis[i:i+colunas])
                                        mensagens_historico.append(linha_palavras)
                                    mensagens_historico.append(f"\nTentativas restantes: {config.HACKING_MAX_TENTATIVAS}")
                                    
                                    estado_terminal = "HACKING"
                                    comando_atual = "" # Limpa o comando do backdoor
                                    play_sound("valid_command")
                                    
                                else: # Processa comandos normais
                                    # processar_comando retorna sugestão de estado e dados extras
                                    respostas_do_comando, sugestao_proximo_estado, dados_proximo_estado, sugestao_som_tocar = \
                                        menus_commands.processar_comando(comando_a_processar, sistema_login, sistema_arquivos, play_sound)
                                    
                                    mensagens_historico.extend(respostas_do_comando)
                                    play_sound(sugestao_som_tocar)

                                    # Aplica sugestão de mudança de estado
                                    if sugestao_proximo_estado == "HACKING":
                                        dados_hacking = hacking_logic.initialize_hacking_game_data() # Inicializa dados do hack
                                        hacking_game_ativo = True
                                        hacking_palavras_possiveis = dados_hacking['palavras']
                                        hacking_senha_correta = dados_hacking['senha_correta']
                                        hacking_tentativas_restantes = dados_hacking['tentativas_restantes']
                                        hacking_likeness_ultima_tentativa = dados_hacking['likeness_ultima_tentativa']
                                        hacking_sequencias_ativas = dados_hacking['sequencias_ativas']
                                        hack_initiated_by_backdoor = False # Hack normal
                                        estado_terminal = "HACKING"
                                        mensagens_historico.append(f"Senhas possíveis (comprimento {len(hacking_senha_correta)}):")
                                        colunas = 3
                                        for i in range(0, len(hacking_palavras_possiveis), colunas):
                                            linha_palavras = "  ".join(hacking_palavras_possiveis[i:i+colunas])
                                            mensagens_historico.append(linha_palavras)
                                        mensagens_historico.append(f"\nTentativas restantes: {config.HACKING_MAX_TENTATIVAS}")

                                    elif sugestao_proximo_estado == "AGUARDANDO_SENHA":
                                        estado_terminal = "AGUARDANDO_SENHA"
                                        usuario_tentando_logar = dados_proximo_estado
                                    elif sugestao_proximo_estado == "CLEAR_SCREEN":
                                        # Recarrega as mensagens iniciais para limpar a tela
                                        mensagens_historico = menus_commands.get_menu_inicial_mensagens()
                                        respostas_menu_inicial, _, _, _ = menus_commands.processar_comando("HELP", sistema_login, sistema_arquivos, play_sound) 
                                        mensagens_historico.extend(respostas_menu_inicial)
                                        estado_terminal = "AGUARDANDO_COMANDO"
                                    elif sugestao_proximo_estado == "EXIT_GAME":
                                        estado_terminal = "DESLIGANDO"
                                        shutdown_start_time = pygame.time.get_ticks()
                                    elif sugestao_proximo_estado == "ATIVAR_PURGE":
                                        purge_protocolo_ativo = True
                                        purge_tempo_inicio_ticks = pygame.time.get_ticks()
                                        purge_mensagem_adicional = "Validando credenciais para Protocolo de Purga..."
                                        protocolo_atual_nome = "PURGE"
                                        if sounds.get('purge_alert') and not pygame.mixer.music.get_busy():
                                            play_sound("purge_alert") 
                                        luz_api.ligar_piscar_vermelho() 
                                        estado_terminal = "PURGE_CONTADOR"
                                    elif sugestao_proximo_estado == "ATIVAR_SERVER_DESTRUCT":
                                        purge_protocolo_ativo = True
                                        purge_tempo_inicio_ticks = pygame.time.get_ticks()
                                        purge_mensagem_adicional = "Validando credenciais para Destruicao de Servidor..."
                                        protocolo_atual_nome = "SERVER_DESTRUCT"
                                        play_sound("server_destruct_alert_random") 
                                        luz_api.ligar_piscar_vermelho() 
                                        estado_terminal = "PURGE_CONTADOR"
                                    
                                    comando_atual = "" 
                            
                            else: 
                                mensagens_historico.append(linha_digitada_no_historico)
                                comando_atual = ""
                                play_sound("invalid_command")
                        
                        elif estado_terminal == "AGUARDANDO_SENHA":
                            senha_digitada = comando_atual.strip().lower() 
                            mensagens_historico.append("****") 
                            
                            if sistema_login.verificar_credenciais(usuario_tentando_logar, senha_digitada):
                                mensagens_historico.append(f"Login de '{sistema_login.get_nome_exibicao(sistema_login.usuario_logado)}' bem-sucedido.")
                                mensagens_historico.append(f"Bem-vindo, {sistema_login.get_nome_exibicao(sistema_login.usuario_logado)}!")
                                play_sound("login_success")
                                
                                if sistema_login.usuario_logado == "admin":
                                    mensagens_historico.extend(menus_commands.get_menu_admin())
                                elif sistema_login.usuario_logado == "marcus":
                                    mensagens_historico.extend(menus_commands.get_menu_diretor())
                                elif sistema_login.usuario_logado == "chefe":
                                    mensagens_historico.extend(menus_commands.get_menu_cientista_chefe())
                                elif sistema_login.usuario_logado == "tech":
                                    mensagens_historico.extend(menus_commands.get_menu_tech())
                                else: # Cientista padrão
                                    mensagens_historico.extend(menus_commands.get_menu_cientista())

                            else:
                                mensagens_historico.append("Senha incorreta. Acesso negado.")
                                sistema_login.deslogar() 
                                play_sound("login_fail")

                            estado_terminal = "AGUARDANDO_COMANDO" 
                            comando_atual = "" 
                            usuario_tentando_logar = "" 
                        
                        elif estado_terminal == "HACKING":
                            palpite = comando_atual.strip().upper() 

                            if palpite in hacking_sequencias_ativas:
                                efeito = hacking_sequencias_ativas[palpite]
                                mensagens_historico.append(f"GUESS > {palpite}")
                                mensagens_historico.append(f"Sequência especial ativada: {efeito.upper()}!")
                                play_sound("valid_command")

                                if efeito == "dud":
                                    duds_removiveis = [
                                        p for p in hacking_palavras_possiveis 
                                        if p != hacking_senha_correta and p not in hacking_sequencias_ativas 
                                    ]
                                    if duds_removiveis:
                                        dud_removido = random.choice(duds_removiveis)
                                        hacking_palavras_possiveis.remove(dud_removido)
                                        mensagens_historico.append(f"Palavra '{dud_removido}' removida da lista.")
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
                                    play_sound("login_success")
                                    hacking_game_ativo = False
                                    estado_terminal = "AGUARDANDO_COMANDO"
                                else:
                                    hacking_tentativas_restantes -= 1
                                    likeness = hacking_logic._calcular_likeness(palpite, hacking_senha_correta) 
                                    hacking_likeness_ultima_tentativa = likeness
                                    mensagens_historico.append(f"Senha incorreta. Similaridade: {likeness}/{len(hacking_senha_correta)}")
                                    mensagens_historico.append(f"Tentativas restantes: {hacking_tentativas_restantes}")
                                    play_sound("invalid_command")

                                    if hacking_tentativas_restantes <= 0: 
                                        if hack_initiated_by_backdoor: 
                                            mensagens_historico.append(f"Tentativas esgotadas. Terminal bloqueado.")
                                            mensagens_historico.append(f"A senha era: {hacking_senha_correta}")
                                            mensagens_historico.append(f"Reiniciando protocolo de hacking em\n{int(config.HACK_RESTART_DURATION_MS / 1000)} segundos...") 
                                            play_sound("login_fail")
                                            
                                            hacking_game_ativo = False 
                                            estado_terminal = "HACK_RESTART_DELAY" 
                                            hack_restart_delay_start_time = pygame.time.get_ticks()
                                            hack_initiated_by_backdoor = False 
                                        else: 
                                            mensagens_historico.append(f"Tentativas esgotadas. TERMINAL BLOQUEADO.")
                                            mensagens_historico.append("Este terminal requer\nreinicializacao manual para reativar.") 
                                            play_sound("login_fail")
                                            
                                            hacking_game_ativo = False 
                                            estado_terminal = "TERMINAL_BLOQUEADO" 
                            else: 
                                mensagens_historico.append(f"GUESS > {palpite}")
                                mensagens_historico.append(f"'{palpite}' não é uma senha válida. Tente novamente.")
                                play_sound("invalid_command")
                            
                            comando_atual = "" 

                    elif evento.key == pygame.K_BACKSPACE:
                        if comando_atual: 
                            comando_atual = comando_atual[:-1]
                            historico_indice = -1 
                    elif evento.key == pygame.K_UP:
                        if historico_comandos:
                            if historico_indice == -1: 
                                historico_indice = len(historico_comandos) - 1
                            elif historico_indice > 0: 
                                historico_indice -= 1
                            comando_atual = historico_comandos[historico_indice]
                        
                    elif evento.key == pygame.K_DOWN:
                        if historico_comandos:
                            if historico_indice < len(historico_comandos) - 1: 
                                historico_indice += 1
                                comando_atual = historico_comandos[historico_indice]
                            elif historico_indice == len(historico_comandos) - 1: 
                                historico_indice = -1
                                comando_atual = "" 
                                
                    else: 
                        if evento.unicode and evento.unicode.isprintable():
                            if estado_terminal == "AGUARDANDO_SENHA":
                                comando_atual += evento.unicode
                            elif estado_terminal == "AGUARDANDO_COMANDO" or estado_terminal == "HACKING":
                                comando_atual += evento.unicode
                                historico_indice = -1


        # --- Renderização da Tela Baseada no Estado ---
        screen.fill(config.COR_FUNDO) 

        if estado_terminal == "PURGE_CONTADOR":
            current_time_ticks = pygame.time.get_ticks()
            screens.draw_purge_countdown_screen(screen, fonts, purge_tempo_inicio_ticks, protocolo_atual_nome, current_time_ticks)
            
            tempo_passado_segundos = (current_time_ticks - purge_tempo_inicio_ticks) / 1000
            if tempo_passado_segundos >= config.PURGE_TEMPO_TOTAL_SEGUNDOS:
                mensagens_historico.append(f"Protocolo de {protocolo_atual_nome} concluído. Sistema desligando.")
                if pygame.mixer.music.get_busy(): 
                    pygame.mixer.music.stop()
                luz_api.desligar_piscar_vermelho() 
                
                play_sound("shutdown") 
                estado_terminal = "DESLIGANDO" 
                shutdown_start_time = pygame.time.get_ticks()

        elif estado_terminal == "DESLIGANDO":
            current_time_ticks = pygame.time.get_ticks()
            screens.draw_shutdown_animation(screen, fonts, shutdown_start_time)
            
            tempo_desligamento_passado = (current_time_ticks - shutdown_start_time) / 1000
            if tempo_desligamento_passado >= 4.0: 
                rodando = False 

        elif estado_terminal == "TERMINAL_BLOQUEADO":
            screens.draw_terminal_blocked_screen(screen, fonts, tempo_frame) 

        elif estado_terminal == "HACK_RESTART_DELAY":
            current_time_ticks = pygame.time.get_ticks()
            screens.draw_hack_restart_delay_screen(screen, fonts, hack_restart_delay_start_time, current_time_ticks)

            tempo_atraso_passado = (current_time_ticks - hack_restart_delay_start_time) / 1000
            if tempo_atraso_passado >= config.HACK_RESTART_DURATION_MS / 1000:
                dados_hacking = hacking_logic.initialize_hacking_game_data()
                hacking_game_ativo = True
                hacking_palavras_possiveis = dados_hacking['palavras']
                hacking_senha_correta = dados_hacking['senha_correta']
                hacking_tentativas_restantes = dados_hacking['tentativas_restantes']
                hacking_likeness_ultima_tentativa = dados_hacking['likeness_ultima_tentativa']
                hacking_sequencias_ativas = dados_hacking['sequencias_ativas']
                hack_initiated_by_backdoor = True 

                mensagens_historico.append("Reiniciando hacking...")
                mensagens_historico.append(f"Senhas possíveis (comprimento {len(hacking_senha_correta)}):")
                colunas = 3
                for i in range(0, len(hacking_palavras_possiveis), colunas):
                    linha_palavras = "  ".join(hacking_palavras_possiveis[i:i+colunas])
                    mensagens_historico.append(linha_palavras)
                mensagens_historico.append(f"\nTentativas restantes: {config.HACKING_MAX_TENTATIVAS}")

                estado_terminal = "HACKING"
                comando_atual = ""
                play_sound("valid_command")
                
        else: 
            prompt_y_offset = config.ALTURA_TELA - (config.TAMANHO_FONTE + 10) 
            
            top_margin_history = 10 

            max_linhas_visiveis_acima_prompt = int((prompt_y_offset - top_margin_history) / (config.TAMANHO_FONTE + 2)) 

            for i, linha in enumerate(mensagens_historico[-max_linhas_visiveis_acima_prompt:]):
                texto_renderizado = fonts['normal'].render(linha, True, config.COR_TEXTO)
                screen.blit(texto_renderizado, (10, top_margin_history + i * (config.TAMANHO_FONTE + 2)))


            prompt_texto = "> "
            if estado_terminal == "AGUARDANDO_SENHA":
                prompt_texto = "Password: "
                texto_renderizado_comando = fonts['normal'].render(prompt_texto + ("*" * len(comando_atual)), True, config.COR_TEXTO)
            elif estado_terminal == "HACKING":
                prompt_texto = "GUESS > "
                texto_renderizado_comando = fonts['normal'].render(prompt_texto + comando_atual, True, config.COR_TEXTO)
            else: 
                texto_renderizado_comando = fonts['normal'].render(sistema_arquivos.get_caminho_atual_exibicao() + comando_atual, True, config.COR_TEXTO)

            screen.blit(texto_renderizado_comando, (10, prompt_y_offset))

            tempo_atual = pygame.time.get_ticks()
            if estado_terminal not in ["PURGE_CONTADOR", "DESLIGANDO", "TERMINAL_BLOQUEADO", "HACK_RESTART_DELAY"] and mostrar_cursor:
                cursor_pos_x = 10 + texto_renderizado_comando.get_width()
                cursor_rect = pygame.Rect(cursor_pos_x, prompt_y_offset, fonts['normal'].size(" ")[0], config.TAMANHO_FONTE)
                pygame.draw.rect(screen, config.COR_TEXTO, cursor_rect)

            if tempo_atual - ultimo_tick_cursor > config.INTERVALO_CURSOR_PISCAR:
                mostrar_cursor = not mostrar_cursor
                ultimo_tick_cursor = tempo_atual

            if glitch_ativo and estado_terminal not in ["PURGE_CONTADOR", "DESLIGANDO", "TERMINAL_BLOQUEADO", "HACK_RESTART_DELAY"]:
                if glitch_tipo == 'shift':
                    shift_x = random.randint(-config.GLITCH_SHIFT_MAX, config.GLITCH_SHIFT_MAX)
                    shift_y = random.randint(-config.GLITCH_SHIFT_MAX, config.GLITCH_SHIFT_MAX)
                    temp_surface = screen.copy()
                    screen.fill(config.COR_FUNDO)
                    screen.blit(temp_surface, (shift_x, shift_y))
                elif glitch_tipo == 'noise':
                    for _ in range(config.GLITCH_NOISE_PIXELS):
                        x = random.randint(0, config.LARGURA_TELA - 1)
                        y = random.randint(0, config.ALTURA_TELA - 1)
                        screen.set_at((x, y), config.COR_GLITCH)
                elif glitch_tipo == 'flicker':
                    flicker_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                    flicker_surface.fill((config.COR_TEXTO[0], config.COR_TEXTO[1], config.COR_TEXTO[2], random.randint(20, 80)))
                    screen.blit(flicker_surface, (0,0))
            
            for y in range(0, config.ALTURA_TELA, 3):
                pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
            
            pygame.display.flip()

            pygame.time.Clock().tick(60)

if not rodando: 
    pygame.quit()
    sys.exit()