import pygame
import sys
import random
import time 

# Importa as configurações
import config

def mostrar_tela_inicial(screen, fonts, main_text):
    """Mostra a tela de boot inicial com o texto principal dinâmico."""
    tela_inicial_ativa = True
    while tela_inicial_ativa:
        screen.fill(config.COR_FUNDO)
        
        # Desenha a borda e as linhas de topo/base
        pygame.draw.rect(screen, config.COR_TEXTO, (0, 0, config.LARGURA_TELA, config.ALTURA_TELA), 2)
        pygame.draw.line(screen, config.COR_TEXTO, (5, 30), (config.LARGURA_TELA - 5, 30), 2)
        pygame.draw.line(screen, config.COR_TEXTO, (5, config.ALTURA_TELA - 30), (config.LARGURA_TELA - 5, config.ALTURA_TELA - 30), 2)

        # Cabeçalho e Rodapé copiados da tela de loading
        mensagens_header = "LEAV -- DUSK % (C) 1987"
        mensagens_footer = "Loading: user_info/password.txt::[File found]"
        
        texto_superior = fonts['pequena'].render(mensagens_header, True, config.COR_TEXTO)
        screen.blit(texto_superior, (config.LARGURA_TELA - texto_superior.get_width() - 10, 10))
        texto_inferior = fonts['pequena'].render(mensagens_footer, True, config.COR_TEXTO)
        screen.blit(texto_inferior, (10, config.ALTURA_TELA - texto_inferior.get_height() - 10))

        # --- ALTERADO AQUI: Posição Y do texto principal da tela inicial ---
        texto_principal = fonts['grande'].render(main_text, True, config.COR_TEXTO)
        # Ajustado para ALTURA_TELA // 4, a mesma posição que na tela de loading
        lab_rect = texto_principal.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 4)) 
        screen.blit(texto_principal, lab_rect)

        # "pressione qualquer tecla para iniciar"
        if int(pygame.time.get_ticks() / config.INTERVALO_CURSOR_PISCAR) % 2 == 0:
            texto_pressione = fonts['media'].render("pressione qualquer tecla para iniciar", True, config.COR_TEXTO)
            pressione_rect = texto_pressione.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA - 100))
            screen.blit(texto_pressione, pressione_rect)

        # Efeito de Scanline (CRT)
        for y in range(0, config.ALTURA_TELA, 3):
            pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                tela_inicial_ativa = False # Sai da tela inicial ao pressionar qualquer tecla

