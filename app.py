import sqlite3
from flask import Flask, request, jsonify

conn = sqlite3.connect('final_project.db')

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to the Basketball Database App!"

if __name__ == '__main__':
    app.run(debug=True)


