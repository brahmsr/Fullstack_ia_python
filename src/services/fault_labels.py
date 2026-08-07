STATE_LABELS = {"normal", "baseline", "teste", "acelerando", "motor_desligado"}


# corrige os tipos/abreviações conhecidas antes de agrupar.
TOKEN_FIXES = {
    "cockecocked": "cocked",
    "desabalanceado": "desbalanceado",
    "desbanlanceado": "desbalanceado",
    "ddesbalanceado": "desbalanceado",
    "dedesbalanceado": "desbalanceado",
    "desabanceado": "desbalanceado",
    "desbalanceamento": "desbalanceado",
    "mortor": "motor",
    "normla": "normal",
    "comb": "combination",
    "tes": "teste",
}

# São apenas noises, então dá pra descartar
NOISE_TOKENS = {"pos", "carga", "adxl", "novo", "teste", "antigo"}

# Alguns rótulos "new_*"/"*_adxl_*" abreviam o nome do defeito (como o "cocked")
ALIASES = {
    "cocked": "cocked_rotor",
    "eccentric": "eccentric_rotor",
}


def canonicalizar_fault(fault: str) -> str:
    """Reduz um rótulo bruto da 'fault' à sua família canônica, agrupando variações"""
    if not isinstance(fault, str) or not fault.strip():
        return fault

    tokens = fault.strip().lower().split("_")
    tokens = [TOKEN_FIXES.get(t, t) for t in tokens]

    if tokens and tokens[0] == "new":
        tokens = tokens[1:] or tokens

    while len(tokens) > 1 and (tokens[-1].isdigit() or tokens[-1] in NOISE_TOKENS):
        tokens.pop()

    familia = "_".join(tokens)
    return ALIASES.get(familia, familia)


def is_state(fault: str) -> bool:
    """Retorna True para não falhas"""
    return canonicalizar_fault(fault) in STATE_LABELS
