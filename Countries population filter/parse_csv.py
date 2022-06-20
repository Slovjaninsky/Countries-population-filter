import csv
from database import Database
import sqlalchemy as sql

def parse(file_name: str, db_name: str):
    try:
        file = open(file_name, 'r', encoding='utf-8')
    except IOError:
        print('Comma-separated file with such name does not exist. Terminating program')
        return
    reader = csv.reader(file, delimiter=',')
    header = next(reader)
    db = Database(db_name)
    db.create_table(db_name, {
        header[0] : sql.String,
        header[1] : sql.String,
        header[3] : sql.String,
        header[5] : sql.String,
        header[7] : sql.Integer
        })
    for row in reader:
        try:
            db.insert([
                row[0],
                row[1],
                row[3],
                row[5],
                int(row[7]) if row[7] not in ['–', ''] else None
                ])
        except Exception as ex:
            print(f"Incorrect record {row}: {ex}")
    return db