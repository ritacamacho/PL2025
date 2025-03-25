import ply.lex as lex
import sys
import json
from datetime import date

tokens = (
    "LISTAR",
    "SAIR",
    "SELECIONAR",
    "MOEDA",
    "NOTA",
    )

stock = {}
coins = {}
notes = {}
t_ignore = ' \t\n'

def t_LISTAR(t):
    r'(?i)LISTAR'; return t

def t_SAIR(t):
    r'(?i)SAIR'; return t

def t_SELECIONAR(t):
    r'(?i)SELECIONAR[ ]+[a-zA-Z0-9]+'; return t

def t_MOEDA(t):
    r'(?i)MOEDA\s+((1e|2e|50c|20c|10c|5c|2c|1c),?\s*)+'; return t

def t_NOTA(t):
    r'(?i)NOTA\s+([5e|10e|20e|50e|100e|200e|500e],?\s*)+'; return t

def t_error(t):
    print(f"Caracter inválido '{t.value[0]}' na posição {t.lexpos}")
    t.lexer.skip(1)

def LISTAR():
    print('      Código       |                     Nome                      |    Quantidade    |     Preço     ')
    print('--------------------------------------------------------------------------------------------------------')
    for product in stock.values():
        print(f"        {product['cod']}        |        {product['nome']: <30}         |      {product['quant']: <5}       |      {product['preco']: <5}")

def TROCO(saldo: float) -> str:
    notes_order = [50.00, 20.00, 10.00, 5.00]
    coins_order = [2.00, 1.00, 0.50, 0.20, 0.10, 0.05, 0.02, 0.01]
    troco_count = {}

    for value in notes_order + coins_order:
        while saldo >= value:
            if value in notes_order:
                note = next((n for n in notes.values() if n["valor"] == value), None)
                if note and note["quant"] > 0:
                    note["quant"] -= 1
                    saldo = round(saldo - value, 2)
                    troco_count[value] = troco_count.get(value, 0) + 1
                else:
                    break
            else:
                coin = next((c for c in coins.values() if c["valor"] == value), None)
                if coin and coin["quant"] > 0:
                    coin["quant"] -= 1
                    saldo = round(saldo - value, 2)
                    troco_count[value] = troco_count.get(value, 0) + 1
                else:
                    break

    troco_str_parts = []
    for value, count in troco_count.items():
        if value in notes_order:
            denomination = f"{int(value)}e"
        else:
            if value in [1.00, 2.00]:
                denomination = f"{int(value)}e"
            else:
                cents = int(value * 100)
                denomination = f"{cents}c"
        troco_str_parts.append(f"{count}x {denomination}")

    if not troco_str_parts:
        return "Sem troco disponível."
    return ", ".join(troco_str_parts[:-1]) + (" e " + troco_str_parts[-1] if len(troco_str_parts) > 1 else troco_str_parts[0])

def vending_machine(file_path: str):
    print(f"maq: {date.today()} Stock carregado, Estado atualizado.")
    print("maq: Bom dia. Estou disponível para atender o seu pedido.")
    lexer = lex.lex()
    saldo = 0

    for line in sys.stdin:
        lexer.input(line)

        for token in lexer:
            if token.type == "LISTAR":
                LISTAR()
                
            elif token.type == "SELECIONAR":
                cod = token.value.split()[1]
                product = stock.get(cod)
                if not product:
                    print(f"Produto não encontrado.")
                    continue
                if saldo == 0:
                    print(f"O Preço do produto é: {product['preco']:.2f}€")
                    continue
                if saldo < product["preco"]:
                    print(f"maq: Saldo insuficiente para satisfazer o seu pedido.")
                    print(f"maq: Saldo = {saldo:.2f}€ e Pedido = {product['preco']:.2f}€")
                    continue
                if product["quant"] == 0:
                    print(f"Produto esgotado.")
                    continue
                
                product["quant"] -= 1
                saldo -= product["preco"]
                print(f"Produto: {product['nome']} - {product['preco']:.2f}€")
                print(f"Saldo restante: {saldo:.2f}€")
            
            elif token.type == "MOEDA":
                moedas_str = " ".join(token.value.split()[1:])
                moedas = moedas_str.split(",")
                for moeda in moedas:
                    moeda = moeda.strip()
                    if moeda:
                        if moeda.endswith('e'):
                            valor = int(moeda[:-1])
                            coin = next((c for c in coins.values() if c["valor"] == valor), None)
                            if coin:
                                coin["quant"] += 1
                            saldo += valor
                        elif moeda.endswith('c'):
                            cents = int(moeda[:-1])
                            valor = cents / 100.0
                            coin = next((c for c in coins.values() if c["valor"] == valor), None)
                            if coin:
                                coin["quant"] += 1
                            saldo += valor
                
                print(f"Saldo: {saldo:.2f}€")
            
            elif token.type == "NOTA":
                notas_str = " ".join(token.value.split()[1:])
                notas = notas_str.split(",")
                for nota in notas:
                    nota = nota.strip()
                    if nota:
                        if nota.endswith('e'):
                            valor_str = nota[:-1]
                            valor = int(valor_str)
                            if valor not in [5, 10, 20]:
                                print(f"Nota inválida. Adicione notas de 5, 10 ou 20.")
                                continue
                            note = next((n for n in notes.values() if n["valor"] == valor), None)
                            if note:
                                note["quant"] += 1
                            saldo += valor
                            print(f"Saldo: {saldo:.2f}€")
            
            elif token.type == "SAIR":
                if saldo > 0:
                    troco = TROCO(saldo)
                    print(f"maq: Pode retirar o troco: {troco}")
                print("maq: Até à próxima! :)")
                save_to_json(file_path)
                exit(0)

def save_to_json(file_path: str):
    data = {
        "stock": list(stock.values()),
        "moedas": list(coins.values()),
        "notas": list(notes.values())
    }
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def storage_machine(data: dict):
    for product in data["stock"]:
        stock[product["cod"]] = product
    for coin in data["moedas"]:
        coins[coin["valor"]] = coin
    for note in data["notas"]:
        notes[note["valor"]] = note

def main():
    if len(sys.argv) != 2:
        path = "stock.json"
    else:
        path = sys.argv[1]
    
    with open(path, "r") as file:
        content = json.load(file)
    
    storage_machine(content)
    vending_machine(path)

if __name__ == "__main__":
    main()