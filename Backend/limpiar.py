import sys
sys.path.insert(0, '.')
from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("DELETE FROM plomeros"))
db.commit()
db.close()
print("✅ Tabla plomeros limpiada")