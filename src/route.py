#in views definiamo le routes
from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pandas
from src import db
from src.model.model import Cliente, Valuta, Vendita, Consumo, Impiego, Risorsa
from src.controller.importFromXLSX import importFromXLSX
from src.controller.article import selectAllArticlesID, selectArticle

import ast

route = Blueprint('routing', __name__)

@route.route("/")
def home():
    articles = []
    for article in selectAllArticlesID():
        articles.append(selectArticle(article.nrArticolo))
    return render_template("dashboard.html", articles = articles)

@route.route('/chi-siamo')
def chiSiamo():
    return render_template("chiSiamo.html")

@route.route('/uploadData')
def renderUploadDataPage():
    return render_template("uploadData.html")

@route.route("/analysisVariances")
def analysisVariances():
    from src.controller.analysisVariances import calcanalysisVariances
    return calcanalysisVariances(selectAllArticlesID())

@route.route("/analysisVariances/market")
def analysisVariancesMarket():
    from src.controller.analysisVariances import calcanalysisVariances
    response = {}

    stmt = db.select(Valuta).distinct().where(Valuta.budOCons == "BUDGET")
    for market in db.session.execute(stmt): # Calcoli per ogni market

        # Faccio analisi scostamenti per mercato (Market)
        response[market.Valuta.codValuta] = ast.literal_eval(market.Valuta.analysisVariances)
        
        # Trovo i clienti che hanno acquistato in un mercato
        response[market.Valuta.codValuta]["client"] = []
        stmt = (
            db.select(Cliente)
            .where(Cliente.valutaCliente == market.Valuta.codValuta)
        )

        # Per ogni cliente faccio analisi scostamenti (Market > Client)
        for client in db.session.execute(stmt):            
            response[market.Valuta.codValuta]["client"].append(ast.literal_eval(client.Cliente.analysisVariances))

    return response

@route.route('/database/import')
def databaseImport():
    return importFromXLSX()

@route.route('/file/upload', methods = ['POST'])
def fileUpload():
    # delete old file
    import shutil
    shutil.rmtree('storage/', False)
    import os
    os.mkdir('storage/')

    # unzip and save into storage/
    file = request.files['file']
    import zipfile
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall('storage/')
    
    # Import file into database
    importFromXLSX()

    return {"error": None}

@route.route('/article/<idArticle>',  methods = ['GET'])
def viewArticle(idArticle):
    from src.controller.article import selectArticle
    return selectArticle(idArticle=idArticle)