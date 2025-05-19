from app.db.base_class import Base

# models/__init__.py에서 전부 import 되기만 하면 Base.metadata에 등록됨
from app.db import models
