# Airflow Data Pipeline to Download Podcasts

## Introdução
O projeto é uma pipeline que será executada diariamente e contará com um banco de dados relacional (SQLite) para armazenas os metadados dos episódios que já foram baixados. Ele utiliza o airflow para construir uma pipeline que procura por novos episódios de podcast diariamente para fazer download. Todos os dias é otbido, a partir [deste endpoint](https://www.marketplace.org/feed/podcast/marketplace/), um arquivo .xml com 50 metadados dos episódios de podcast mais recentes, caso algum deles não esteja no banco de dados, ele é adicionado e depois feito o download do arquivo em áudio, no formato .mp3.

## Como executar
Ao executar este projeto no codespace, não será possível entrar na aplicação do airflow. Apesar de ser possível acessar a porta 8080 (porta padrão ao executar o ambiente vitual do airflow), não será possível fazer login e interagir com as DAGs.

Ao executar com sistemas operacionais do tipo unix (linux ou macOS, por exemplo), é possível acompanhar o andamento das pipelines, seja atual ou não, ao executar o ambiente do airflow.

Para windows, eu consegui fazer funcionar até certo ponto. Ao tentar iniciar o ambiente virtual, o airflow roda o comando ``$ pwd``, que é nativo dos sitemas operacionais do tipo unix, interropendo, assim, a inicialização do ambiente virtual.

Garanta que você tem o python 3.10.x instalado. Ele será necessário para instalar o [airflow 2.7.1](https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html#airflow-2-7-1-2023-09-07), que é a versão mais recente até a data de implementação desta pipeline.

<strong>Para criar um ambiente virtual, siga os passos abaixo.</strong>
Obs.: Os comando a seguir devem ser executados a partir da pasta ``Project_2``.

Criar um ambiente virtual chamado airflow
```
python3.10 -m venv airflow
```

Ativar o ambiente:
```
source ./airflow/bin/activate
```

Para instalar o airflow:
```
AIRFLOW_VERSION=2.7.1
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

Depois que estiver instalado, você pode executar a aplicação:
```
airflow standalone
```

Após isso, será criado automaticamente a pasta ``~/airflow`` e a aplicação ficará disponível na porta ``http://localhost:8080``. No terminal será disponibilizado seu <strong>login e senha</strong>, e é de extrema importância que você os encontre para que possa entrar na aplicação.

Agora será preciso fazer uma auteração nas configurações do airflow.

Entre na pasta ``dags/`` e obtenha e copie para área de transferência o caminho até este diretótio:
```
cd dags/
pwd
```

Depois de copiar o caminho da pasta, entre no arquivo de configurações do airflow. Para obter o caminho até o esse arquivo:
```
find ~/ -name "airflow.cfg"
```

Entre no arquivo com um editor de texto do próprio terminal:
```
nano {path_of_the_airflow.cfg_file}
```

Edite a variável ``dags_folder`` para que aponte para a sua pasta dags, cujo caminho você já possui na área de transferência. No meu caso ficou assim:
```
dags_folder = /home/augusto/Downloads/mlops2023/Python_Essentials_for_MLOps/Project_2/dags
```

Instale as dependência do projeto:
```
pip install -r requirements.txt
```

Como utilizaremos um banco de dados SQLite, temos que instalá-lo:
```
wget https://www.sqlite.org/snapshot/sqlite-snapshot-202309111527.tar.gz
tar -xzvf sqlite-snapshot-202309111527.tar.gz
cd sqlite-snapshot-202309111527
./configure
make
sudo make install
sqlite3 --version
```

Em um terminal, dentro da pasta ``dags/``, criaremos o banco de dados:
```
sqlite3 episodes.db
.databases
.quit
```

Agora precisamos fazer uma conexão do airflow com o banco de dados. Substitua o caminho a seguir pelo caminho até o seu banco de dados ``episodes.db``, criado anteriormente:
```
airflow connections add 'podcast_summary' --conn-type 'sqlite' --conn-host '/home/augusto/Downloads/mlops2023/Python_Essentials_for_MLOps/Project_2/dags/episodes.db'
```

Agora, cheque a conexão do airflow com o seu banco de dados:
```
airflow connections get podcast_summary
```

Agora, pare a execução da aplicação do airflow e a execute novamente para aplicar as mudanças feitas:
```
airflow standalone
```

Na página inicial, em que há uma lista com as DAGs, procure pela opção "podcast_summary" e despause essa DAG clicando no toggle ao lado de seu título. Em seguida, clique no título e você obterá mais informações sobre ela, como grafos e logs sobre cada task da pipeline. Para executar a pipeline, basta clicar no ícone de "play" na parte superior direita.

![fwefgr](images/airflow.png)

A última task foi interrompida, uma vez que não quero os 50 episódios de podcast, mas alguns foram baixados para testar a eficiência da pipeline.

## O código
A pipeline é criado a partir do decorador @dag(), que está sendo configurada ter o nome de "podcast_summary", ser executada diariamente, ter uma data de incício no dia 08/10/2023 e não ser executado retroativamente, ou seja, ele indica que o DAG não deve executar tarefas retroativamente para as datas em que o DAG deveria ter sido executado, mas não foi devido a atrasos ou falta de execução.
```
@dag(
    dag_id='podcast_summary',
    schedule_interval="@daily",
    start_date=pendulum.datetime(2023, 10, 8),
    catchup=False
)
def podcast_summary():
    """
    Cria a pipeline de dados com o decorador @dag
    """

    # Cria o banco de dados
    logging.info("Creating the table, if it don't exists")
    database = create_database()

    # Faz o download dos episódios
    logging.info("Downloading episodes metadata")
    podcast_episodes = get_episodes_task()

    # Especifica que primeiro deve ser criado o banco de dados e
    # depois feito o donwload dos episódios
    database.set_downstream(podcast_episodes)

    # Armazena os novos episódios baixados
    load_episodes(podcast_episodes)

    # Faz o download dos arquivos de audio
    download_episodes(podcast_episodes)

podcast_summary()
```
