# [TPC3] Conversor de MarkDown para HTML

## 🗓️ Data de Realização

**22/02/2025**

## ⭐ Objetivos

Criar em *Python* um pequeno conversor de **MarkDown** para **HTML** para os elementos descritos na *"Basic Syntax"* da ***Cheat Sheet***:
- **Cabeçalhos**: linhas iniciadas por "#", "##" ou "###"
- **Negrito**: pedaços de texto entre "**"
- **Itálico**: pedaços de texto entre "*"
- **Lista Numerada**
- **Link**: [texto](endereço URL)
- **Imagem**: ![texto alternativo](path para a imagem)

## 🤓 Solução

O programa ``markdown_to_html``, utilizando **expressões regulares**, converte **MarkDown** recebido como ``string`` (proveniente de ``example.md``) para o código **HTML** correspondente.
As **expressões regulares** utilizadas foram cuidadosamente associadas a cada elemento constituinte da sintaxe básica mencionada, substituindo sucessivamente os padrões encontrados na ``string`` (sintaxe **MarkDown**) pelo resultado desejado (sintaxe **HTML** correspondente).