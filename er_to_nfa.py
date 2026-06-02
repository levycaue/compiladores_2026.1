from __future__ import annotations

_state_counter = 0

def _new_state():
    global _state_counter
    s = _state_counter
    _state_counter += 1
    return s

def _reset_counter():
    global _state_counter
    _state_counter = 0

def nfa_symbol(char):
    s0, s1 = _new_state(), _new_state()
    return {
        "states":      {s0, s1},
        "alphabet":    {char},
        "transitions": {s0: {char: {s1}}},
        "epsilon":     {},
        "start":       s0,
        "accept":      {s1: None},
    }

def nfa_epsilon():
    s0, s1 = _new_state(), _new_state()
    return {
        "states":      {s0, s1},
        "alphabet":    set(),
        "transitions": {},
        "epsilon":     {s0: {s1}},
        "start":       s0,
        "accept":      {s1: None},
    }

def nfa_concat(m, n):
    new_epsilon = {**m["epsilon"]}
    for s, targets in n["epsilon"].items():
        new_epsilon[s] = new_epsilon.get(s, set()) | targets

    for accept_state in m["accept"]:
        new_epsilon[accept_state] = (
            new_epsilon.get(accept_state, set()) | {n["start"]}
        )

    new_transitions = {**m["transitions"]}
    for s, chars in n["transitions"].items():
        if s not in new_transitions:
            new_transitions[s] = {}
        for c, targets in chars.items():
            new_transitions[s][c] = (
                new_transitions[s].get(c, set()) | targets
            )

    return {
        "states":      m["states"] | n["states"],
        "alphabet":    m["alphabet"] | n["alphabet"],
        "transitions": new_transitions,
        "epsilon":     new_epsilon,
        "start":       m["start"],
        "accept":      n["accept"],
    }

def nfa_union(m, n):
    new_start  = _new_state()
    new_accept = _new_state()

    new_epsilon = {
        new_start: {m["start"], n["start"]},
        **m["epsilon"],
    }
    for s, targets in n["epsilon"].items():
        new_epsilon[s] = new_epsilon.get(s, set()) | targets

    for accept_state in m["accept"]:
        new_epsilon[accept_state] = (
            new_epsilon.get(accept_state, set()) | {new_accept}
        )
    for accept_state in n["accept"]:
        new_epsilon[accept_state] = (
            new_epsilon.get(accept_state, set()) | {new_accept}
        )

    new_transitions = {**m["transitions"]}
    for s, chars in n["transitions"].items():
        if s not in new_transitions:
            new_transitions[s] = {}
        for c, targets in chars.items():
            new_transitions[s][c] = (
                new_transitions[s].get(c, set()) | targets
            )

    return {
        "states":      m["states"] | n["states"] | {new_start, new_accept},
        "alphabet":    m["alphabet"] | n["alphabet"],
        "transitions": new_transitions,
        "epsilon":     new_epsilon,
        "start":       new_start,
        "accept":      {new_accept: None},
    }

def nfa_star(m):
    new_start  = _new_state()
    new_accept = _new_state()

    new_epsilon = {
        new_start: {m["start"], new_accept},
        **m["epsilon"],
    }
    for accept_state in m["accept"]:
        new_epsilon[accept_state] = (
            new_epsilon.get(accept_state, set()) | {m["start"], new_accept}
        )

    return {
        "states":      m["states"] | {new_start, new_accept},
        "alphabet":    m["alphabet"],
        "transitions": {**m["transitions"]},
        "epsilon":     new_epsilon,
        "start":       new_start,
        "accept":      {new_accept: None},
    }

def nfa_plus(m):
    return nfa_concat(m, nfa_star(m))

def nfa_optional(m):
    return nfa_union(m, nfa_epsilon())

def nfa_string(s):
    if not s:
        return nfa_epsilon()
    result = nfa_symbol(s[0])
    for ch in s[1:]:
        result = nfa_concat(result, nfa_symbol(ch))
    return result

def nfa_char_class(chars):
    chars = list(chars)
    result = nfa_symbol(chars[0])
    for ch in chars[1:]:
        result = nfa_union(result, nfa_symbol(ch))
    return result

def nfa_range(start_char, end_char):
    chars = [chr(c) for c in range(ord(start_char), ord(end_char) + 1)]
    return nfa_char_class(chars)

def nfa_any_except(excluded_chars):
    alphabet = set()
    for c in range(ord('a'), ord('z') + 1):
        alphabet.add(chr(c))
    for c in range(ord('A'), ord('Z') + 1):
        alphabet.add(chr(c))
    for c in range(ord('0'), ord('9') + 1):
        alphabet.add(chr(c))
    alphabet |= set(' \t\n+-*/=>()<;!@#$%&?|_\'"')
    allowed = alphabet - set(excluded_chars)
    return nfa_char_class(sorted(allowed))

def build_token_nfa(token_name, nfa):
    nfa["accept"] = {s: token_name for s in nfa["accept"]}
    return nfa

