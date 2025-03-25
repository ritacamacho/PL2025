# [TPC6] ***Parser* LL(1) Recursivo Descendente**

## 🗓️ Data de Realização

**21/03/2025**

## ⭐ Objetivos

Criar um ***parser* LL(1) recursivo descendente** que reconheça **expressões aritméticas** e calcule o respetivo valor.

## 🤓 Solução

O programa, em *Python*, segue a abordagem de **análise sintática recursiva descendente** para avaliar **expressões aritméticas**.

O analisador léxico reconhece os seguintes *tokens*:

- **NUM**: Números Inteiros
- **ADD (+)**: Operação de Adição
- **SUB (-)**: Operação de Subtração
- **MUL (*)**: Operação de Multiplicação
- **DIV (/)**: Operação de Divisão
- **PO (()**: Parêntese a abrir
- **PC ())**: Parêntese a fechar

Através de **expressões regulares**, os *tokens* são identificados e atribuídos corretamente.