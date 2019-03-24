import psycopg2

class DBHandler:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def execute(self, cmd, fetch=True):
        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(cmd)
        if fetch:
            data = cur.fetchall()
            output = []
            for i in data:
                output.append(list(i)[0])
        cur.close()

        return output

    def fetch_column(self, column, table, where=None, fetch=True):
        self.conn = self.get_connection()
        cur = self.conn.cursor()
        if where is not None:
            cur.execute(f"SELECT {column} FROM {table} WHERE {where};")
        else:
            cur.execute(f"SELECT {column} FROM {table};")

        if fetch:
            data = cur.fetchall()
            output = []
            for i in data:
                output.append(list(i)[0])
        cur.close()

        return output

    def insert_data(self, data, column, table):
        columns = f"{column}".replace("'","")
        datas = f"{data}".replace("'", "")

        cmd = f"INSERT INTO {table} {columns} VALUES {datas};"
        print(cmd)

        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(cmd)
        self.conn.commit()
        cur.close()

    def delete_data(self, data, column, table):
        columns = f"{column}".replace("'", "")
        datas = f"{data}".replace("'", "")

        cmd = f"DELETE FROM {table} WHERE {columns} = {datas};"

        self.conn = self.get_connection()
        cur = self.conn.cursor()
        cur.execute(cmd)
        self.conn.commit()
        cur.close()
