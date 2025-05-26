import psycopg2
from db.config import load_config

def connect():
    config = load_config()
    conn = psycopg2.connect(**config)

    return conn