import psycopg2


class Handler:
    def __init__(self, table_name=None, processing=None, *args, **kwargs):
        self.table_name = table_name
        self.processing = processing
        self.args = args
        self.kwargs = kwargs


class DBManager:
    def __init__(self, db_url, debug=False):
        self.db_url = db_url
        self.conn = None
        self.debug = debug

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def do(self, handler: Handler):
        """handler.processingで見分ける"""
        if handler.processing == "execute":
            return self._execute(*handler.args, **handler.kwargs)
        elif handler.processing == "fetch_column":
            return self.fetch_column(handler.table_name, *handler.args, **handler.kwargs)
        elif handler.processing == "insert":
            return self.insert(handler.table_name, *handler.args, **handler.kwargs)
        elif handler.processing == "delete":
            return self.delete(handler.table_name, *handler.args, **handler.kwargs)
        elif handler.processing == "update":
            return self.update(handler.table_name, *handler.args, **handler.kwargs)
        else:
            return None

    def _execute(self, sql, fetch=True):
        output = []
        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(sql)
        if fetch:
            data = cur.fetchall()
            for i in data:
                # output.append(list(i)[0]) <- 言いたくないけどクソ処理　関数の名前詐欺してるよ
                # executeなら結果全部返すようにしろよ(言葉遣い汚くてすまん)
                output.append(i)
        cur.close()

        return output

    def fetch_column(self, table, column, where=None, fetch=True):
        output = []
        self.conn = self.get_connection()
        cur = self.conn.cursor()
        if where is not None:
            cur.execute(f"SELECT {column} FROM {table} WHERE {where};")
        else:
            cur.execute(f"SELECT {column} FROM {table};")

        if fetch:
            data = cur.fetchall()
            for i in data:
                output.append(list(i)[0])
        cur.close()

        return output

    def insert(self, table, data, column):
        columns = f"{column}".replace("'", "")
        datas = f"{data}".replace("'", "")

        cmd = f"INSERT INTO {table} {columns} VALUES {datas};"
        if self.debug:
            print(cmd)

        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(cmd)
        self.conn.commit()
        cur.close()

    def delete(self, table, data, column):
        columns = f"{column}".replace("'", "")
        datas = f"{data}".replace("'", "")

        cmd = f"DELETE FROM {table} WHERE {columns} = {datas};"

        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(cmd)
        self.conn.commit()
        cur.close()

    def update(self, table, data, column, where=None):

        if where is not None:
            cmd = f"UPDATE {table} SET {column} = {data} WHERE {where}"
        else:
            cmd = f"UPDATE {table} SET {column} = {data}"

        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(cmd)
        self.conn.commit()
        cur.close()
