import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost/vida_plus"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora