from db import Database
from auth import Auth
from app import MainWindow

if __name__ == "__main__":
    db = Database("service", "postgres", "1234", "localhost", 5432)
    if db.connect():
        auth = Auth(db)
        auth.root.mainloop()
        if auth.is_auth:
            app = MainWindow(db, auth.user_data)
            app.root.mainloop()
        db.close()

