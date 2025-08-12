import sqlite3
#import numpy

class userA:
    nameOperating = ""
    def __init__(self,name:str):
        self.nameOperating = name
        connCurrent=sqlite3.connect(self.nameOperating)
        connCurrent.execute("""CREATE TABLE IF NOT EXISTS DATA 
            (KEY TEXT PRIMARY KEY,
            VALUE INTEGER);
        """)
        connCurrent.commit()
        connCurrent.close()

    def Write (self,key : str, value : int) -> int:
        try:
            connWrite = sqlite3.connect(self.nameOperating)
            connWrite.execute("INSERT INTO DATA (KEY,VALUE) \
                            VALUES (?,?)", (key,value))
            connWrite.commit()
            connWrite.close()
            return 0
        except sqlite3.IntegrityError:
            return 1
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return 2

    def Modify (self,key : str, value : int) -> int:
        try:
            connWrite = sqlite3.connect(self.nameOperating)
            connWrite.execute(" \
                              UPDATE DATA \
                              SET VALUE = ? \
                              WHERE KEY = ? \
            ",(value,key))
            connWrite.commit()
            connWrite.close()
            return 0
        except sqlite3.Error as e:
            return 1

if __name__ == "__main__":
    alice = userA("0Demo.db")
    print(alice.Write("accountBalance",100))
    print(alice.Modify("accountBalance",700))
    pass

