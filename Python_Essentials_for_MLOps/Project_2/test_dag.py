"""
Testa a DAG criada a partir da pipeline
Autor: José Augusto
Data: 2023-10-09
"""

# Importa bibliotecas
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

def test_create_database(create_database_fixture) -> None:
    """
    Testa se o dado proveniente da fixture create_database_fixture
    é uma instância de SQLExecuteQueryOperator.

    Args:
        create_database_fixture (SQLExecuteQueryOperator): banco de dados SQLite
    """

    database = create_database_fixture

    assert isinstance(database, SQLExecuteQueryOperator)

def test_get_episodes(get_episodes_fixture) -> None:
    """
    Testa se o dado proveniente da fixture fetch_data_fixture é uma lista de
    tamanho 50.

    Args:
        get_episodes_fixture (list): lista de metadados dos episódios
    """

    episodes = get_episodes_fixture

    assert isinstance(episodes, list)
    assert len(episodes) == 50
