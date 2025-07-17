import pygame
import sys
import random
import time 

# Importa as configurações
import config

def mostrar_tela_inicial(screen, fonts, main_text): # <--- Adicionado 'main_text' como argumento
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

        # --- ALTERADO AQUI: Usa 'main_text' do argumento ---
        texto_principal_render = fonts['grande'].render(main_text, True, config.COR_TEXTO)
        main_text_rect = texto_principal_render.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2 - 50))
        screen.blit(texto_principal_render, main_text_rect)

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
    """Exibe a tela de carregamento com a mensagem da empresa e 'LOADING...' piscando."""
    sounds['boot_up'].play()

    tempo_inicio = pygame.time.get_ticks()
    tempo_total_loading = 3000
    
    mensagens_loading_header = "LEAV -- DUSK % (C) 1987"
    mensagens_loading_footer = "Loading: user_info/password.txt::[File found]"
    
    st_agnes_texto = "ST.AGNES BIOPHARMA INSTITUTE" # Este texto ainda é fixo na tela de loading

    start_time = pygame.time.get_ticks()
    loading_duration = config.TEMPO_TELA_LOADING * 1000 # Convertendo para milissegundos
    
    show_loading_text = True
    last_blink_time = start_time

    while pygame.time.get_ticks() - start_time < loading_duration:
        screen.fill(config.COR_FUNDO)
        
        # Desenha a borda e as linhas de topo/base
        pygame.draw.rect(screen, config.COR_TEXTO, (0, 0, config.LARGURA_TELA, config.ALTURA_TELA), 2)
        pygame.draw.line(screen, config.COR_TEXTO, (5, 30), (config.LARGURA_TELA - 5, 30), 2)
        pygame.draw.line(screen, config.COR_TEXTO, (5, config.ALTURA_TELA - 30), (config.LARGURA_TELA - 5, config.ALTURA_TELA - 30), 2)

        # Mensagem da empresa (fixa, com fonte 'grande')
        render_empresa = fonts['grande'].render(st_agnes_texto, True, config.COR_TEXTO)
        x_empresa = (config.LARGURA_TELA - render_empresa.get_width()) // 2
        y_empresa = config.ALTURA_TELA // 4 # Posição mais acima
        screen.blit(render_empresa, (x_empresa, y_empresa))

        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > config.INTERVALO_CURSOR_PISCAR:
            show_loading_text = not show_loading_text
            last_blink_time = current_time

        if show_loading_text:
            texto_loading = "LOADING..."
            render_loading = fonts['normal'].render(texto_loading, True, config.COR_TEXTO)
            x_loading = (config.LARGURA_TELA - render_loading.get_width()) // 2
            y_loading = y_empresa + render_empresa.get_height() + 50 
            screen.blit(render_loading, (x_loading, y_loading))

        # Cabeçalho e Rodapé copiados da tela de loading (sem piscar aqui)
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
    
    mensagem_atraso = f"Hack falhou. Reiniciando em {int(tempo_atraso_restante)} segundos..."
    
    # Piscar a mensagem
    if int(tempo_atraso_passado * 5) % 2 == 0:
        texto_atraso = fonts['grande'].render(mensagem_atraso, True, config.COR_ALARME_CLARO) # Laranja piscante
    else:
        texto_atraso = fonts['grande'].render(mensagem_atraso, True, config.COR_TEXTO)

    atraso_rect = texto_atraso.get_rect(center=(config.LARGURA_TELA // 2, config.ALTURA_TELA // 2))
    
    screen.fill(config.COR_FUNDO)
    screen.blit(texto_atraso, atraso_rect)

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
            mensagem_status_purga_base = "Fase critica:\nDetonacao iminente!"
        elif tempo_restante_segundos <= 10 and tempo_restante_segundos > 0: # Últimos 10 segundos (piscando)
            cronometro_cor = config.COR_ALARME_CRITICO
            if int(tempo_restante_segundos * 10) % 10 < 5:
                mensagem_status_purga_base = "ATENCAO:\nEVACUE AGORA!"
            else:
                mensagem_status_purga_base = ""
        elif tempo_restante_segundos <= 0:
            cronometro_cor = config.COR_ALARME_CRITICO
            mensagem_status_purga_base = "DETONACAO."
    
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