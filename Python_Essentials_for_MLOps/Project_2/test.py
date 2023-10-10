"""
Pipeline feito com airflow para fazer download de poscasts 
e armazená-los em um databe. Utilizaremos o SQLite para isso.
"""

"""
Main DAG file for the podcast summary project.
Author: Morsinaldo Medeiros
Date: 2023-09-30
"""
# import libraries
import os
import json
import logging
import pendulum
import requests
import xmltodict
import pandas as pd

from airflow.decorators import dag, task
from airflow.providers.sqlite.operators.sqlite import SQLExecuteQueryOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

# set constants
PODCAST_URL = "https://www.marketplace.org/feed/podcast/marketplace/"
PROJECT_FOLDER = "/home/augusto/Downloads/mlops2023/mlops2023/Python_Essentials_for_MLOps/Project_02/"
EPISODE_FOLDER = PROJECT_FOLDER + "/dags/episodes"
FRAME_RATE = 16000

# set the logging level
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

def create_database() -> SQLExecuteQueryOperator:
    """
    Creates the database table.

    Returns:
        create_database (SQLExecuteQueryOperator): An Airflow operator for 
            creating the database table.
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
        conn_id="podcasts"
    )


def fetch_data() -> list:
    """
    Downloads podcast episodes as audio files.

    Returns:
        audio_files (list): A list of dictionaries containing audio file information.
    """
    try:
        # download data
        data = requests.get(PODCAST_URL, timeout=15)

        # transform to dict
        feed = xmltodict.parse(data.text)

        # get episodes
        episodes = feed["rss"]["channel"]["item"]
        logging.info("Found %s episodes.", len(episodes))
        return episodes
    except requests.RequestException as e:
        logging.error("Error fetching podcast episodes: %s", str(e))
        raise
    except Exception as general_error:
        logging.error("Error parsing podcast episodes: %s", str(general_error))
        raise


@task()
def get_episodes() -> list:
    """
    Task to fetch podcast episodes from the RSS feed.

    Returns:
        episodes (list): A list of dictionaries containing podcast episode information.
    """
    return fetch_data()

def load_data(episodes: list) -> list:
    """
    Loads new podcast episodes into the database.

    Args:
        episodes (list): A list of dictionaries containing podcast episode information.

    Returns:
        new_episodes (list): A list of new episode records.
    """
    try:
        # connect to the database
        hook = SqliteHook(sqlite_conn_id="podcasts")

        # get stored episodes
        stored_episodes = hook.get_pandas_df("SELECT * from episodes;")
        new_episodes = []

        # check for new episodes
        for episode in episodes:
            if episode["link"] not in stored_episodes["link"].values:
                filename = f"{episode['link'].split('/')[-1]}.mp3"
                new_episodes.append([episode["link"],
                                     episode["title"],
                                     episode["pubDate"],
                                     episode["description"],
                                     filename])

        # insert new episodes into the database
        hook.insert_rows(table='episodes',
                         rows=new_episodes,
                         target_fields=["link",
                                        "title",
                                        "published",
                                        "description",
                                        "filename"])
        logging.info("Loaded %s new episodes.", len(new_episodes))
        return new_episodes
    except Exception as e:
        logging.error("Error loading episodes into the database: %s", str(e))
        raise

@task()
def load_episodes(episode_data: list) -> list:
    """
    Task to load new podcast episodes into the database.

    Args:
        episode_data (list): A list of dictionaries containing podcast episode information.

    Returns:
        new_episodes (list): A list of new episode records.
    """
    return load_data(episode_data)

def download_data(episodes: list) -> list:
    """
    Download the specified podcast episodes.

    Args:
        episodes (list): A list of dictionaries containing podcast episode information.

    Returns:
        audio_files (list): A list of dictionaries containing audio file information.
    """

    audio_files = []

    for episode in episodes:
        try:
            name_end = episode["link"].split('/')[-1]
            filename = f"{name_end}.mp3"
            audio_path = os.path.join(EPISODE_FOLDER, filename)
            if not os.path.exists(audio_path):
                logging.info("Downloading episode %s", episode["link"])
                audio = requests.get(episode["enclosure"]["@url"], timeout=15)
                with open(audio_path, "wb+") as file:
                    file.write(audio.content)
            audio_files.append({
                "link": episode["link"],
                "filename": filename
            })
        except requests.RequestException as e:
            logging.error("Error downloading podcast episode: %s", str(e))
            raise
        except IOError as e:
            logging.error("Error writing podcast episode to disk: %s", str(e))
            raise
        except Exception as general_error:
            logging.error("Error downloading podcast episode: %s", str(general_error))
            raise

    return audio_files

@task()
def download_episodes(episode_data: list) -> list:
    """
    Task to download the specified podcast episodes.

    Args:
        episode_data (list): A list of dictionaries containing podcast episode information.

    Returns:
        audio_files (list): A list of dictionaries containing audio file information.
    """
    return download_data(episode_data)

def fetch_untranscribed_episodes(hook: SqliteHook) -> pd.DataFrame:
    """
    Fetches untranscribed episodes from the database.
    
    Args:
        hook (SqliteHook): A hook to connect to the database.
        
    Returns:
        untranscribed_episodes (pd.DataFrame): A dataframe containing untranscribed episodes.
    """

    query = (
        "SELECT * "
        "FROM episodes "
        "WHERE transcript IS NULL;"
    )
    return hook.get_pandas_df(query)

def initialize_transcription_model() -> Model:
    """
    Initialize the transcription model.

    Returns:
        model (Model): The transcription model.
    """
    return Model(model_name="vosk-model-en-us-0.22-lgraph")

def transcribe_audio(row: pd.Series, rec: KaldiRecognizer) -> str:
    """
    Transcribes the specified audio file.

    Args:
        row (pd.Series): A row from the dataframe containing audio file information.
        rec (KaldiRecognizer): The transcription model.

    Returns:
        transcript (str): The transcript of the audio file.
    """
    filepath = os.path.join(EPISODE_FOLDER, row["filename"])
    mp3 = AudioSegment.from_mp3(filepath).set_channels(1).set_frame_rate(FRAME_RATE)

    step = 20000
    transcript = ""
    for i in range(0, len(mp3), step):
        logging.debug("Transcribing %s at %s", row["filename"], i)
        segment = mp3[i:i + step]
        rec.AcceptWaveform(segment.raw_data)
        result = rec.Result()
        text = json.loads(result)["text"]
        transcript += text
    return transcript

def store_transcript(hook: SqliteHook, link: str, transcript: str) -> None:
    """
    Stores the transcript in the database.

    Args:
        hook (SqliteHook): A hook to connect to the database.
        link (str): The link to the podcast episode.
        transcript (str): The transcript of the podcast episode.
    """
    hook.insert_rows(
        table='episodes',
        rows=[[link, transcript]],
        target_fields=["link", "transcript"],
        replace=True
    )

@task()
def speech_to_text() -> None:
    """
    Transcribe the audio content of the episodes to text.

    Returns:
        None
    """

    hook = SqliteHook(sqlite_conn_id="podcasts")
    untranscribed_episodes = fetch_untranscribed_episodes(hook)

    model = initialize_transcription_model()
    rec = KaldiRecognizer(model, FRAME_RATE)
    rec.SetWords(True)

    for _, row in untranscribed_episodes.iterrows():
        logging.info("Transcribing %s", row["filename"])
        transcript = transcribe_audio(row, rec)

        store_transcript(hook, row["link"], transcript)

@dag(
    dag_id='podcast_summary',
    schedule="@daily",
    start_date=pendulum.datetime(2023, 10, 9),
    catchup=False,
)

def podcast_summary():
    """
    Definition of the DAG.

    Returns:
        None
    """

    # create the directory for the episodes
    if not os.path.exists("episodes"):
        os.makedirs("episodes")

    # create the database
    database = create_database()

    # fetch episodes
    podcast_episodes = get_episodes()

    # set downstream dependencies
    database.set_downstream(podcast_episodes)

    # load episodes
    load_episodes(podcast_episodes)

    # download episodes
    download_episodes(podcast_episodes)

    # transcribe episodes
    # speech_to_text()

podcast_summary()
