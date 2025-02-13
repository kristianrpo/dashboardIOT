import os
import shutil
from dashboardIOT.wsgi import application

db_path = "/tmp/db.sqlite3"
if not os.path.exists(db_path):
    shutil.copyfile("db.sqlite3", db_path)

app = application
