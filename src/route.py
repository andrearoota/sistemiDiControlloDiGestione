#in views definiamo le routes
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import pandas as pandas
from src import db
from src.model.model import Cliente, Valuta, Vendita, Consumo, Impiego, Risorsa
from src.controller.importFromXLSX import importFromXLSX
from src.controller.article import selectAllArticlesID, selectArticle
import copy

import ast

route = Blueprint('routing', __name__)

@route.route("/")
def home():
    # Dati articolo
    articles = []
    for article in selectAllArticlesID():
        articles.append(selectArticle(article.nrArticolo))

    # Calcolo scostamenti con valuta a consuntivo
        # Definizione strutture base
    revenueCenter = {
        "unitPrice": 0,
        "quantity": 0,
        "percentageOutput": 100
    }

    analysisVariancesRevenueCenter = {
        "BUDGET": copy.deepcopy(revenueCenter),
        "mixStandard": copy.deepcopy(revenueCenter),
        "mixEffettivo": copy.deepcopy(revenueCenter),
        "CONSUNTIVO": copy.deepcopy(revenueCenter)
    }

    from src.controller.sale import countSales
    totalSalesQuantity = countSales()

    for type in ["BUDGET", "CONSUNTIVO"]:
        stmt = (
            db.select(db.func.sum(Vendita.importoVenditeVL / Valuta.tassoCambioMedio).label("unitPrice"))
            .join(Cliente)
            .join(Valuta, (Valuta.codValuta == Cliente.valutaCliente) & (Valuta.budOCons == "CONSUNTIVO"))
            .where(Vendita.tipo == type)
        )

        analysisVariancesRevenueCenter[type]["unitPrice"] = db.session.scalars(stmt).one()
        analysisVariancesRevenueCenter[type]["quantity"] = totalSalesQuantity[type] # Total sales volume

    # Mix data to calculate mix standard and mix effettivo 
    analysisVariancesRevenueCenter["mixStandard"]["unitPrice"] = analysisVariancesRevenueCenter["BUDGET"]["unitPrice"]
    analysisVariancesRevenueCenter["mixStandard"]["quantity"] = analysisVariancesRevenueCenter["CONSUNTIVO"]["quantity"]
    
    analysisVariancesRevenueCenter["mixEffettivo"]["unitPrice"] = analysisVariancesRevenueCenter["BUDGET"]["unitPrice"]
    analysisVariancesRevenueCenter["mixEffettivo"]["quantity"] = analysisVariancesRevenueCenter["CONSUNTIVO"]["quantity"] ### DA SISTEMARE

    return render_template("dashboard.html", articles = articles, analysis = analysisVariancesRevenueCenter)

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

@route.route('/resource',  methods = ['GET'])
def getResource():
    stmt = (
        db.select(Risorsa)
    )
    response = []
    for item in db.session.execute(stmt):
        response.append({
            "id": item.Risorsa.areaProd + '-' + item.Risorsa.codRisorsa,
            "tipo": "risorsa",
            "costoOrarioBudget": item.Risorsa.costoOrarioBudget,
            "costoOrarioConsuntivo": item.Risorsa.costoOrarioConsuntivo,
        })

    stmt = (
        db.text("SELECT Consumo.codiceMP, Consumo.tipo, AVG(Consumo.importoTotaleC / Consumo.qtaC) AS costo \
            FROM Consumo \
            GROUP BY codiceMP, tipo \
            ORDER BY Consumo.codiceMP, Consumo.tipo")
    )
    '''
    lastMP = ""
    for item in db.session.execute(stmt):
        if lastMP == item.codiceMP:
            if item.tipo == "BUDGET":
                response[len(response)-1]["costoOrarioBudget"] = item.costo
            else:
                response[len(response)-1]["costoOrarioConsuntivo"] = item.costo
            lastMP = ""
        elif lastMP == "" or lastMP != item.codiceMP:
            response.append({
                "id": item.codiceMP,
                "tipo": "materia prima",
                "costoOrarioBudget": None,
                "costoOrarioConsuntivo": None,
            })
            if item.tipo == "BUDGET":
                response[len(response)-1]["costoOrarioBudget"] = item.costo
            else:
                response[len(response)-1]["costoOrarioConsuntivo"] = item.costo

            lastMP = item.codiceMP
    '''
    return response

@route.route('/analysisVariances/currency/consuntivo',  methods = ['GET'])
def getAnalysisVariancesCurrency():

    return analysisVariancesRevenueCenter
