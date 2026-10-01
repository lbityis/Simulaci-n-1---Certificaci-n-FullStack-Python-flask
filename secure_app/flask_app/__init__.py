from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "clave_secreta_bookhub"

bcrypt = Bcrypt(app)