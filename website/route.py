#in views definiamo le routes
from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pandas
from website import db
from website.model.model import Cliente, Valuta, Vendita, Consumo, Impiego, Risorsa
from website.controller.importFromXLSX import importFromXLSX

route = Blueprint('routing', __name__)

#li definisco all'avvio gli array da riempire in modo tale da poterli riusare in diverse parti del sito
listaPrezziBudget = []
listaQuantitaBudget = []
mixBudget = []
listaPrezziCons = []
listaQuantitaCons = []
mixCons = []
listaQuantitaMixStd = []
mixMixEffettivo = []
listaCostiUnitariMPBudget = []
listaCostiUnitariLAVBudget = []
listaCostiUnitariBudget = []
listaCostiUnitariMPCons = []
listaCostiUnitariLAVCons = []
listaCostiUnitariCons = []
# 0: qtaB, 4: rB, 8:cB , 12: mB -- max 15
listaTotali = []

@route.route("/")
def home():
    from website.controller.article import selectAllArticles
    return render_template("dashboard.html", articles = selectAllArticles())

@route.route('/chi-siamo')
def chiSiamo():
    return render_template("chiSiamo.html")

@route.route('/uploadData')
def renderUploadDataPage():
    return render_template("uploadData.html")

@route.route("/analysesVariances")
def analysesVariances():
    from website.controller.analysesVariances import calcAnalysesVariances
    return calcAnalysesVariances()

@route.route('/database/import')
def databaseImport():
    return importFromXLSX()

@route.route('/file/upload', methods = ['POST'])
def fileUpload():
    # delete old file
    import shutil
    shutil.rmtree('inputXLSX/', False)
    import os
    os.mkdir('inputXLSX/')

    # unzip and save into inputXLSX/
    file = request.files['file']
    import zipfile
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall('inputXLSX/')
    
    # Import file into database
    importFromXLSX()

    return {"error": None}

@route.route('/article/<idArticle>',  methods = ['GET'])
def viewArticle(idArticle):
    from website.controller.article import selectArticle
    return selectArticle(idArticle=idArticle)