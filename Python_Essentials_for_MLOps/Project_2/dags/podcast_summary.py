"""
Pipeline que baixa episódios de podcast
Autor: José Augusto
Data: 2023-10-09
"""

# Import libraries
import os
import logging
import pendulum
import requests
import xmltodict
from airflow.decorators import dag, task
from airflow.providers.sqlite.hooks.sqlite import SqliteHook
from airflow.providers.sqlite.operators.sqlite import SQLExecuteQueryOperator

PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
USER_PATH = "/home/augusto/Downloads"
EPISODE_FOLDER = USER_PATH + "/mlops2023/Python_Essentials_for_MLOps/Project_2/dags/episodes"
FRAME_RATE = 16000

# Configuração inicial do logging
# Com level logging.INFO, também é englobado o level logging.ERROR
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


def create_database() -> SQLExecuteQueryOperator:
    """
    Cria a tabela episodes no banco de dados.

    Returns:
        create_database (SQLExecuteQueryOperator): Um operador Airflow
            para criar a tabela no banco de dados.
    """
    return SQLExecuteQueryOperator(
        task_id='create_table_sqlite',
        sql=r"""
        CREATE TABLE IF NOT EXISTS episodes (
            link TEXT PRIMARY KEY,
            title TEXT,
            filename TEXT,
            published TEXT,
            description TEXT,
            transcript TEXT
        );
        """,
        conn_id="podcast_summary"
    )

def get_episodes() -> list:
    """
    Faz o donwload dos metadados dos 50 últimos episódios.

    Return:
        episodes (list): Lista de dicionários contendo os 50 
            últimos episódios lançados.
    """
    try:
        # Download dos dados
        data = requests.get(PODCAST_URL, timeout=20)
        # Parse de xml para dicionário
        feed = xmltodict.parse(data.text)
        # Obtém a lista de episódios
        episodes = feed["rss"]["channel"]["item"]
        # Mostra a quantidade de episódios que foram feitos o download
        logging.info("Found %s episodes.", len(episodes))
        return episodes
    except requests.exceptions.ConnectionError:
        logging.error("Connection Error")
        raise
    except requests.exceptions.Timeout:
        logging.error("Timeout Error")
        raise
    except requests.exceptions.HTTPError:
        logging.error("HTTP Error")
        raise
    except Exception as e:
        logging.error("Error downloading podcast episodes metadata: %s", str(e))
        raise

@task()
def get_episodes_task() -> list:
    """
    Task para requisitar os podcasts do endpoint
    Return:
        list: Lista de dicionários contendo os 50 últimos episódios lançados.
    """
    return get_episodes()

@task()
def load_episodes(episodes: list) -> None:
    """
    Insere no banco de dados os novos episódios baixados e
    impedindo que eles se repitam

    Arg:
        episodes (list): Lista com os metadados dos episódios
    """
    try:
        hook = SqliteHook(sqlite_conn_id="podcast_summary")
        stored = hook.get_pandas_df("SELECT * from episodes;")
        new_episodes = []
        for episode in episodes:
            if episode["link"] not in stored["link"].values:
                logging.info("Storing episode %s on database", episode["link"])
                filename = f"{episode['link'].split('/')[-1]}.mp3"
                new_episodes.append([episode["link"],
                                    episode["title"],
                                    episode["pubDate"],
                                    episode["description"],
                                    filename])
        hook.insert_rows(table="episodes", rows=new_episodes, target_fields=["link",
                                                                            "title",
                                                                            "published",
                                                                            "description",
                                                                            "filename"])
    except Exception as e:
        logging.error("Error loading episodes into the database: %s", str(e))
        raise

@task()
def download_episodes(episodes: list) -> None:
    """
    Faz o download dos arquivos de audio no formato .mp3 dos episódios 
    que ainda não foram baixados

    Arg:
        episodes (list): Lista com os metadados dos episódios
    """
    try:
        for episode in episodes:
            filename = f"{episode['link'].split('/')[-1]}.mp3"
            audio_path = os.path.join(EPISODE_FOLDER, filename)
            if not os.path.exists(audio_path):
                logging.info("Downloading %s", filename)
                audio = requests.get(episode["enclosure"]["@url"], timeout=300)
                with open(audio_path, "wb+") as f:
                    f.write(audio.content)
    except requests.exceptions.ConnectionError:
        logging.error("Connection Error")
        raise
    except requests.exceptions.HTTPError:
        logging.error("HTTP Error")
        raise
    except IOError as e:
        logging.error("Error writing podcast episode to disk: %s", str(e))
        raise
    except Exception as e:
        logging.error("Error downloading podcast episodes in .mp3: %s", str(e))
        raise

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
