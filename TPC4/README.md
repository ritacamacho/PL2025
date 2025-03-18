# [TPC4] Analisador Léxico

## 🗓️ Data de Realização

**06/03/2025**

## ⭐ Objetivos

Criar em *Python* um **analisador léxico** para a linguagem **`SPARQL`**, capaz de reconhecer os principais ***tokens*** da mesma.

## 🤓 Solução

Foi definida uma **lista de *tokens* e expressões regulares** para reconhecer comentários, palavras-chave, variáveis, prefixos, strings e números.

A **ordem das regras** no analisador léxico é fundamental para evitar conflitos. Palavras-chave devem ser processadas antes de identificadores genéricos, regras específicas antes de regras abrangentes e a regra de erro deve vir por último para capturar caracteres inválidos.