# run.py
from flask import Flask
from appmain.routes import main

app = Flask(__name__, template_folder="appmain/templates", static_folder="appmain/static")
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
