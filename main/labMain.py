import pygame
import sys
import random
import os
import time

# Importar os módulos personalizados
import config
import systems
import menus_commands
import screens
import hacking_logic

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
except pygame.error as e:
    print(f"ATENÇÃO: Um ou mais sons não puderam ser carregados: {e}")
    print(f"Verifique se os arquivos de som existem na pasta '{os.path.abspath('sons')}'")
    # Define sons como None para evitar erros se não carregados
    for key in ['boot_up', 'enter_key', 'valid_command', 'invalid_command', 'login_success', 'login_fail', 'shutdown']:
        if key not in sounds:
            sounds[key] = None # Garante que a chave exista, mesmo que o som não esteja carregado

# Configurar tela
screen = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
pygame.display.set_caption("Terminal Pip-Boy (Fallout Inspired)")

# Funções auxiliares para tocar sons (usadas como callback para evitar dependências circulares)
def play_sound(sound_type):
    """Toca um som específico se ele foi carregado."""
    if sounds.get(sound_type):
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

    # --- Mensagens iniciais do histórico para LAB MAIN ---
    # Agora a função get_menu_inicial_mensagens() é para as instruções HELP e LOGON
    # As linhas de cabeçalho específicas do terminal são definidas aqui
    mensagens_historico = [
        "ST.AGNES BIOPHARMA INSTITUTE - TERMINAL INTERFACE V2.0",
        "COPYRIGHT (C) 2077 UMBRELLA CORP. ALL RIGHTS RESERVED.",
        "", # Espaço entre o cabeçalho e as instruções
    ]
    # Adiciona as mensagens de HELP e LOGON da função menus_commands
    mensagens_historico.extend(menus_commands.get_menu_inicial_mensagens()) 
    mensagens_historico.append("") # Adiciona uma linha em branco final para espaçamento

    # --- Chamada das Telas Iniciais ---
    # Agora passamos o texto principal da splash screen como argumento para mostrar_tela_inicial
    screens.mostrar_tela_inicial(screen, fonts, "ST.AGNES BIOPHARMA INSTITUTE") 
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
                                            pygame.mixer.music.load(config.MUSICA_PURGE_ALERTA)
                                            pygame.mixer.music.play(-1)
                                        estado_terminal = "PURGE_CONTADOR"
                                    elif sugestao_proximo_estado == "ATIVAR_SERVER_DESTRUCT":
                                        purge_protocolo_ativo = True
                                        purge_tempo_inicio_ticks = pygame.time.get_ticks()
                                        purge_mensagem_adicional = "Validando credenciais para Destruicao de Servidor..."
                                        protocolo_atual_nome = "SERVER_DESTRUCT"
                                        if sounds.get('purge_alert') and not pygame.mixer.music.get_busy():
                                            pygame.mixer.music.load(config.MUSICA_PURGE_ALERTA)
                                            pygame.mixer.music.play(-1)
                                        estado_terminal = "PURGE_CONTADOR"
                                    
                                    comando_atual = "" # Limpa comando após processamento
                            
                            else: # Se o usuário só apertar ENTER no modo de comando (com comando_atual vazio)
                                mensagens_historico.append(linha_digitada_no_historico)
                                comando_atual = ""
                                play_sound("invalid_command")
                        
                        elif estado_terminal == "AGUARDANDO_SENHA":
                            senha_digitada = comando_atual.strip().lower() # Senhas devem ser verificadas em lowercase
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
                                sistema_login.deslogar() # Desloga em caso de falha
                                play_sound("login_fail")

                            estado_terminal = "AGUARDANDO_COMANDO" # Retorna ao estado de comando após login ou falha
                            comando_atual = "" # Limpa o comando para o próximo input
                            usuario_tentando_logar = "" # Limpa o usuário que estava tentando logar
                        
                        elif estado_terminal == "HACKING":
                            palpite = comando_atual.strip().upper() # Hacking usa maiúsculas para comparação

                            # Lógica para sequências especiais (dud, attempt)
                            if palpite in hacking_sequencias_ativas:
                                efeito = hacking_sequencias_ativas[palpite]
                                mensagens_historico.append(f"GUESS > {palpite}")
                                mensagens_historico.append(f"Sequência especial ativada: {efeito.upper()}!")
                                play_sound("valid_command")

                                if efeito == "dud":
                                    # Tenta remover uma palavra aleatória que não seja a senha ou outra sequência especial
                                    duds_removiveis = [
                                        p for p in hacking_palavras_possiveis 
                                        if p != hacking_senha_correta and p not in hacking_sequencias_ativas # Não remove a senha ou outras sequências
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
                            hacking_sequencias_ativas.pop(palpite, None) # Remove do dicionário de ativas

                        elif palpite in hacking_palavras_possiveis: # Palpite é uma palavra normal
                            mensagens_historico.append(f"GUESS > {palpite}")
                            
                            if palpite == hacking_senha_correta:
                                mensagens_historico.append("Acesso garantido! Senha correta!")
                                play_sound("login_success")
                                hacking_game_ativo = False
                                estado_terminal = "AGUARDANDO_COMANDO"
                            else:
                                hacking_tentativas_restantes -= 1
                                likeness = hacking_logic._calcular_likeness(palpite, hacking_senha_correta) # Usa a função do hacking_logic
                                hacking_likeness_ultima_tentativa = likeness
                                mensagens_historico.append(f"Senha incorreta. Similaridade: {likeness}/{len(hacking_senha_correta)}")
                                mensagens_historico.append(f"Tentativas restantes: {hacking_tentativas_restantes}")
                                play_sound("invalid_command")

                                if hacking_tentativas_restantes <= 0: # Fim das tentativas
                                    if hack_initiated_by_backdoor: # Se foi por backdoor, reinicia
                                        mensagens_historico.append(f"Tentativas esgotadas. Terminal bloqueado.")
                                        mensagens_historico.append(f"A senha era: {hacking_senha_correta}")
                                        mensagens_historico.append(f"Reiniciando protocolo de hacking em {int(config.HACK_RESTART_DURATION_MS / 1000)} segundos...")
                                        play_sound("login_fail")
                                        
                                        hacking_game_ativo = False # Desativa o jogo de hacking atual
                                        estado_terminal = "HACK_RESTART_DELAY" # Transiciona para o estado de atraso
                                        hack_restart_delay_start_time = pygame.time.get_ticks()
                                        hack_initiated_by_backdoor = False # Reseta a flag para o próximo hack
                                    else: # Se foi hack normal, bloqueia permanentemente
                                        mensagens_historico.append(f"Tentativas esgotadas. TERMINAL BLOQUEADO.")
                                        mensagens_historico.append(f"A senha era: {hacking_senha_correta}")
                                        mensagens_historico.append("Este terminal requer reinicializacao manual para reativar.")
                                        play_sound("login_fail")
                                        
                                        hacking_game_ativo = False # Desativa o jogo de hacking
                                        estado_terminal = "TERMINAL_BLOQUEADO" # Bloqueio permanente
                                else: # Palpite não é reconhecido
                                    mensagens_historico.append(f"GUESS > {palpite}")
                                    mensagens_historico.append(f"'{palpite}' não é uma senha válida. Tente novamente.")
                                    play_sound("invalid_command")
                            
                            comando_atual = "" # Limpa comando após palpite

                    elif evento.key == pygame.K_BACKSPACE:
                        if comando_atual: # Só apaga se houver algo para apagar
                            comando_atual = comando_atual[:-1]
                            historico_indice = -1 
                    elif evento.key == pygame.K_UP:
                        if historico_comandos:
                            if historico_indice == -1: # Se não estava navegando, vai para o último comando
                                historico_indice = len(historico_comandos) - 1
                            elif historico_indice > 0: # Vai para o comando anterior
                                historico_indice -= 1
                            comando_atual = historico_comandos[historico_indice]
                        
                    elif evento.key == pygame.K_DOWN:
                        if historico_comandos:
                            if historico_indice < len(historico_comandos) - 1: # Vai para o próximo comando
                                historico_indice += 1
                                comando_atual = historico_comandos[historico_indice]
                            elif historico_indice == len(historico_comandos) - 1: # Se já estava no último, limpa
                                historico_indice = -1
                                comando_atual = "" 
                                
                    else: # Este é o bloco para caracteres digitáveis gerais
                        if evento.unicode and evento.unicode.isprintable():
                            if estado_terminal == "AGUARDANDO_SENHA":
                                comando_atual += evento.unicode
                            elif estado_terminal == "AGUARDANDO_COMANDO" or estado_terminal == "HACKING":
                                comando_atual += evento.unicode
                                historico_indice = -1


        # --- Renderização da Tela Baseada no Estado ---
        screen.fill(config.COR_FUNDO) # Limpa a tela a cada frame

        if estado_terminal == "PURGE_CONTADOR":
            current_time_ticks = pygame.time.get_ticks()
            screens.draw_purge_countdown_screen(screen, fonts, purge_tempo_inicio_ticks, protocolo_atual_nome, current_time_ticks)
            
            # Lógica de transição após o fim da contagem (re-checa aqui para garantir)
            tempo_passado_segundos = (current_time_ticks - purge_tempo_inicio_ticks) / 1000
            if tempo_passado_segundos >= config.PURGE_TEMPO_TOTAL_SEGUNDOS:
                mensagens_historico.append(f"Protocolo de {protocolo_atual_nome} concluído. Sistema desligando.")
                if pygame.mixer.music.get_busy(): # Para a música se estiver tocando
                    pygame.mixer.music.stop()
                play_sound("shutdown") # Toca o som de shutdown
                estado_terminal = "DESLIGANDO" # Transiciona para o desligamento
                shutdown_start_time = pygame.time.get_ticks()

        elif estado_terminal == "DESLIGANDO":
            current_time_ticks = pygame.time.get_ticks()
            screens.draw_shutdown_animation(screen, fonts, shutdown_start_time)
            
            # Transição final para reiniciar o loop externo
            tempo_desligamento_passado = (current_time_ticks - shutdown_start_time) / 1000
            if tempo_desligamento_passado >= 4.0: # Duração da animação de desligamento
                rodando = False # Sai do loop interno, permitindo que o loop externo reinicie

        elif estado_terminal == "TERMINAL_BLOQUEADO":
            screens.draw_terminal_blocked_screen(screen, fonts, tempo_frame) # tempo_frame é o current_time_ticks

        elif estado_terminal == "HACK_RESTART_DELAY":
            current_time_ticks = pygame.time.get_ticks()
            screens.draw_hack_restart_delay_screen(screen, fonts, hack_restart_delay_start_time, current_time_ticks)

            # Lógica de transição para reiniciar o hacking
            tempo_atraso_passado = (current_time_ticks - hack_restart_delay_start_time) / 1000
            if tempo_atraso_passado >= config.HACK_RESTART_DURATION_MS / 1000:
                # Reinicializa o hacking game
                dados_hacking = hacking_logic.initialize_hacking_game_data()
                hacking_game_ativo = True
                hacking_palavras_possiveis = dados_hacking['palavras']
                hacking_senha_correta = dados_hacking['senha_correta']
                hacking_tentativas_restantes = dados_hacking['tentativas_restantes']
                hacking_likeness_ultima_tentativa = dados_hacking['likeness_ultima_tentativa']
                hacking_sequencias_ativas = dados_hacking['sequencias_ativas']
                hack_initiated_by_backdoor = True # Hack por backdoor ao reiniciar

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
                
        else: # Renderização normal do terminal (AGUARDANDO_COMANDO, HACKING ativo com digitação)
            # Calcula o y_offset para o prompt fixo na parte inferior
            prompt_y_offset = config.ALTURA_TELA - (config.TAMANHO_FONTE + 10) 
            
            # Define a margem superior para o histórico
            top_margin_history = 10 

            # Calcula o número máximo de linhas do histórico que cabem entre a margem superior e o prompt
            max_linhas_visiveis_acima_prompt = int((prompt_y_offset - top_margin_history) / (config.TAMANHO_FONTE + 2)) 

            # Renderiza as mensagens do histórico, começando da margem superior
            for i, linha in enumerate(mensagens_historico[-max_linhas_visiveis_acima_prompt:]):
                texto_renderizado = fonts['normal'].render(linha, True, config.COR_TEXTO)
                screen.blit(texto_renderizado, (10, top_margin_history + i * (config.TAMANHO_FONTE + 2)))


            # --- Renderiza o prompt e o comando atual ---
            prompt_texto = "> "
            if estado_terminal == "AGUARDANDO_SENHA":
                prompt_texto = "Password: "
                texto_renderizado_comando = fonts['normal'].render(prompt_texto + ("*" * len(comando_atual)), True, config.COR_TEXTO)
            elif estado_terminal == "HACKING":
                prompt_texto = "GUESS > "
                texto_renderizado_comando = fonts['normal'].render(prompt_texto + comando_atual, True, config.COR_TEXTO)
            else: # AGUARDANDO_COMANDO
                texto_renderizado_comando = fonts['normal'].render(sistema_arquivos.get_caminho_atual_exibicao() + comando_atual, True, config.COR_TEXTO)

            screen.blit(texto_renderizado_comando, (10, prompt_y_offset))

            # Lógica para o cursor piscando na linha de comando atual
            tempo_atual = pygame.time.get_ticks()
            if estado_terminal not in ["PURGE_CONTADOR", "DESLIGANDO", "TERMINAL_BLOQUEADO", "HACK_RESTART_DELAY"] and mostrar_cursor:
                cursor_pos_x = 10 + texto_renderizado_comando.get_width()
                cursor_rect = pygame.Rect(cursor_pos_x, prompt_y_offset, fonts['normal'].size(" ")[0], config.TAMANHO_FONTE)
                pygame.draw.rect(screen, config.COR_TEXTO, cursor_rect)

            if tempo_atual - ultimo_tick_cursor > config.INTERVALO_CURSOR_PISCAR:
                mostrar_cursor = not mostrar_cursor
                ultimo_tick_cursor = tempo_atual

            # --- Aplica os Efeitos de Glitch (ANTES DO SCANLINE E FLIP) ---
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
            
            # --- Efeito de Scanline (CRT) ---
            for y in range(0, config.ALTURA_TELA, 3):
                pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
            
            pygame.display.flip()

            pygame.time.Clock().tick(60)

# Sai do loop externo apenas se a flag 'rodando' for False (indicando QUIT ou ESC)
# Se o loop interno termina por EXIT/SHUTDOWN/PURGE, ele reinicia o loop externo
if not rodando: 
    # Sai do 'while True' externo e encerra o programa
    pygame.quit()
    sys.exit()