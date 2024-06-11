from sqlalchemy.orm import  declarative_base
from flask_sqlalchemy import SQLAlchemy

#engine = create_engine('postgres://postgres:tim123mo@localhost:5432/print_store')
#db_session = scoped_session(sessionmaker(autocommit=False,
#                                         autoflush=False,
#                                         bind=engine))
Base = declarative_base()

db = SQLAlchemy(model_class=Base)

def init_db():
    import models
    db.create_all()