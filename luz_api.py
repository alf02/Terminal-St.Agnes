import socket
import config

# --- Configurações UDP ---
# O IP e a porta serão definidos em config.py

def enviar_comando(comando_int):
    """
    Envia um comando UDP para a sirene.
    Comandos esperados: 0, 1
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.settimeout(0.1) # Timeout curto para não travar o programa
        
        server_address = (config.IP_LUMINARIA, config.PORTA_LUMINARIA)
        
        # Converte o inteiro para uma string antes de enviar
        message = str(comando_int).encode('utf-8')
        
        print(f"DEBUG: Enviando comando UDP '{message.decode()}' para {config.IP_LUMINARIA}:{config.PORTA_LUMINARIA}")
        sock.sendto(message, server_address)
        
    except socket.timeout:
        print(f"DEBUG: Timeout ao enviar comando UDP. Verifique a conexao.")
        pass 
    except Exception as e:
        print(f"ERRO ao enviar comando UDP para a sirene: {e}")
        pass 
    finally:
        sock.close()

def ligar_sirene():
    """Liga a sirene (envia '1')."""
    enviar_comando(1)

def desligar_sirene():
    """Desliga a sirene (envia '0')."""
    enviar_comando(0)

# Exemplo de uso (para teste)
if __name__ == "__main__":
    print("Testando API da Sirene com UDP...")
    ligar_sirene()
    import time
    time.sleep(3)
    desligar_sirene()
    print("Teste de API UDP concluído.")