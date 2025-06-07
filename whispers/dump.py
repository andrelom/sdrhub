import os

def print_tree(start_path='.', prefix=''):
    """Imita o comando `tree` de forma recursiva."""
    entries = sorted(os.listdir(start_path))
    for index, name in enumerate(entries):
        path = os.path.join(start_path, name)
        connector = "└── " if index == len(entries) - 1 else "├── "
        print(prefix + connector + name)
        if os.path.isdir(path):
            extension = "    " if index == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension)

def print_all_file_contents(start_path='.'):
    """Percorre e imprime o conteúdo de todos os arquivos."""
    for root, _, files in os.walk(start_path):
        for fname in files:
            file_path = os.path.join(root, fname)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    print(f"-----[ {file_path} ]-----")
                    print(f.read())
                    print()
            except Exception as e:
                print(f"-----[ {file_path} ]-----")
                print(f"[Erro ao ler o arquivo: {e}]\n")

if __name__ == '__main__':
    current_dir = os.getcwd()
    print(f"Target Directory: {current_dir}")

    print("\n==========================")
    print("== ESTRUTURA DO DIRETÓRIO ==")
    print("==========================\n")
    print_tree(current_dir)

    print("\n==========================")
    print("== CONTEÚDO DOS ARQUIVOS ==")
    print("==========================\n")
    print_all_file_contents(current_dir)
