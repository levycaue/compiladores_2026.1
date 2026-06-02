import sys
import os
from lexer import tokenizar, formatar_saida


def ler_arquivo(caminho):
    if not os.path.exists(caminho):
        print(f"ERRO: arquivo '{caminho}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def ler_stdin():
    print("Aguardando entrada (Ctrl+D para finalizar):", file=sys.stderr)
    return sys.stdin.read()


def main():
    args = sys.argv[1:]

    if args and args[0] == "--inline":
        if len(args) < 2:
            print("ERRO: --inline requer uma string de código.", file=sys.stderr)
            sys.exit(1)
        source = args[1]
    elif args:
        source = ler_arquivo(args[0])
    else:
        source = ler_stdin()

    print(formatar_saida(tokenizar(source)))


if __name__ == "__main__":
    main()
