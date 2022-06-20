import sqlalchemy as sql

class Database(object):
    """a class for storing a database"""

    def __init__(self, name: str):
        self.engine = sql.create_engine(f'sqlite:///{name}.db')
        self.conn = self.engine.connect()
        self.meta = sql.MetaData(self.engine)
        self.meta.reflect(bind = self.engine)
        self.active_table = None

    def connect_table(self, name: str):
        if name in self.meta.tables:
            self.active_table = sql.Table(name, self.meta, autoload=True)
            self.meta.create_all(self.engine)
            
    def create_table(self, name: str, header: dict):
        if name not in self.meta.tables:
            self.active_table = sql.Table(
                name, self.meta,
                *[sql.Column(col, header[col], primary_key = list(header.keys()).index(col) == 0) for col in header]
                )
            self.meta.create_all(self.engine)

    def insert(self, row: list):
        trans = self.conn.begin()
        ins = self.active_table.insert().values(row)
        self.conn.execute(ins)
        trans.commit()

    def select(self, filter: dict = None):
        if self.active_table == None:
            return
        sel = sql.select(self.active_table)
        if filter:
            for col in filter:
                if(len(filter[col]) != 0):
                    sel = sel.where(self.active_table.c[col].in_(filter[col]))
        self.last_operation = sel
        res = self.conn.execute(sel)
        return res

    def select_min(self, column: str, filter: dict = None):
        if self.active_table == None:
            return
        sel = sql.select([self.active_table.c[0], sql.func.min(self.active_table.c[column])])
        if filter:
            for col in filter:
                if(len(filter[col]) != 0):
                    sel = sel.where(self.active_table.c[col].in_(filter[col]))
        self.last_operation = sel
        res = self.conn.execute(sel)
        return res

    def select_max(self, column: str, filter: dict = None):
        if self.active_table == None:
            return
        sel = sql.select([self.active_table.c[0], sql.func.max(self.active_table.c[column])])
        if filter:
            for col in filter:
                if(len(filter[col]) != 0):
                    sel = sel.where(self.active_table.c[col].in_(filter[col]))
        self.last_operation = sel
        res = self.conn.execute(sel)
        return res

    def select_sum(self, column: str, filter: dict = None):
        if self.active_table == None:
            return
        sel = sql.select([sql.func.sum(self.active_table.c[column])])
        if filter:
            for col in filter:
                if(len(filter[col]) != 0):
                    sel = sel.where(self.active_table.c[col].in_(filter[col]))
        self.last_operation = sel
        res = self.conn.execute(sel)
        return res

    def select_column(self, column: str, filter: dict = None):
        if self.active_table == None:
            return
        sel = sql.select([self.active_table.c[0], self.active_table.c[column]])
        if filter:
            for col in filter:
                if(len(filter[col]) != 0):
                    sel = sel.where(self.active_table.c[col].in_(filter[col]))
        self.last_operation = sel
        res = self.conn.execute(sel)
        return res