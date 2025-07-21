import random
import config

def _calcular_likeness(palavra1, palavra2):
    """Calcula a 'similaridade' entre duas palavras (número de letras em comum na mesma posição)."""
    likeness = 0
    min_len = min(len(palavra1), len(palavra2))
    for i in range(min_len):
        if palavra1[i] == palavra2[i]:
            likeness += 1
    return likeness

def initialize_hacking_game_data():
    """
    Gera todos os dados necessários para iniciar um novo jogo de hacking.
    Retorna um dicionário com 'palavras', 'senha_correta', 'tentativas_restantes', 'sequencias_ativas'.
    """
    dados_hacking = {}
    
    # Escolhe um comprimento aleatório para a senha
    comprimento_alvo = random.choice([6, 7, 8, 9, 10]) 
    
    # Filtra as palavras base que correspondem ao comprimento alvo
    palavras_filtradas = [p for p in config.HACKING_PALAVRAS_BASE if len(p) == comprimento_alvo]
    
    # Se não houver palavras suficientes do comprimento alvo, usa palavras maiores também
    if len(palavras_filtradas) < config.HACKING_MAX_TENTATIVAS * 2:
        palavras_filtradas = [p for p in config.HACKING_PALAVRAS_BASE if len(p) >= 6]

    # Gera sequências especiais (duds/attempts)
    sequencias_geradas = []
    for _ in range(config.NUM_SEQUENCIAS_ESPECIAIS):
        tipo_seq_info = random.choice(config.HACKING_TIPOS_ESPECIAIS)
        open_char = tipo_seq_info[1]
        close_char = tipo_seq_info[2]
        junk_content = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(1, 3)))
        sequencia_completa = f"{open_char}{junk_content}{close_char}"
        sequencias_geradas.append((sequencia_completa, tipo_seq_info[0]))
    
    # Combina palavras e sequências especiais, e embaralha
    todas_opcoes = list(palavras_filtradas)
    for seq_str, _ in sequencias_geradas:
        todas_opcoes.append(seq_str)
    random.shuffle(todas_opcoes)
    
    # Garante que haja palavras suficientes se o embaralhamento resultou em poucas opções
    if len(todas_opcoes) < 10 and len(config.HACKING_PALAVRAS_BASE) > len(todas_opcoes):
        while len(todas_opcoes) < 10:
            palavra_nova = random.choice(config.HACKING_PALAVRAS_BASE)
            if len(palavra_nova) == comprimento_alvo and palavra_nova not in todas_opcoes:
                todas_opcoes.append(palavra_nova)
            elif len(palavra_nova) >= 6 and palavra_nova not in todas_opcoes: # fallback to any length
                todas_opcoes.append(palavra_nova)


    dados_hacking['palavras'] = todas_opcoes
    
    # Escolhe a senha correta apenas entre as palavras reais (não sequências especiais)
    palavras_sem_sequencias = [p for p in todas_opcoes if p not in [s[0] for s in sequencias_geradas]]
    if palavras_sem_sequencias:
        dados_hacking['senha_correta'] = random.choice(palavras_sem_sequencias)
    else: # Fallback se todas as opções forem sequências especiais (improvável, mas seguro)
        dados_hacking['senha_correta'] = random.choice(palavras_filtradas)
    
    dados_hacking['tentativas_restantes'] = config.HACKING_MAX_TENTATIVAS
    dados_hacking['likeness_ultima_tentativa'] = -1 # Nenhuma tentativa ainda
    dados_hacking['sequencias_ativas'] = {seq_str: tipo_ef for seq_str, tipo_ef in sequencias_geradas}
    
    print(f"DEBUG_HACK_INIT: Senha correta gerada: {dados_hacking['senha_correta']}")
    print(f"DEBUG_HACK_INIT: Palavras possíveis: {dados_hacking['palavras']}")
    print(f"DEBUG_HACK_INIT: Sequências ativas: {dados_hacking['sequencias_ativas']}")
    
    return dados_hacking