# Monitoramento de Câmeras com Reconhecimento de Placas

Este projeto é uma aplicação de monitoramento de câmeras que utiliza YOLOv8 para detecção de objetos e EasyOCR para leitura de placas de veículos. A aplicação realiza a captura de vídeos de câmeras, analisa e processa os quadros para identificar e registrar placas de veículos em um banco de dados PostgreSQL.

## Funcionalidades

- **Detecção de Objetos**: Utiliza YOLOv8 para detectar objetos em tempo real.
- **Reconhecimento de Placas**: Usa EasyOCR para ler placas de veículos.
- **Registro em Banco de Dados**: Armazena informações sobre a entrada e saída de veículos em um banco de dados PostgreSQL.
- **Interface Gráfica**: Desenvolvida com Tkinter para exibir o feed das câmeras.

## Dependências

Certifique-se de ter as seguintes bibliotecas instaladas:

- OpenCV (`cv2`)
- Pandas (`pandas`)
- Ultralytics YOLO (`ultralytics`)
- NumPy (`numpy`)
- EasyOCR (`easyocr`)
- PIL (`Pillow`)
- Tkinter (`tkinter`)
- Psycopg2 (`psycopg2`)
- Relatório (para funcionalidades adicionais, se necessário)

## Instale as dependências com:

requirements.txt

## Configuração

# Modelos e Arquivos Necessários:

- modelo/best.pt: Modelo YOLOv8 pré-treinado.
- coco1.txt: Arquivo de classes YOLO.
- Banco de Dados PostgreSQL:

Configure o banco de dados PostgreSQL com as credenciais apropriadas no código.
O banco de dados deve conter as tabelas entrada, saida, e registro_placas.
Câmeras:

Atualize a lista self.rtsp_links com os links dos feeds das câmeras que você deseja monitorar.
Uso
Inicie a Aplicação: Execute o script Python:

**Inicie a Aplicação**:
   Execute o script Python com o seguinte comando:

   bash
 python interface.py

**Interface Gráfica**:
.A aplicação exibirá uma janela com feeds das câmeras.
.A área de análise será destacada em vermelho e as placas identificadas serão processadas.

# Aplicação de Relatórios com Flask

Esta aplicação web permite o gerenciamento de registros de entrada e saída de veículos, bem como a visualização de imagens associadas a esses registros. Desenvolvida com Flask, a aplicação fornece funcionalidades para filtrar registros por data, editar e excluir registros, e visualizar imagens armazenadas no banco de dados PostgreSQL.

## Funcionalidades

- **Visualização de Registros**: Exibe registros de entrada e saída com a opção de filtrar por data.
- **Edição e Exclusão de Registros**: Permite atualizar ou excluir registros existentes.
- **Upload e Visualização de Imagens**: Visualiza imagens associadas a registros de entrada.
- **Autenticação de Administrador**: Protege páginas administrativas com uma senha.

## Dependências

Certifique-se de ter as seguintes bibliotecas instaladas:

- Flask (`flask`)
- Psycopg2 (`psycopg2`)

Instale as dependências com:

bash
pip install flask psycopg2

### Estrutura do Código:
Conexão com o Banco de Dados
connect_db: Estabelece uma conexão com o banco de dados PostgreSQL.
Funções de Manipulação de Registros
fetch_records(table, start_date=None, end_date=None): Recupera registros de uma tabela específica com a opção de filtrar por intervalo de datas.
update_record(table, placa, new_placa): Atualiza um registro existente.
delete_record(table, placa): Exclui um registro.
add_record(table, placa, data, hora): Adiciona um novo registro.
### Rotas:
- /: Página inicial com formulários para filtrar registros, visualizar todos os registros, e realizar operações de edição e exclusão.
- /image/<record_id>: Exibe a imagem associada ao registro de entrada especificado.
- /admin: Página de login para administração com proteção por senha.
- /admin_page: Página de administração onde registros podem ser adicionados, editados ou excluídos.
- /admin/add: Adiciona um registro através de um formulário na página de administração.
- /admin/edit: Atualiza um registro através de um formulário na página de administração.
- /admin/delete: Exclui um registro através de um formulário na página de administração.
- /entries: Exibe todos os registros de entrada.
- /exits: Exibe todos os registros de saída.
## Como Usar
Inicie a Aplicação: Execute o script Flask com o seguinte comando:

bash
Copiar código
python app.py
Acesse a Interface Web: Abra um navegador e vá para http://127.0.0.1:5000/ para acessar a aplicação.

## Administração:

# Acesse a página de administração através de http://127.0.0.1:5000/admin.
Use a senha admin8822 para entrar na área de administração.
Visualização de Registros:

Use a página inicial para filtrar e visualizar registros.
Visualize imagens associadas a registros de entrada clicando nos links apropriados.