def mostrar_tela_loading(screen, fonts, sounds):
    """Exibe a tela de carregamento com o nome da empresa e mensagens de loading piscando."""
    sounds['boot_up'].play()

    tempo_inicio = pygame.time.get_ticks()
    tempo_total_loading = 3000 # Duração total da tela de loading
    
    mensagens_loading_header = "LEAV -- DUSK % (C) 1987"
    mensagens_loading_footer = "Loading: user_info/password.txt::[File found]"
    
    st_agnes_texto = "ST.AGNES BIOPHARMA INSTITUTE" # Nome da empresa (fixo nesta tela)
    
    # NOVAS MENSAGENS DE LOADING
    # Variáveis para o ciclo de mensagens do loading (aqui são locais da função)
    loading_messages = [
        "LOADING...",
        "LOADING EXPLOSIVES...",
        "LOADING ANTENAS...",
        "LOADING CRAZY S**T...",
    ]
    current_message_index = 0
    last_message_change_time = tempo_inicio # Usa tempo_inicio como o start
    message_state = "BLINKING" # "BLINKING" ou "FIXED"
    messages_fixed_on_screen = [] # Armazena as mensagens que já foram fixadas

    while pygame.time.get_ticks() - tempo_inicio < tempo_total_loading:
        screen.fill(config.COR_FUNDO)
        
        # Desenha a borda e as linhas de topo/base
        pygame.draw.rect(screen, config.COR_TEXTO, (0, 0, config.LARGURA_TELA, config.ALTURA_TELA), 2)
        pygame.draw.line(screen, config.COR_TEXTO, (5, 30), (config.LARGURA_TELA - 5, 30), 2)
        pygame.draw.line(screen, config.COR_TEXTO, (5, config.ALTURA_TELA - 30), (config.LARGURA_TELA - 5, config.ALTURA_TELA - 30), 2)

        # Mensagem da empresa (agora pisca)
        current_time = pygame.time.get_ticks()
        if current_time - last_message_change_time > config.INTERVALO_CURSOR_PISCAR: # Reutiliza a lógica de piscar
            # show_loading_text = not show_loading_text # Esta variável foi removida
            pass # A lógica de piscar agora é interna para cada mensagem no ciclo abaixo

        # Nome da empresa (permanece estático e visível)
        render_empresa = fonts['grande'].render(st_agnes_texto, True, config.COR_TEXTO)
        x_empresa = (config.LARGURA_TELA - render_empresa.get_width()) // 2
        y_empresa = config.ALTURA_TELA // 4 # Posição mais acima (igual a tela inicial)
        screen.blit(render_empresa, (x_empresa, y_empresa))


        # Lógica para ciclar as mensagens de loading
        # Gerencia a transição de mensagens e estado de piscar/fixar
        if current_time - last_message_change_time > config.AD_MESSAGE_BLINK_DURATION_MS + config.AD_PAUSE_BETWEEN_MESSAGES_MS:
            # Se a mensagem atual já foi processada (piscou e fixou)
            if current_message_index < len(loading_messages): # Se ainda há mensagens a serem processadas
                messages_fixed_on_screen.append(loading_messages[current_message_index]) # Fixa a mensagem atual
                current_message_index += 1 # Avança para a próxima
                last_message_change_time = current_time # Reseta o tempo para a próxima transição

        # Renderiza as mensagens já fixadas (do y_empresa para baixo)
        y_offset_loading_msgs = y_empresa + render_empresa.get_height() + 50 # Posição inicial abaixo do nome da empresa
        for i, msg in enumerate(messages_fixed_on_screen):
            rendered_msg = fonts['normal'].render(msg, True, config.COR_TEXTO)
            msg_rect = rendered_msg.get_rect(center=(config.LARGURA_TELA // 2, y_offset_loading_msgs + i * fonts['normal'].get_linesize()))
            screen.blit(rendered_msg, msg_rect)

        # Renderiza a mensagem atual (se ainda houver e no estado BLINKING)
        if current_message_index < len(loading_messages):
            current_loading_message_text = loading_messages[current_message_index]
            
            # Pisca a mensagem atual
            if int(current_time / config.INTERVALO_CURSOR_PISCAR) % 2 == 0:
                render_current_loading = fonts['normal'].render(current_loading_message_text, True, config.COR_TEXTO)
                current_loading_rect = render_current_loading.get_rect(center=(config.LARGURA_TELA // 2, y_offset_loading_msgs + len(messages_fixed_on_screen) * fonts['normal'].get_linesize()))
                screen.blit(render_current_loading, current_loading_rect)


        # Cabeçalho e Rodapé (fixos, não piscam)
        texto_superior = fonts['pequena'].render(mensagens_loading_header, True, config.COR_TEXTO)
        screen.blit(texto_superior, (config.LARGURA_TELA - texto_superior.get_width() - 10, 10))
        texto_inferior = fonts['pequena'].render(mensagens_loading_footer, True, config.COR_TEXTO)
        screen.blit(texto_inferior, (10, config.ALTURA_TELA - texto_inferior.get_height() - 10))

        # Efeito de Scanline (CRT)
        for y in range(0, config.ALTURA_TELA, 3):
            pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

def draw_shutdown_animation(screen, fonts, shutdown_start_time):
    """Desenha a animação de desligamento do terminal."""
    tempo_desligamento_passado = (pygame.time.get_ticks() - shutdown_start_time) / 1000
    
    mensagem_desligamento = ""
    if tempo_desligamento_passado < 1.0:
        mensagem_desligamento = "Sistema desligando..."
    elif tempo_desligamento_passado < 2.5:
        mensagem_desligamento = "Desativando modulos..."
    elif tempo_desligamento_passado < 4.0:
        mensagem_desligamento = "Adeus."
    
    screen.fill(config.COR_FUNDO)

    # Nome da empresa no topo (com fonte 'grande')
    st_agnes_texto = "ST.AGNES BIOPHARMA INSTITUTE"
    render_empresa = fonts['grande'].render(st_agnes_texto, True, config.COR_TEXTO)
    x_empresa = (config.LARGURA_TELA - render_empresa.get_width()) // 2
    y_empresa = config.ALTURA_TELA // 4
    screen.blit(render_empresa, (x_empresa, y_empresa))

    # Renderiza a mensagem de desligamento PISCANDO
    if mensagem_desligamento:
        # Aplica o efeito de piscar
        if int(tempo_desligamento_passado * 5) % 2 == 0:
            texto_desligamento = fonts['media'].render(mensagem_desligamento, True, config.COR_TEXTO)
            # Posiciona abaixo do nome da empresa, com mais espaço (ajustado para y_empresa + altura_empresa + 2*linha_altura_media)
            desligamento_rect = texto_desligamento.get_rect(center=(config.LARGURA_TELA // 2, y_empresa + render_empresa.get_height() + (2 * fonts['media'].get_linesize()) ))
            screen.blit(texto_desligamento, desligamento_rect)
    
    # Efeito de Scanline (CRT)
    for y in range(0, config.ALTURA_TELA, 3):
        pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 

    pygame.display.flip()

def draw_terminal_blocked_screen(screen, fonts, current_time_ticks):
    """Desenha a tela de terminal bloqueado."""
    mensagem_bloqueio = "TERMINAL BLOQUEADO."
    sub_mensagem_bloqueio = "Este terminal requer reinicializacao manual para reativar."
    
    # Piscar a mensagem
    if int(current_time_ticks / config.INTERVALO_CURSOR_PISCAR) % 2 == 0:
        texto_bloqueio = fonts['grande'].render(mensagem_bloqueio, True, config.COR_ALARME_CRITICO) # Vermelho piscante
        texto_sub_bloqueio = fonts['pequena'].render(sub_mensagem_bloqueio, True, config.COR_ALARME_CRITICO)
    else:
        texto_bloqueio = fonts['grande'].render(mensagem_bloqueio, True, config.COR_TEXTO) # Verde normal
        texto_sub_bloqueio = fonts['pequena'].render(sub_mensagem_bloqueio, True, config.COR_TEXTO)
    
    bloqueio_rect = texto_bloqueio.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2 - 20))
    sub_bloqueio_rect = texto_sub_bloqueio.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2 + 30))

    screen.fill(config.COR_FUNDO)
    screen.blit(texto_bloqueio, bloqueo_rect)
    screen.blit(texto_sub_bloqueio, sub_bloqueio_rect)

    # Efeito de Scanline (CRT)
    for y in range(0, config.ALTURA_TELA, 3):
        pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
    
    pygame.display.flip()

def draw_hack_restart_delay_screen(screen, fonts, hack_restart_delay_start_time, current_time_ticks):
    """Desenha a tela de atraso de reinício do hack."""
    tempo_atraso_passado = (current_time_ticks - hack_restart_delay_start_time) / 1000
    tempo_atraso_restante = max(0, config.HACK_RESTART_DURATION_MS / 1000 - tempo_atraso_passado)
    
    mensagem_atraso = f"Hack falhou. Reiniciando em\n{int(tempo_atraso_restante)} segundos..." 
    
    # Piscar a mensagem
    if int(tempo_atraso_passado * 5) % 2 == 0:
        texto_atraso_render = fonts['grande'].render(mensagem_atraso, True, config.COR_ALARME_CLARO) 
    else:
        texto_atraso_render = fonts['grande'].render(mensagem_atraso, True, config.COR_TEXTO)

    # Dividir a mensagem em linhas e centralizar cada uma
    lines = mensagem_atraso.split('\n')
    line_height = fonts['grande'].get_linesize()
    total_text_height = len(lines) * line_height
    
    start_y_central = (config.ALTURA_TELA // 2) - (total_text_height // 2) 

    screen.fill(config.COR_FUNDO)
    
    for i, line in enumerate(lines):
        rendered_line = fonts['grande'].render(line, True, texto_atraso_render.get_at((0,0))) 
        line_rect = rendered_line.get_rect(center=(config.LARGURA_TELA // 2, start_y_central + i * line_height))
        screen.blit(rendered_line, line_rect)

    # Efeito de Scanline (CRT)
    for y in range(0, config.ALTURA_TELA, 3):
        pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
    
    pygame.display.flip()

def draw_purge_countdown_screen(screen, fonts, purge_tempo_inicio_ticks, protocolo_atual_nome, current_time_ticks):
    """Desenha a tela de contagem regressiva de purga ou destruição de servidor."""
    tempo_passado_segundos = (current_time_ticks - purge_tempo_inicio_ticks) / 1000
    tempo_restante_segundos = max(0, config.PURGE_TEMPO_TOTAL_SEGUNDOS - tempo_passado_segundos)

    minutos = int(tempo_restante_segundos // 60)
    segundos = int(tempo_restante_segundos % 60)
    
    cronometro_str = f"{minutos:02d}:{segundos:02d}"

    cronometro_cor = config.COR_TEXTO
    mensagem_status_purga_base = "STATUS INDEFINIDO"

    if protocolo_atual_nome == "PURGE":
        if tempo_restante_segundos > config.PURGE_TEMPO_TOTAL_SEGUNDOS - 10:
            mensagem_status_purga_base = "Protocolo de Purga:\nValidando credenciais de detonacion..."
            cronometro_cor = config.COR_TEXTO
        elif tempo_restante_segundos > config.PURGE_TEMPO_TOTAL_SEGUNDOS - 20:
            mensagem_status_purga_base = "Protocolo de Purga:\nIniciando sequencia de aniquilacao de dados..."
            cronometro_cor = config.COR_TEXTO
        elif tempo_restante_segundos > 60: # Maior que 1 minuto
            mensagem_status_purga_base = "Processo de purga em andamento:\nPreparando para auto-destruicao..."
            cronometro_cor = config.COR_TEXTO
        elif tempo_restante_segundos <= 60 and tempo_restante_segundos > 10: # Último minuto
            cronometro_cor = config.COR_ALARME_CLARO
            mensagem_status_purga_base = "Fase critica:\nDetonacion iminente!"
        elif tempo_restante_segundos <= 10 and tempo_restante_segundos > 0: # Últimos 10 segundos (piscando)
            cronometro_cor = config.COR_ALARME_CRITICO
            if int(tempo_restante_segundos * 10) % 10 < 5:
                mensagem_status_purga_base = "ATENCAO:\nEVACUE AGORA!"
            else:
                mensagem_status_purga_base = ""
        elif tempo_restante_segundos <= 0:
            cronometro_cor = config.COR_ALARME_CRITICO
            mensagem_status_purga_base = "DETONACION."
    
    elif protocolo_atual_nome == "SERVER_DESTRUCT":
        if tempo_restante_segundos > config.PURGE_TEMPO_TOTAL_SEGUNDOS - 10:
            mensagem_status_purga_base = "Destruicao de Servidor:\nValidando acesso de nivel Omega..."
            cronometro_cor = config.COR_TEXTO
        elif tempo_restante_segundos > config.PURGE_TEMPO_TOTAL_SEGUNDOS - 20:
            mensagem_status_purga_base = "Destruicao de Servidor:\nIniciando sobrescrita de dados..."
            cronometro_cor = config.COR_TEXTO
        elif tempo_restante_segundos > 60: # Maior que 1 minuto
            mensagem_status_purga_base = "Processo de destruicao de servidor em andamento:\nIrreversivel..."
            cronometro_cor = config.COR_TEXTO
        elif tempo_restante_segundos <= 60 and tempo_restante_segundos > 10:
            cronometro_cor = config.COR_ALARME_CLARO
            mensagem_status_purga_base = "Fase critica:\nServidores offline em breve!"
        elif tempo_restante_segundos <= 10 and tempo_restante_segundos > 0:
            cronometro_cor = config.COR_ALARME_CRITICO
            if int(tempo_restante_segundos * 10) % 10 < 5:
                mensagem_status_purga_base = "ALERTA:\nDADOS DO SERVIDOR PERDIDOS!"
            else:
                mensagem_status_purga_base = ""
        elif tempo_restante_segundos <= 0:
            cronometro_cor = config.COR_ALARME_CRITICO
            mensagem_status_purga_base = "SERVIDORES OFFLINE."

    screen.fill(config.COR_FUNDO)

    # Desenha o cronômetro
    texto_cronometro = fonts['cronometro'].render(cronometro_str, True, cronometro_cor)
    cronometro_rect = texto_cronometro.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2 - 50))
    screen.blit(texto_cronometro, cronometro_rect)

    # Desenha as mensagens de status da purga (AGORA COM QUEBRA DE LINHA)
    lines = mensagem_status_purga_base.split('\n')
    line_height = fonts['media'].get_linesize()
    total_text_height = len(lines) * line_height
    
    start_y = config.ALTURA_TELA // 2 + 50 - (total_text_height // 2) + (line_height // 2) 

    for i, line in enumerate(lines):
        rendered_line = fonts['media'].render(line, True, cronometro_cor)
        line_rect = rendered_line.get_rect(center=(config.LARGURA_TELA // 2, start_y + i * line_height))
        screen.blit(rendered_line, line_rect)

    # Efeito de Scanline (CRT)
    for y in range(0, config.ALTURA_TELA, 3):
        pygame.draw.line(screen, config.COR_SCANLINE, (0, y), (config.LARGURA_TELA, y)) 
    
    pygame.display.flip()