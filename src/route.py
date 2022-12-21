#in views definiamo le routes
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import pandas as pandas
from src import db
from src.model.model import Client, Currency, Sales, Consumption, Impiego, Risorsa
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
        articles.append(selectArticle(article.articleNumber))

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
            db.select(db.func.sum(Sales.salesAmount / Currency.exchangeRate).label("unitPrice"))
            .join(Client)
            .join(Currency, (Currency.currencyCode == Client.currency) & (Currency.budOrCons == "CONSUNTIVO"))
            .where(Sales.budOrCons == type)
        )

        analysisVariancesRevenueCenter[type]["unitPrice"] = db.session.scalars(stmt).one()
        analysisVariancesRevenueCenter[type]["quantity"] = totalSalesQuantity[type] # Total sales volume
    
    # Get currency
    stmt = (
        db.text(
            "SELECT Currency.currencyCode, Currency.exchangeRate AS tassoBudget, CurrencyCons.exchangeRate AS tassoConsuntivo \
                FROM Currency \
                    INNER JOIN Currency as CurrencyCons ON Currency.currencyCode = CurrencyCons.currencyCode AND CurrencyCons.budOrCons LIKE 'CONSUNTIVO' \
                        WHERE Currency.budOrCons LIKE 'BUDGET'"
        )
    )
    currencies = db.session.execute(stmt)

    return render_template("dashboard.html", articles = articles, analysis = analysisVariancesRevenueCenter, currencies = currencies)

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

    stmt = db.select(Currency).distinct().where(Currency.budOrCons == "BUDGET")
    for market in db.session.execute(stmt): # Calcoli per ogni market

        # Faccio analisi scostamenti per mercato (Market)
        response[market.Currency.currencyCode] = ast.literal_eval(market.Currency.analysisVariances)
        
        # Trovo i clienti che hanno acquistato in un mercato
        response[market.Currency.currencyCode]["client"] = []
        stmt = (
            db.select(Client)
            .where(Client.currency == market.Currency.currencyCode)
        )

        # Per ogni cliente faccio analisi scostamenti (Market > Client)
        for client in db.session.execute(stmt):            
            response[market.Currency.currencyCode]["client"].append(ast.literal_eval(client.Client.analysisVariances))

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
        db.text("SELECT Consumption.rawMaterialCode, Consumption.budOrCons, AVG(Consumption.totalAmountC / Consumption.quantityC) AS costo \
            FROM Consumption \
            GROUP BY Consumption.rawMaterialCode, Consumption.budOrCons \
            ORDER BY Consumption.rawMaterialCode, Consumption.budOrCons")
    )
    '''
    lastMP = ""
    for item in db.session.execute(stmt):
        if lastMP == item.rawMaterialCode:
            if item.tipo == "BUDGET":
                response[len(response)-1]["costoOrarioBudget"] = item.costo
            else:
                response[len(response)-1]["costoOrarioConsuntivo"] = item.costo
            lastMP = ""
        elif lastMP == "" or lastMP != item.rawMaterialCode:
            response.append({
                "id": item.rawMaterialCode,
                "tipo": "materia prima",
                "costoOrarioBudget": None,
                "costoOrarioConsuntivo": None,
            })
            if item.tipo == "BUDGET":
                response[len(response)-1]["costoOrarioBudget"] = item.costo
            else:
                response[len(response)-1]["costoOrarioConsuntivo"] = item.costo

            lastMP = item.rawMaterialCode
    '''
    return response

@route.route('/analysisVariances/currency/consuntivo',  methods = ['GET'])
def getAnalysisVariancesCurrency():

    return analysisVariancesRevenueCenter
