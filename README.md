# LangC Lexer

Analisador Léxico da linguagem **LangC**, desenvolvido para a disciplina de Compiladores (UFC 2026.1).

Implementa o pipeline clássico de compiladores:

```
Expressões Regulares (ER)
        ↓  [er_to_nfa.py — Algoritmo de Thompson]
Autômato Finito Não Determinístico (NFA)
        ↓  [nfa_to_dfa.py — Algoritmo de Subconjuntos]
Autômato Finito Determinístico (DFA)
        ↓  [lexer.py — Maior Casamento]
Lista de Tokens
```

## Estrutura do Projeto

```
LangC-lexer-main/
├── main.py          ← ponto de entrada (lê arquivo, stdin ou --inline)
├── lexer.py         ← analisador léxico (maior casamento sobre o DFA)
├── er_to_nfa.py     ← algoritmo de Thompson (ER → NFA)
├── nfa_to_dfa.py    ← algoritmo de subconjuntos (NFA → DFA)
├── tokens.txt       ← lista oficial dos tokens da LangC
├── Membros da Equipe ← Autores
├── exemplo.langc    ← exemplo de código-fonte LangC
└── testes/
    ├── teste_01.langc  …  teste_15.langc
```

---

## Como Rodar

### 1. Analisar um arquivo `.langc`

```bash
python main.py testes/teste_01.langc
```

Saída:

```
NUM VAR EQ NUM SEMICOLON
```

### 2. Passar código diretamente pela linha de comando (`--inline`)

```bash
python main.py --inline "num x = 5 ;"
```

Saída:

```
NUM VAR EQ NUM SEMICOLON
```

### 3. Entrada via stdin (pipe)

```bash
echo "show a == b ;" | python main.py
```

Saída:

```
SHOW VAR EQEQ VAR SEMICOLON
```

Ou de forma interativa (pressione `Ctrl+D` para encerrar):

```bash
python main.py
```

### 4. Arquivo de exemplo incluso

```bash
python main.py exemplo.langc
```

---

## Formato da Saída

Uma linha por linha do código-fonte, com os **tipos dos tokens** separados por espaço.

Exemplo de entrada (`programa.langc`):

```
num a = 0 ;
num b = 5 + a ;
text c = "teSte" ;
```

Saída:

```
NUM VAR EQ NUM SEMICOLON
NUM VAR EQ NUM ADD VAR SEMICOLON
TEXT VAR EQ CONST SEMICOLON
```

Em caso de **erro léxico**, a saída é simplesmente:

```
ERRO
```

---

## Tokens da LangC

| Token       | O que reconhece               | Exemplo         |
|-------------|-------------------------------|-----------------|
| `NUM`       | Palavra reservada `num`       | `num`           |
| `TEXT`      | Palavra reservada `text`      | `text`          |
| `BOOL`      | Palavra reservada `bool`      | `bool`          |
| `SHOW`      | Palavra reservada `show`      | `show`          |
| `TRUE`      | Palavra reservada `true`      | `true`          |
| `FALSE`     | Palavra reservada `false`     | `false`         |
| `VAR`       | Identificador (máx. 30 chars) | `_minha_var99`  |
| `NUM`       | Número inteiro                | `42`            |
| `CONST`     | String literal                | `"Olá mundo"`   |
| `EQEQ`      | Comparação de igualdade       | `==`            |
| `EQ`        | Atribuição                    | `=`             |
| `GT`        | Maior que                     | `>`             |
| `LT`        | Menor que                     | `<`             |
| `ADD`       | Adição                        | `+`             |
| `SUB`       | Subtração                     | `-`             |
| `MUL`       | Multiplicação                 | `*`             |
| `DIV`       | Divisão                       | `/`             |
| `LPAREN`    | Parêntese esquerdo            | `(`             |
| `RPAREN`    | Parêntese direito             | `)`             |
| `SEMICOLON` | Ponto e vírgula               | `;`             |
| `WHITESPACE`| Espaços, tabs, quebras        | _(descartado)_  |

---

## Rodando os Testes

Cada módulo possui sua própria suíte de testes. Execute-os individualmente:

### Testes do Algoritmo de Thompson (`er_to_nfa.py`)

