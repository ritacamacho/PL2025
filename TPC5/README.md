# [TPC5] ***Vending Machine***

## 🗓️ Data de Realização

**13/03/2025**

## ⭐ Objetivos

Construir um programa em *Python* que simule uma **máquina de *vending***.

A máquina tem um *stock* de produtos: uma lista de triplos, nome do produto, quantidade e preço.

## 🤓 Solução

Foi definida uma **lista de *tokens* e expressões regulares** para reconhecer as várias ações possíveis da *vending machine*: listar, selecionar produto, inserir moedas, inserir notas e sair.

A partir daí, são executadas as **ações** reconhecidas, inseridas pelo utilizador, lendo o **`stock.json`** com os detalhes dos produtos disponíveis, e calculando **valores como saldo, troco, etc.** após **inserção de dinheiro e/ou compra de produtos**.