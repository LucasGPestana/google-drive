from pydrive.auth import GoogleAuth, AuthenticationError
from pydrive.drive import GoogleDrive
import os, glob

# Serve para dar upload nos arquivos presentes no diretório local folder_directory
def uploadFiles(folder_directory, driveParentFolderId, drive):

  # Serão criados no drive os arquivos presentes localmente no diretório atual, assim como seu conteúdo já será setado
  # O metadado parents define que o arquivo estará dentro do diretório atual no drive
  for fileOrDir in os.listdir(folder_directory):

    if os.path.isfile(os.path.join(folder_directory, fileOrDir)):

      driveFile = drive.CreateFile({"title": fileOrDir, "parents": [{"kind": "drive#fileLink", "id": driveParentFolderId}]})

      driveFile.SetContentFile(os.path.join(folder_directory, fileOrDir))

      driveFile.Upload()

def searchDirectories(prompt, drive):

  driveFilesList = drive.ListFile({"q": prompt, "orderBy": "createdDate desc"})

  return driveFilesList.GetList()

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
driveFolder = drive.CreateFile({"title": "Teste", "mimeType": "application/vnd.google-apps.folder"})
driveFolder.Upload()

root_directory = os.path.join(os.environ.get("USERPROFILE"), "Desktop", "Teste")

uploadFiles(root_directory, driveFolder["id"], drive)

folders = [directory[:-len(os.sep)] if directory.endswith(os.sep) else directory for directory in glob.glob(pathname="**/", root_dir=root_directory, recursive=True)]

folders.pop(folders.index("Teste3"))

for folder in folders:

  # Essa lista serve para organizar os diretórios de forma similar ao que é encontrado localmente (Isto é, com os subdiretórios dentro do seu diretório pai local), ou seja, ela vai conter objetos GoogleDriveFile
  directories = list()

  # Enquanto for encontrado um diretório pai (parent) local no diretório atual, vai ser criado um diretório no drive correspondente a esse diretório pai local (Laço while)
  while True:

    folder_directory = os.path.join(root_directory, folder)

    # driveFilesList = searchDirectories(f"title contains '{os.path.basename(os.path.dirname(folder))}' and trashed=False", drive)

    driveParentFolder = drive.CreateFile({"title": os.path.basename(folder), 
                                                "mimeType": "application/vnd.google-apps.folder"})
    driveParentFolder.Upload()

    directories.append(driveParentFolder)

    driveParentFolderId = driveParentFolder["id"]

    uploadFiles(folder_directory, driveParentFolderId, drive)

    # A cada iteração, a variável folder vai receber o diretório pai do diretório atual (Caso este diretório ainda tenha diretórios pai)
    # Quando não tiver mais diretórios pai locais (Nesse caso, a função dirname retorna uma string vazia), sairá do laço while
    if not os.path.dirname(folder):

      break
    
    else:

      folder = os.path.dirname(folder)
  
  # Verifica se a lista directories está vazia ou não
  # Caso não esteja, a lista vai ser percorrida de trás para frente (Uma vez que os diretórios foram adicionados também de trás para frente - Ex: VSC\Python\Soma vai ficar, na lista, ["Soma", "Python", "VSC"] -), cujo metadado "parents" vai determinar que o diretório pai do diretório atual da iteração é o diretório anterior da iteração
  if directories:

    for i in range(len(directories) - 1, -1, -1):

      if i == len(directories) - 1:

        directories[i]["parents"] = [{"kind": "drive#fileLink", "id": driveFolder["id"]}]
      
      else:

        directories[i]["parents"] = [{"kind": "drive#fileLink", "id": directories[i - 1]["id"]}]
      
      directories[i].Upload()