### Demonstraçao do interface.py 
![Captura de tela de 2024-08-27 21-23-33](https://github.com/user-attachments/assets/b10ca3a0-51b5-47ef-b38e-b8969f7ed553)

### Demonstraçao do app.py
![Captura de tela de 2024-09-06 11-16-13](https://github.com/user-attachments/assets/1a70fcc5-961a-423f-9aff-fb987781c6d3)
## Placas
![Captura de tela de 2024-09-06 11-17-10](https://github.com/user-attachments/assets/de1213c6-d06e-45c8-b9a0-ad4c4dfbc95d)

### Observação:
Para o correto funcionamento da interface.py, é essencial que o arquivo best.pt esteja presente na pasta modelo. Devido ao tamanho do arquivo, não foi possível realizar o upload para o GitHub. Se precisar do modelo de aprendizado de máquina para reconhecimento de placas de veículos, por favor, entre em contato pelo e-mail jj9075713@gmail.com.

### Requisitos de Hadware :
 Este sistema realiza a análise de apenas uma câmera RTSP e permite a adição de mais três câmeras para visualização. O hardware mínimo necessário para o funcionamento deste software é um processador com 8 núcleos e 4 threads. Caso tenha interesse em realizar a análise de quatro câmeras simultaneamente, é imprescindível ter uma GPU, caso contrário, o sistema não funcionará adequadamente.

### Dica:
Para adicionar os links das câmeras, localize a linha self.rtsp_links = [ na classe CameraApp e insira os links desejados. Lembre-se de que o primeiro link é destinado à análise de entrada e saída de veículos. Veja o código abaixo:
![Captura de tela de 2024-09-06 11-35-13](https://github.com/user-attachments/assets/2050e496-ee5e-468a-8e09-f9eebf08b5d0)
# Criando Atalhos para Scripts Python

## No Windows

No Windows, você cria atalhos para executar scripts ou aplicativos através do sistema de arquivos. Aqui está um guia para criar atalhos para os seus scripts Python:

### Criar o Atalho

1. Navegue até o local onde você deseja criar o atalho (por exemplo, na área de trabalho).
2. Clique com o botão direito do mouse em um espaço vazio e selecione **Novo** > **Atalho**.

### Definir o Caminho do Atalho

- **Para o Interface:**
  Na caixa que aparece, digite o caminho fictício para o interpretador Python e o script Python. Exemplo:
  ```plaintext
  "C:\Program Files\Python\python.exe" "C:\MeusProgramas\MeuApp\interface.py"
- **Para o Relatório:**
  Na caixa que aparece, digite o caminho fictício para o interpretador Python e o script Python. Exemplo:
  "C:\Program Files\Python\python.exe" "C:\MeusProgramas\MeuApp\app.py"
## Nomear o Atalho:
Após definir o caminho, clique em Avançar.
Dê um nome ao atalho, como "Interface" ou "Relatório".
Clique em Concluir.
### No Ubuntu (Linux):
No Ubuntu, você cria atalhos criando arquivos .desktop. Aqui está um guia para criar os arquivos .desktop com caminhos fictícios:

## Criar o Arquivo .desktop
Abra um editor de texto (como gedit, nano, ou vim).
Cole o conteúdo abaixo para cada atalho, substituindo os caminhos fictícios.
Para o Interface:

- **Exemplo:Interface**
[Desktop Entry]
Name=Interface
Comment=Executar o script Python para o aplicativo de câmera
Exec=/usr/bin/python3 /home/usuario/MeusProgramas/MeuApp/interface.py
Icon=utilities-terminal
Terminal=false
Type=Application
Para o Relatório:

- **Exemplo:Relatorio**
[Desktop Entry]
Name=Relatório
Comment=Inicia o servidor para gerar relatórios
Exec=/usr/bin/python3 /home/usuario/MeusProgramas/MeuApp/app.py
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Development;

## Salvar o Arquivo
Salve o arquivo com a extensão .desktop, por exemplo, interface.desktop e relatorio.desktop.
Coloque esses arquivos no diretório ~/Desktop se você quiser que eles apareçam na área de trabalho, ou em ~/.local/share/applications para que apareçam no menu de aplicativos.
## Tornar o Arquivo Executável
Abra o terminal.
Navegue até o diretório onde você salvou os arquivos .desktop, por exemplo:
cd ~/Desktop
## Torne o arquivo executável com o comando:
chmod +x interface.desktop
chmod +x relatorio.desktop

## Explicação dos Caminhos Fictícios
## No Windows:

"C:\Program Files\Python\python.exe" é um caminho fictício para o interpretador Python.
"C:\MeusProgramas\MeuApp\interface.py" e "C:\MeusProgramas\MeuApp\app.py" são caminhos fictícios para os scripts Python.
## No Ubuntu:

/usr/bin/python3 é um caminho fictício para o interpretador Python.
/home/usuario/MeusProgramas/MeuApp/interface.py e /home/usuario/MeusProgramas/MeuApp/app.py são caminhos fictícios para os scripts Python.
-** Como fica a aplicaçao no Ubuntu:
![Captura de tela de 2024-09-13 11-43-58](https://github.com/user-attachments/assets/11585f06-6516-40ee-bda4-3b5c76c2bf83)

Esses caminhos fictícios devem ser substituídos pelos caminhos reais onde o Python e os scripts estão localizados no seu sistema. Se seguir essas instruções, você conseguirá criar atalhos funcionais tanto no Windows quanto no Ubuntu para os seus scripts Python.

 
