from pydrive.auth import GoogleAuth, AuthenticationError
from pydrive.drive import GoogleDrive
import os

# Serve para dar upload nos arquivos presentes no diretório local folder_directory
def uploadFiles(folder_directory, driveFolderId, drive):

  for fileOrDir in os.listdir(folder_directory):

    # Serão criados no drive os arquivos presentes localmente no diretório atual, assim como seu conteúdo já será setado
    # O metadado parents define que o arquivo estará dentro do diretório atual no drive
    # O continue serve para ele não retornar para o diretório pai caso o diretório atual corresponda a um arquivo (Vai diretamente para a próxima iteração da lista os.listdir) 
    if os.path.isfile(os.path.join(folder_directory, fileOrDir)):

      driveFile = drive.CreateFile({"title": fileOrDir, 
                                    "parents": [{"kind": "drive#fileLink", "id": driveFolderId}]})

      driveFile.SetContentFile(os.path.join(folder_directory, fileOrDir))

      driveFile.Upload()

      continue
    
    # Caso seja um diretório
    else:

      folder_directory = os.path.join(folder_directory, fileOrDir)

      driveParentFolder = drive.CreateFile({"title": fileOrDir, 
                                              "mimeType": "application/vnd.google-apps.folder", 
                                              "parents": [{"kind": "drive#fileLink", "id": driveFolderId}]})
        
      driveParentFolder.Upload()

      # Verifica se existem subdiretórios e/ou arquivos no diretório atual
      # Também verifica se o diretório existe (Ou seja, se é válido). Caso não seja, ele roda a linha do os.path.dirname
      if os.listdir(folder_directory) and os.path.exists(folder_directory):

        uploadFiles(folder_directory, driveParentFolder["id"], drive)
    
    # Retorna para o diretório pai do diretório atual
    folder_directory = os.path.dirname(folder_directory)
        

# Verifica se o arquivo client_secrets.json está presente no mesmo diretório do script
if not "client_secrets.json" in os.listdir(os.path.dirname(os.path.abspath(__file__))):

  raise FileNotFoundError("O arquivo client_secrets.json não foi encontrado!")

try:

  # Autenticação do google (Solicita as credenciais e a permissão para o uso do app, inicialmente)
  gauth = GoogleAuth()

  # Carrega o json contendo as credenciais do usuário e guardando-as no atributo credentials do objeto GoogleAuth
  gauth.LoadCredentialsFile("credentials.json")

  # Verifica se as credenciais foram preenchidas
  if not gauth.credentials:

    # Estabelece um servidor web para pegar o código de autorização presente na url
    gauth.LocalWebserverAuth()

  else:

    # Autoriza o usuário (A partir das credenciais do atributo credentials) e constroe o serviço
    gauth.Authorize()

  # Salva (E atualiza) os dados das credenciais em um json
  gauth.SaveCredentialsFile("credentials.json")

except AuthenticationError:

  print("Erro ao autenticar o usuário! Verifique suas autorizações e tente novamente!")

# Conexão com o google drive, a partir da autenticação do google estabelecida anteriormente
drive = GoogleDrive(auth=gauth)

# Cria um objeto GoogleDriveFile (Representação de um arquivo do drive) e envia para o drive
# O valor do metadado mimeType representa que o arquivo é um diretório (pasta)
driveRootFolder = drive.CreateFile({"title": "VSC", "mimeType": "application/vnd.google-apps.folder"})
driveRootFolder.Upload()

root_directory = os.path.join(os.environ.get("USERPROFILE"), "Documents", "VSC")

uploadFiles(root_directory, driveRootFolder["id"], drive)


