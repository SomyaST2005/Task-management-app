import mysql.connector
from config import Config


def get_db():
    conn = mysql.connector.connect(**Config.DB_CONFIG)
    return conn


def get_db_dict():
    conn = mysql.connector.connect(**Config.DB_CONFIG)
    return conn, conn.cursor(dictionary=True)