def build_all_token_nfas():
    lower  = nfa_range('a', 'z')
    upper  = nfa_range('A', 'Z')
    digit  = nfa_range('0', '9')
    letter = nfa_union(lower, upper)
    alnum  = nfa_union(nfa_union(letter, digit), nfa_symbol('_'))

    kw_num   = build_token_nfa("NUM",   nfa_string("num"))
    kw_text  = build_token_nfa("TEXT",  nfa_string("text"))
    kw_bool  = build_token_nfa("BOOL",  nfa_string("bool"))
    kw_show  = build_token_nfa("SHOW",  nfa_string("show"))
    kw_true  = build_token_nfa("TRUE",  nfa_string("true"))
    kw_false = build_token_nfa("FALSE", nfa_string("false"))

    id_start    = nfa_union(letter, nfa_symbol('_'))
    var_nfa     = build_token_nfa("VAR", nfa_concat(id_start, nfa_star(alnum)))
    integer_nfa = build_token_nfa("NUM", nfa_plus(digit))

    quote      = nfa_symbol('"')
    string_nfa = build_token_nfa(
        "CONST",
        nfa_concat(quote, nfa_concat(nfa_star(nfa_any_except('"')), quote))
    )

    eqeq_nfa      = build_token_nfa("EQEQ",      nfa_string("=="))
    eq_nfa        = build_token_nfa("EQ",         nfa_symbol('='))
    gt_nfa        = build_token_nfa("GT",         nfa_symbol('>'))
    lt_nfa        = build_token_nfa("LT",         nfa_symbol('<'))
    add_nfa       = build_token_nfa("ADD",        nfa_symbol('+'))
    sub_nfa       = build_token_nfa("SUB",        nfa_symbol('-'))
    mul_nfa       = build_token_nfa("MUL",        nfa_symbol('*'))
    div_nfa       = build_token_nfa("DIV",        nfa_symbol('/'))
    lparen_nfa    = build_token_nfa("LPAREN",     nfa_symbol('('))
    rparen_nfa    = build_token_nfa("RPAREN",     nfa_symbol(')'))
    semicolon_nfa = build_token_nfa("SEMICOLON",  nfa_symbol(';'))
    whitespace_nfa = build_token_nfa("WHITESPACE", nfa_plus(nfa_char_class(' \t\n')))

    return [
        ("NUM",        kw_num),
        ("TEXT",       kw_text),
        ("BOOL",       kw_bool),
        ("SHOW",       kw_show),
        ("TRUE",       kw_true),
        ("FALSE",      kw_false),
        ("NUM",        integer_nfa),
        ("CONST",      string_nfa),
        ("VAR",        var_nfa),
        ("EQEQ",       eqeq_nfa),
        ("EQ",         eq_nfa),
        ("GT",         gt_nfa),
        ("LT",         lt_nfa),
        ("ADD",        add_nfa),
        ("SUB",        sub_nfa),
        ("MUL",        mul_nfa),
        ("DIV",        div_nfa),
        ("LPAREN",     lparen_nfa),
        ("RPAREN",     rparen_nfa),
        ("SEMICOLON",  semicolon_nfa),
        ("WHITESPACE", whitespace_nfa),
    ]

def combine_nfas(token_nfas):
    new_start = _new_state()
    combined = {
        "states":      {new_start},
        "alphabet":    set(),
        "transitions": {},
        "epsilon":     {new_start: set()},
        "start":       new_start,
        "accept":      {},
        "priority":    {},
    }

    for priority, (token_name, nfa) in enumerate(token_nfas):
        combined["epsilon"][new_start].add(nfa["start"])
        combined["states"]   |= nfa["states"]
        combined["alphabet"] |= nfa["alphabet"]

        for s, chars in nfa["transitions"].items():
            if s not in combined["transitions"]:
                combined["transitions"][s] = {}
            for c, targets in chars.items():
                combined["transitions"][s][c] = (
                    combined["transitions"][s].get(c, set()) | targets
                )

        for s, targets in nfa["epsilon"].items():
            combined["epsilon"][s] = (
                combined["epsilon"].get(s, set()) | targets
            )

        for accept_state, token in nfa["accept"].items():
            combined["accept"][accept_state] = token
            combined["priority"][accept_state] = priority

    return combined

def build_langc_nfa():
    _reset_counter()
    return combine_nfas(build_all_token_nfas())

def run_tests():
    print("\nExecutando testes do Algoritmo de Thompson...")

    _reset_counter()
    nfa = nfa_symbol('a')
    assert nfa["start"] == 0
    assert 1 in nfa["accept"]
    assert nfa["transitions"][0]['a'] == {1}
    print("  [OK] nfa_symbol")

    _reset_counter()
    nfa = nfa_string("num")
    assert len(nfa["states"]) == 6
    print("  [OK] nfa_string('num')")

    _reset_counter()
    u = nfa_union(nfa_symbol('a'), nfa_symbol('b'))
    assert len(u["states"]) == 6
    assert len(u["accept"]) == 1
    print("  [OK] nfa_union(a, b)")

    _reset_counter()
    s = nfa_star(nfa_symbol('a'))
    assert len(s["accept"]) == 1
    print("  [OK] nfa_star(a)")

    _reset_counter()
    p = nfa_plus(nfa_range('0', '9'))
    assert len(p["accept"]) == 1
    print("  [OK] nfa_plus([0-9])")

    nfa = build_langc_nfa()
    assert nfa["start"] is not None
    tokens_presentes = set(nfa["accept"].values())
    tokens_esperados = {
        "NUM", "TEXT", "BOOL", "SHOW", "TRUE", "FALSE",
        "VAR", "CONST", "EQ", "EQEQ", "GT", "LT",
        "ADD", "SUB", "MUL", "DIV",
        "LPAREN", "RPAREN", "SEMICOLON", "WHITESPACE"
    }
    assert tokens_esperados == tokens_presentes
    print("  [OK] NFA combinado com todos os tokens da LangC")

    print("\nTodos os testes passaram!\n")

if __name__ == "__main__":
    run_tests()