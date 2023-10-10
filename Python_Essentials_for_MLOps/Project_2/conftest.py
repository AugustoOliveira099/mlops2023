"""
Provê as fixtures para o pytest
Autor: José Augusto
Data: 2023-10-09
"""

import pytest
from dags.podcast_summary import get_episodes
from dags.podcast_summary import create_database
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

@pytest.fixture
def create_database_fixture() -> SQLExecuteQueryOperator:
    """
    Simula um banco de dados SQLite

    Return:
       SQLExecuteQueryOperator: Banco de dados SQLite
    """
    return create_database()

@pytest.fixture
def get_episodes_fixture() -> list:
    """
    Simula uma lista de episódios de podcast

    Return:
        list: Lista de episódios de podcast
    """
    print(type(get_episodes()))
    return get_episodes()
