import os

def exists_directory(directory: str):
    if not os.path.isdir(directory):
        print(f'{directory} directory does not exist')
        return False
    return True

def remove_file(file_path):
    """
    Remove um arquivo do diretório especificado.

    :param file_path: Caminho completo do arquivo a ser removido.
    """
    try:
        # Verifica se o arquivo existe
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Arquivo removido com sucesso: {file_path}")
        else:
            print(f"Arquivo não encontrado: {file_path}")
    except Exception as e:
        print(f"Erro ao tentar remover o arquivo: {e}")