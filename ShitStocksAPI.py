import flask
from flask import request, jsonify
import alphavantage
import sqlite3
import socket

app = flask.Flask(_name_)
app.config["DEBUG"] = True

#data

@app.route("/", methods = ["GET"])
def home():
    return '''<h1>ShitStocks Data<h1>
    <p>A api for accessing data from the ShitStocks service<p>'''

@app.route("/shitstocks/companies/list", methods = ["GET"])
def companies_list():
    list = open("companies_list.txt", "r")
    read_list = list.read()
    return jsonify(read_list)