Verifica a construção dos NFAs individuais e do NFA combinado.

```bash
python er_to_nfa.py
```

Saída esperada:

```
Executando testes do Algoritmo de Thompson...
  [OK] nfa_symbol
  [OK] nfa_string('num')
  [OK] nfa_union(a, b)
  [OK] nfa_star(a)
  [OK] nfa_plus([0-9])
  [OK] NFA combinado com todos os tokens da LangC

Todos os testes passaram!
```

Além dos testes, exibe o **resumo do NFA combinado** e os detalhes internos de dois NFAs individuais para inspeção.

---

### Testes do Algoritmo de Subconjuntos (`nfa_to_dfa.py`)

Verifica o ε-closure, o move, o determinismo do DFA e a resolução de prioridades.

```bash
python nfa_to_dfa.py
```

Saída esperada:

```
Executando testes do Algoritmo de Subconjuntos (NFA → DFA)...
  [OK] epsilon_closure: alcança todos os estados por ε
  [OK] move: une os destinos de todos os estados do conjunto
  [OK] Determinismo: todas as transições apontam para um único estado
  [OK] Todos os 20 tokens estão presentes no DFA
  [OK] Prioridade: '==' reconhecido como EQEQ (não como dois EQ)
  [OK] Palavras reservadas reconhecidas corretamente (não como VAR)
  [OK] verify_dfa: sem erros estruturais

Todos os testes passaram!
```

Além dos testes, exibe o **resumo do DFA** (total de estados, transições, tokens) e a tabela de transições.

---

### Testes do Analisador Léxico (`lexer.py`)

Executa 20 casos de teste cobrindo declarações, operadores, strings, identificadores, palavras reservadas e erros léxicos.

```bash
python lexer.py
```

Saída esperada:

```
Executando testes do Analisador Léxico...

  [OK]     Exemplo do enunciado (3 linhas)
  [OK]     Declaração num simples
  [OK]     Declaração text
  [OK]     Declaração bool com true
  [OK]     Declaração bool com false
  [OK]     Prioridade: 'num' é NUM, não VAR
  [OK]     Prioridade: 'show' é SHOW, não VAR
  [OK]     Operadores aritméticos
  [OK]     Maior casamento: == é EQEQ, não dois EQ
  [OK]     Atribuição com = simples
  [OK]     Operadores > e <
  [OK]     Operador <
  [OK]     Expressão com parênteses
  [OK]     String com espaço interno
  [OK]     String vazia
  [OK]     Identificador com underscore
  [OK]     Identificador com dígito
  [OK]     Programa completo da especificação
  [OK]     Erro léxico: @ inválido
  [OK]     Erro léxico: # inválido

  Resultado: 20/20 testes passaram
```

---

## Casos de Teste Inclusos (`testes/`)

