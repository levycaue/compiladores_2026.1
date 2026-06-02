from er_to_nfa import build_langc_nfa


def epsilon_closure(nfa, states):
    closure = set(states)
    queue   = list(states)
    while queue:
        s = queue.pop()
        for t in nfa["epsilon"].get(s, set()):
            if t not in closure:
                closure.add(t)
                queue.append(t)
    return frozenset(closure)


def move(nfa, states, char):
    result = set()
    for s in states:
        result |= nfa["transitions"].get(s, {}).get(char, set())
    return result


def dfa_edge(nfa, dfa_state_set, char):
    moved = move(nfa, dfa_state_set, char)
    if not moved:
        return frozenset()
    return epsilon_closure(nfa, moved)


def resolve_token(nfa, dfa_state_set):
    best_token    = None
    best_priority = float("inf")
    for s in dfa_state_set:
        if s in nfa["accept"]:
            p = nfa["priority"].get(s, float("inf"))
            if p < best_priority:
                best_priority = p
                best_token    = nfa["accept"][s]
    return best_token


def nfa_to_dfa(nfa):
    alphabet  = nfa["alphabet"]
    start_set = epsilon_closure(nfa, {nfa["start"]})

    set_to_id = {start_set: 0}
    id_to_set = {0: start_set}
    queue     = [start_set]

    dfa_transitions = {}
    dfa_accept      = {}
    next_id         = 1

    while queue:
        current_set = queue.pop(0)
        current_id  = set_to_id[current_set]

        dfa_transitions[current_id] = {}

        token = resolve_token(nfa, current_set)
        if token is not None:
            dfa_accept[current_id] = token

        for char in alphabet:
            next_set = dfa_edge(nfa, current_set, char)
            if not next_set:
                continue
            if next_set not in set_to_id:
                set_to_id[next_set] = next_id
                id_to_set[next_id]  = next_set
                next_id            += 1
                queue.append(next_set)
            dfa_transitions[current_id][char] = set_to_id[next_set]

    return {
        "states":         set(range(next_id)),
        "alphabet":       alphabet,
        "transitions":    dfa_transitions,
        "start":          0,
        "accept":         dfa_accept,
        "dead":           None,
        "_id_to_nfa_set": id_to_set,
    }


def verify_dfa(dfa):
    errors = []
    valid_tokens = {
        "NUM", "TEXT", "BOOL", "SHOW", "TRUE", "FALSE",
        "VAR", "CONST", "EQ", "EQEQ", "GT", "LT",
        "ADD", "SUB", "MUL", "DIV",
        "LPAREN", "RPAREN", "SEMICOLON", "WHITESPACE"
    }
    if dfa["start"] not in dfa["states"]:
        errors.append("Estado inicial não está no conjunto de estados.")
    for state, transitions in dfa["transitions"].items():
        if state not in dfa["states"]:
            errors.append(f"Estado {state} nas transições não existe.")
        for char, dest in transitions.items():
            if dest not in dfa["states"]:
                errors.append(f"Transição δ({state}, {repr(char)}) = {dest}: destino não existe.")
            if not isinstance(dest, int):
                errors.append(f"Transição δ({state}, {repr(char)}): destino deve ser inteiro.")
    for state, token in dfa["accept"].items():
        if state not in dfa["states"]:
            errors.append(f"Estado final {state} não existe.")
        if token not in valid_tokens:
            errors.append(f"Estado {state} tem token inválido: '{token}'.")
    return errors


def run_tests():
    print("\nExecutando testes do Algoritmo de Subconjuntos (NFA → DFA)...")

    nfa_mock = {"epsilon": {0: {1, 2}, 1: {3}, 3: {4}}}
    result = epsilon_closure(nfa_mock, {0})
    assert result == frozenset({0, 1, 2, 3, 4})
    print("  [OK] epsilon_closure: alcança todos os estados por ε")

    nfa_mock = {"transitions": {0: {"a": {1, 2}}, 1: {"a": {3}}, 2: {"b": {4}}}}
    result = move(nfa_mock, {0, 1}, "a")
    assert result == {1, 2, 3}
    print("  [OK] move: une os destinos de todos os estados do conjunto")

    nfa = build_langc_nfa()
    dfa = nfa_to_dfa(nfa)

    for state, transitions in dfa["transitions"].items():
        for char, dest in transitions.items():
            assert isinstance(dest, int)
    print("  [OK] Determinismo: todas as transições apontam para um único estado")

    esperados = {
        "NUM", "TEXT", "BOOL", "SHOW", "TRUE", "FALSE",
        "VAR", "CONST", "EQ", "EQEQ", "GT", "LT",
        "ADD", "SUB", "MUL", "DIV",
        "LPAREN", "RPAREN", "SEMICOLON", "WHITESPACE"
    }
    assert not (esperados - set(dfa["accept"].values()))
    print(f"  [OK] Todos os {len(esperados)} tokens estão presentes no DFA")

    state = dfa["start"]
    for char in "==":
        state = dfa["transitions"].get(state, {}).get(char)
    assert dfa["accept"].get(state) == "EQEQ"
    print("  [OK] Prioridade: '==' reconhecido como EQEQ (não como dois EQ)")

    for word, expected in {"num": "NUM", "text": "TEXT", "bool": "BOOL",
                           "show": "SHOW", "true": "TRUE", "false": "FALSE"}.items():
        state = dfa["start"]
        for char in word:
            state = dfa["transitions"].get(state, {}).get(char)
        assert dfa["accept"].get(state) == expected
    print("  [OK] Palavras reservadas reconhecidas corretamente (não como VAR)")

    assert not verify_dfa(dfa)
    print("  [OK] verify_dfa: sem erros estruturais")

    print("\nTodos os testes passaram!\n")


if __name__ == "__main__":
    run_tests()
