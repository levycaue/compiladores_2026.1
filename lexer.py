import sys
from er_to_nfa import build_langc_nfa, _reset_counter
from nfa_to_dfa import nfa_to_dfa


def _build_dfa():
    _reset_counter()
    nfa = build_langc_nfa()
    return nfa_to_dfa(nfa)


_DFA = _build_dfa()


class ErroLexico(Exception):
    pass


class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo   = tipo
        self.lexema = lexema
        self.linha  = linha

    def __repr__(self):
        return f"Token({self.tipo}, {repr(self.lexema)}, linha={self.linha})"


def _proximo_token(dfa, source, pos, linha_atual):
    state       = dfa["start"]
    last_accept = None
    last_pos    = pos
    last_linha  = linha_atual
    j           = pos
    linha_j     = linha_atual

    while j < len(source):
        char  = source[j]
        trans = dfa["transitions"].get(state, {})
        if char not in trans:
            break
        state = trans[char]
        j    += 1
        if char == "\n":
            linha_j += 1
        if state in dfa["accept"]:
            last_accept = dfa["accept"][state]
            last_pos    = j
            last_linha  = linha_j

    if last_accept is None:
        char_ruim = repr(source[pos]) if pos < len(source) else "EOF"
        raise ErroLexico(f"Caractere inválido {char_ruim} na linha {linha_atual}")

    return Token(last_accept, source[pos:last_pos], linha_atual), last_pos, last_linha


def tokenizar(source, dfa=None):
    if dfa is None:
        dfa = _DFA

    tokens      = []
    pos         = 0
    linha_atual = 1

    while pos < len(source):
        try:
            tok, pos, linha_atual = _proximo_token(dfa, source, pos, linha_atual)
        except ErroLexico as e:
            print(f"ERRO: {e}")
            return None

        if tok.tipo == "WHITESPACE":
            continue

        if tok.tipo in ("VAR", "NUM") and tok.lexema not in (
            "num", "text", "bool", "show", "true", "false"
        ):
            if tok.lexema[0].isdigit():
                if not tok.lexema.isdigit():
                    print(f"ERRO: token inválido '{tok.lexema}' na linha {tok.linha}")
                    return None
                tok.tipo = "NUM"
            else:
                tok.tipo = "VAR"

        if tok.tipo == "VAR" and len(tok.lexema) > 30:
            print(f"ERRO: identificador '{tok.lexema}' excede 30 caracteres (linha {tok.linha})")
            return None

        tokens.append(tok)

    return tokens


def formatar_saida(tokens):
    if tokens is None:
        return "ERRO"
    linhas = {}
    for tok in tokens:
        linhas.setdefault(tok.linha, []).append(tok.tipo)
    if not linhas:
        return ""
    return "\n".join(" ".join(linhas[l]) for l in sorted(linhas))


def analisar_arquivo(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho}")
        return
    print(formatar_saida(tokenizar(source)))


def analisar_string(source):
    print(formatar_saida(tokenizar(source)))


def _verificar(descricao, source, esperado):
    saida = formatar_saida(tokenizar(source))
    ok    = saida.strip() == esperado.strip()
    print(f"  {'[OK]    ' if ok else '[FALHOU]'} {descricao}")
    if not ok:
        print(f"           Entrada  : {repr(source)}")
        print(f"           Esperado : {repr(esperado)}")
        print(f"           Obtido   : {repr(saida)}")
    return ok


