import os
import shutil
import subprocess
import threading
import time
from zipfile import ZipFile
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, ResumableUploadError
import platform

def perform_backup(progress_callback=None):
    def backup_process():
        print("Iniciando processo de backup...")

        backup_dir = 'users/backup'
        backup_file_name = f'backup.zip'
        backup_file_path = os.path.join(backup_dir, backup_file_name)
        db_name = 'crm'
        db_user = 'root'
        db_password = '99480231aA!'

        # Verifica o sistema operacional
        system_platform = platform.system()
        if system_platform == 'Windows':
            # No Windows, estamos usando XAMPP MySQL
            mysql_dump_command = f'mysqldump -u {db_user} {"" if db_password == "" else "-p" + db_password} {db_name} > {backup_dir}/{db_name}.sql'
        elif system_platform == 'Linux':
            # No Linux, usa o MySQL instalado diretamente
            mysql_dump_command = f'mysqldump -u {db_user} {"" if db_password == "" else "--password=" + db_password} {db_name} > {backup_dir}/{db_name}.sql'
        else:
            print("Sistema operacional não suportado.")
            return

        # Backup do banco de dados MySQL
        print("Fazendo backup do banco de dados...")
        subprocess.run(mysql_dump_command, shell=True)
        print("Backup do banco de dados concluído.")

        if progress_callback:
            progress_callback(25)

        temp_backup_dir = os.path.join(backup_dir, 'temp_backup')
        os.makedirs(temp_backup_dir, exist_ok=True)

        temp_media_dir = os.path.join(temp_backup_dir, 'media')

        print("Copiando pasta 'media' para o diretório temporário...")
        if os.path.exists(temp_media_dir):
            print("A pasta 'media' já existe no diretório temporário. Atualizando...")
            update_media_directory('media', temp_media_dir)
        else:
            shutil.copytree('media', temp_media_dir)  # Cria uma cópia da pasta 'media' no diretório temporário

        print("Cópia da pasta 'media' concluída.")
        if progress_callback:
            progress_callback(50)

        print("Criando arquivo zip...")
        with ZipFile(backup_file_path, 'w') as zipf:
            zipf.write(f"{backup_dir}/{db_name}.sql", f"{db_name}.sql")  # Adiciona o arquivo SQL ao ZIP

            # Adiciona os arquivos do diretório temporário ao zip
            for root, dirs, files in os.walk(temp_backup_dir):
                for file in files:
                    src_path = os.path.join(root, file)
                    zipf.write(src_path, os.path.relpath(src_path, temp_backup_dir))

        print("Arquivo zip criado.")
        if progress_callback:
            progress_callback(75)

        print("Autenticando no Google Drive...")
        creds = Credentials.from_authorized_user_file('token.json')
        service = build('drive', 'v3', credentials=creds)

        print("Verificando se o arquivo já existe no Google Drive...")
        existing_file_id = find_existing_file(service, backup_file_name)

        media = MediaFileUpload(backup_file_path, mimetype='application/zip', resumable=True)
        if existing_file_id:
            print("Arquivo encontrado. Atualizando...")
            request = service.files().update(fileId=existing_file_id, media_body=media)
        else:
            print("Arquivo não encontrado. Fazendo upload...")
            file_metadata = {'name': backup_file_name}
            request = service.files().create(body=file_metadata, media_body=media, fields='id')

        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    if progress_callback:
                        progress_callback(int(status.progress() * 100))
            except ResumableUploadError as e:
                print(f"Erro no upload resumível: {e}")
                break

        print("Upload concluído.")
        if progress_callback:
            progress_callback(100)

        print("Removendo arquivos temporários...")
        # Verifica se o arquivo backup.zip ainda está sendo usado por outro processo
        while is_file_in_use(backup_file_path):
            print("O arquivo backup.zip ainda está sendo usado. Aguardando...")
              # Espera 5 segundos antes de verificar novamente

        try:
            time.sleep(60)
            os.remove(backup_file_path)
            os.remove(f"{backup_dir}/{db_name}.sql")  # Remove também o arquivo SQL de backup
            shutil.rmtree(temp_backup_dir)
        except PermissionError as e:
            print(f"Erro ao remover arquivos temporários: {e}")

        print("Processo de backup concluído.")

    # Inicia a thread para executar o processo de backup
    backup_thread = threading.Thread(target=backup_process)
    backup_thread.start()

def is_file_in_use(file_path):
    """
    Verifica se o arquivo está sendo usado por outro processo.
    """
    if os.path.exists(file_path):
        try:
            # Tenta abrir o arquivo em modo de leitura
            with open(file_path, 'r') as f:
                return False  # Se puder ser aberto, não está em uso
        except PermissionError:
            return True  # Se não puder ser aberto, está em uso
    return False  # Se o arquivo não existir, não está em uso

def update_media_directory(src_dir, dst_dir):
    """
    Atualiza a pasta de destino com os arquivos da pasta de origem.
    """
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)

        if os.path.isdir(src_item):
            # Se for um diretório, chama recursivamente a função para atualizar seu conteúdo
            if not os.path.exists(dst_item):
                os.makedirs(dst_item)
            update_media_directory(src_item, dst_item)
        else:
            # Se for um arquivo, copia ou substitui o arquivo existente
            shutil.copy2(src_item, dst_item)

def find_existing_file(service, file_name):
    """
    Procura por um arquivo com o nome especificado no Google Drive.
    Retorna o ID do arquivo se encontrado, senão retorna None.
    """
    results = service.files().list(q=f"name='{file_name}'", fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        return None

# Chame a função perform_backup para iniciar o processo de backup
perform_backup()
