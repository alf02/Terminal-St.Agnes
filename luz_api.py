import paho.mqtt.client as mqtt
import config

# --- Configurações MQTT ---
# O IP e a porta serão definidos em config.py
MQTT_TOPIC_COMMANDS = "naka5/servidor/cmd" # Tópico para o qual o terminal vai publicar
MQTT_QOS = 2 # Qualidade de Servico (garante entrega da mensagem)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT com sucesso!")
    else:
        print(f"Falha na conexao ao broker, código de retorno: {rc}")

def enviar_comando_mqtt(comando):
    """
    Conecta ao broker MQTT e publica um comando.
    Comandos esperados: "LIGAR_LUZ", "LIGAR_SIRENE", "DESLIGAR_TUDO"
    """
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.on_connect = on_connect
        client.connect(config.IP_LUZ, config.PORTA_MQTT_BROKER)
        
        # Envia a mensagem para o tópico
        client.publish(MQTT_TOPIC_COMMANDS, payload=comando, qos=MQTT_QOS, retain=False)
        print(f"DEBUG: Comando MQTT '{comando}' publicado no tópico '{MQTT_TOPIC_COMMANDS}'.")
        client.disconnect()

    except Exception as e:
        print(f"ERRO ao enviar comando MQTT para luz: {e}")

def ligar_luz():
    """Envia o comando 'lampada'."""
    enviar_comando_mqtt("lampada")

def ligar_sirene():
    """Envia o comando 'sirenes'."""
    enviar_comando_mqtt("sirenes")

def desligar_tudo():
    """Envia o comando 'DESLIGAR_TUDO'."""
    enviar_comando_mqtt("DESLIGAR_TUDO")

# Exemplo de uso (para teste)
if __name__ == "__main__":
    print("Testando API das Luz com MQTT...")
    # OBS: O broker precisa estar rodando no IP e porta configurados!
    ligar_luz()
    import time
    time.sleep(2)
    ligar_sirene()
    time.sleep(2)
    desligar_tudo()
    print("Teste de API MQTT concluído.")