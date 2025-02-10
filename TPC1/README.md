# [TPC1] Somador ON/OFF

## 🗓️ Data de Realização

**10/02/2025**

## ⭐ Objetivos

1. Pretende-se que o programa some todas as sequências de dígitos que encontra num texto
2. Sempre que encontrar a `string` `Off` em qualquer combinação de maiúsculas e minúsculas, esse comportamento é desligado
3. Sempre que encontrar a `string` `On` em qualquer combinação de maiúsculas e minúsculas, esse comportamento é novamente ligado
4. Sempre que encontrar o caracter `=`, o resultado da soma é colocado na saída

## 🤓 Solução

O programa `on_off` lê um ficheiro de texto, percorrendo o seu conteúdo `char` a `char`, verificando continuamente as condições explícitas em **Objetivos**.
A soma é controlada por ativação booleana (on/off), confirmando se os dígitos encontrados devem ser ignorados ou somados ao valor total, imprimindo valores intermédios sempre que `=` é encontrado.