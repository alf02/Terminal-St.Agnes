import socket
import config # Para acessar o IP_LUMINARIA e PORTA_LUMINARIA

# --- Configurações UDP ---
# O IP e a porta serão definidos em config.py

def enviar_comando_luminaria(comando):
    """
    Envia um comando UDP para as luminárias.
    Comandos esperados: "BLINK_RED_ON", "BLINK_RED_OFF"
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.settimeout(0.1) # Timeout curto para não travar o programa
        
        # O IP e a porta virão do config.py
        server_address = (config.IP_LUMINARIA, config.PORTA_LUMINARIA)
        
        message = comando.encode('utf-8')
        
        # print(f"DEBUG: Enviando comando UDP '{comando}' para {config.IP_LUMINARIA}:{config.PORTA_LUMINARIA}")
        sock.sendto(message, server_address)
        
        # Não esperamos resposta, mas podemos adicionar um recvfrom para depuração se necessário
        # data, server = sock.recvfrom(4096)
        # print(f"DEBUG: Resposta recebida: {data.decode('utf-8')}")
        
    except socket.timeout:
        # print(f"DEBUG: Timeout ao enviar comando UDP para {config.IP_LUMINARIA}:{config.PORTA_LUMINARIA}. Verifique a conexão.")
        pass # Não travar o jogo se a luminária não estiver online
    except Exception as e:
        # print(f"ERRO ao enviar comando UDP para luminária: {e}")
        pass # Não travar o jogo em caso de outros erros de rede
    finally:
        sock.close()

def ligar_piscar_vermelho():
    """Envia o comando para as luminárias começarem a piscar em vermelho."""
    enviar_comando_luminaria("BLINK_RED_ON")

def desligar_piscar_vermelho():
    """Envia o comando para as luminárias pararem de piscar em vermelho."""
    enviar_comando_luminaria("BLINK_RED_OFF")

# Exemplo de uso (apenas para teste direto deste arquivo)
if __name__ == "__main__":
    # Certifique-se de que config.py tenha IP_LUMINARIA e PORTA_LUMINARIA definidos
    print("Testando API das Luminárias...")
    print("Ligando piscar vermelho por 5 segundos...")
    ligar_piscar_vermelho()
    import time
    time.sleep(5)
    print("Desligando piscar vermelho.")
    desligar_piscar_vermelho()
    print("Teste concluído.")