def run_tests():
    print("\nExecutando testes do Analisador Léxico...\n")
    total  = 0
    passou = 0

    casos = [
        (
            "Exemplo do enunciado (3 linhas)",
            'num a = 0 ;\nnum b = 5 + a ;\ntext c = "teSte" ;',
            "NUM VAR EQ NUM SEMICOLON\n"
            "NUM VAR EQ NUM ADD VAR SEMICOLON\n"
            "TEXT VAR EQ CONST SEMICOLON"
        ),
        ("Declaração num simples",       "num x = 10 ;",          "NUM VAR EQ NUM SEMICOLON"),
        ("Declaração text",              'text msg = "Ola" ;',     "TEXT VAR EQ CONST SEMICOLON"),
        ("Declaração bool com true",     "bool b = true ;",        "BOOL VAR EQ TRUE SEMICOLON"),
        ("Declaração bool com false",    "bool b = false ;",       "BOOL VAR EQ FALSE SEMICOLON"),
        ("Prioridade: 'num' é NUM",      "num num = 5 ;",          "NUM NUM EQ NUM SEMICOLON"),
        ("Prioridade: 'show' é SHOW",    "show show ;",            "SHOW SHOW SEMICOLON"),
        (
            "Operadores aritméticos",
            "num r = 2 + 3 * 4 / 1 - 0 ;",
            "NUM VAR EQ NUM ADD NUM MUL NUM DIV NUM SUB NUM SEMICOLON"
        ),
        ("Maior casamento: == é EQEQ",   "show a == b ;",          "SHOW VAR EQEQ VAR SEMICOLON"),
        ("Atribuição com = simples",     "num a = 5 ;",            "NUM VAR EQ NUM SEMICOLON"),
        ("Operador >",                   "show a > b ;",           "SHOW VAR GT VAR SEMICOLON"),
        ("Operador <",                   "show x < 10 ;",          "SHOW VAR LT NUM SEMICOLON"),
        (
            "Expressão com parênteses",
            "num r = ( 2 + 3 ) ;",
            "NUM VAR EQ LPAREN NUM ADD NUM RPAREN SEMICOLON"
        ),
        ("String com espaço interno",    'text s = "oi vc" ;',     "TEXT VAR EQ CONST SEMICOLON"),
        ("String vazia",                 'text s = "" ;',           "TEXT VAR EQ CONST SEMICOLON"),
        ("Identificador com underscore", "num _x = 1 ;",           "NUM VAR EQ NUM SEMICOLON"),
        ("Identificador com dígito",     "num valor1 = 99 ;",      "NUM VAR EQ NUM SEMICOLON"),
        (
            "Programa completo da especificação",
            "show 2 > 2 ;\nnum a = 5 ;\nnum b = 10 ;\nnum soma = a + b ;\n"
            'text mensagem = "Oi!" ;\nshow mensagem ;\nshow a ;\nshow soma ;\n'
            "show a < b ;\nshow a = 5 ;",
            "SHOW NUM GT NUM SEMICOLON\nNUM VAR EQ NUM SEMICOLON\nNUM VAR EQ NUM SEMICOLON\n"
            "NUM VAR EQ VAR ADD VAR SEMICOLON\nTEXT VAR EQ CONST SEMICOLON\n"
            "SHOW VAR SEMICOLON\nSHOW VAR SEMICOLON\nSHOW VAR SEMICOLON\n"
            "SHOW VAR LT VAR SEMICOLON\nSHOW VAR EQ NUM SEMICOLON"
        ),
        ("Erro léxico: @ inválido",      "num @x = 1 ;",           "ERRO"),
        ("Erro léxico: # inválido",      "# comentario",           "ERRO"),
    ]

    for descricao, source, esperado in casos:
        total  += 1
        passou += _verificar(descricao, source, esperado)

    print(f"\n  Resultado: {passou}/{total} testes passaram\n")
    return passou == total


if __name__ == "__main__":
    if len(sys.argv) > 1:
        analisar_arquivo(sys.argv[1])
        sys.exit(0)

    sucesso = run_tests()

    if sucesso:
        print("=" * 60)
        print("  Demonstração — Exemplo do enunciado")
        print("=" * 60)
        exemplo = 'num a = 0 ;\nnum b = 5 + a ;\ntext c = "teSte" ;'
        print("\nEntrada:")
        for linha in exemplo.splitlines():
            print(f"  {linha}")
        print("\nSaída:")
        analisar_string(exemplo)