| Arquivo | Código-fonte | Saída esperada | Tipo |
|---|---|---|---|
| `teste_01.langc` | `num x = 1 ;` | `NUM VAR EQ NUM SEMICOLON` | Declaração simples |
| `teste_02.langc` | `num text bool show true false` | `NUM TEXT BOOL SHOW TRUE FALSE` | Todas as palavras reservadas |
| `teste_03.langc` | `num _minha_Var99 = 0 ;` | `NUM VAR EQ NUM SEMICOLON` | Identificador com `_` e dígitos |
| `teste_04.langc` | `text s = "a+b=c!?" ;` | `TEXT VAR EQ CONST SEMICOLON` | String com símbolos especiais |
| `teste_05.langc` | `num r = 10 + 2 - 3 * 4 / 2 ;` | `NUM VAR EQ NUM ADD NUM SUB NUM MUL NUM DIV NUM SEMICOLON` | Todos os operadores aritméticos |
| `teste_06.langc` | Comparações `>`, `<`, `==`, `=` | `SHOW VAR GT VAR SEMICOLON` / `SHOW VAR LT VAR SEMICOLON` / `SHOW VAR EQEQ VAR SEMICOLON` / `SHOW VAR EQ VAR SEMICOLON` | Operadores relacionais (4 linhas) |
| `teste_07.langc` | Expressão com parênteses aninhados | `SHOW LPAREN LPAREN NUM ADD NUM RPAREN MUL LPAREN NUM SUB NUM RPAREN RPAREN SEMICOLON` | Parênteses aninhados |
| `teste_08.langc` | `a = "ismailly" ;` / `show a ;` | `VAR EQ CONST SEMICOLON` / `SHOW VAR SEMICOLON` | Atribuição de string e exibição |
| `teste_09.langc` | `numerico = 1 ;` / `num = 7 ;` | `NUM VAR EQ NUM SEMICOLON` / `NUM EQ NUM SEMICOLON` | Identificador iniciando com palavra reservada; `num` sem declaração de tipo |
| `teste_10.langc` | `num __x = 5 ;` | `NUM VAR EQ NUM SEMICOLON` | Identificador iniciado com `__` |
| `teste_11.langc` | `num numerico = 9 ;` | `NUM VAR EQ NUM SEMICOLON` | Declaração com identificador longo |
| `teste_12.langc` | `show true ;` / `show false ;` | `SHOW TRUE SEMICOLON` / `SHOW FALSE SEMICOLON` | Literais booleanos |
| `teste_13.langc` | `num x = 5 & 2 ;` | `ERRO`¹ | Erro léxico — caractere `&` inválido |
| `teste_14.langc` | `num 1 * num ;` | `NUM NUM MUL NUM SEMICOLON` | `1` como número isolado (válido) |
| `teste_15.langc` | `text s = "aberto ;` | `TEXT VAR EQ CONST VAR SEMICOLON`² | String não fechada |

> ¹ **`teste_13`** — o caractere `&` não pertence ao alfabeto da LangC. O lexer interrompe a análise ao encontrá-lo e emite a mensagem: `ERRO: Caractere inválido '&' na linha 1`. Este é um erro **léxico** legítimo — o analisador não consegue formar nenhum token válido a partir desse caractere.

> ² **`teste_15`** — a string `"aberto ;` não possui aspas de fechamento. O lexer reconhece `"aberto ` como `CONST` e continua tokenizando o restante normalmente. Erros de string não fechada são de natureza **sintática**, não léxica — o analisador léxico não os rejeita.

Para rodar todos os testes de uma vez:

```bash
for i in $(seq 1 15); do
  f="testes/teste_$(printf '%02d' $i).langc"
  echo -n "$(basename $f): "
  python main.py "$f"
done
```

---

## Observações Importantes

### Erros léxicos vs. outros erros

O analisador léxico detecta apenas **erros léxicos**: caracteres inválidos (`@`, `#`, `&`, etc.) e tokens malformados (identificador começando com dígito, como `1valor`).

Erros de **sintaxe** (parênteses sem fechar, expressões inválidas) e de **semântica** (variável não declarada, tipos incompatíveis) **não são verificados aqui** — eles pertencem às fases seguintes do compilador.

### Regra do maior casamento

O lexer sempre consome o maior trecho possível. Exemplo:

- Entrada `==` → reconhece `EQEQ` (não dois `EQ`)
- Entrada `numerico` → reconhece `VAR` (não `NUM` + `VAR`)

### Limite de identificadores

Identificadores com mais de 30 caracteres são rejeitados com erro léxico.

### Prioridade de tokens

Quando dois tokens casam com o mesmo trecho, vence o de maior prioridade na lista:

1. Palavras reservadas (`num`, `text`, `bool`, `show`, `true`, `false`) antes de `VAR`
2. `EQEQ` antes de `EQ`

---

## Conceitos Teóricos Implementados

| Conceito | Arquivo | Detalhes |
|---|---|---|
| Algoritmo de Thompson | `er_to_nfa.py` | Constrói NFA a partir de ER usando `symbol`, `concat`, `union`, `star`, `plus` |
| ε-closure | `nfa_to_dfa.py` | BFS sobre transições ε |
| Algoritmo de Subconjuntos | `nfa_to_dfa.py` | Cada conjunto de estados NFA vira um estado DFA |
| Resolução de prioridades | `nfa_to_dfa.py` | Em conflito, vence o token de menor índice na lista |
| Maior casamento | `lexer.py` | Avança enquanto há transição; retorna o último estado final visitado |
