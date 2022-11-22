#in views definiamo le routes
from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pandas
from website import db
from website.model.model import Cliente, Valuta, Vendita, Consumo, Impiego, Risorsa

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

@route.route('/chiSiamo')
def chiSiamo():
    return render_template("chiSiamo.html")

@route.route("/analysesVariances")
def analysesVariances():
    from website.controller.analysesVariances import calcAnalysesVariances
    return calcAnalysesVariances()

@route.route('/database/import')
def databaseImport():
    from website.controller.importFromXLSX import importFromXLSX
    return importFromXLSX()

@route.route('/article/<idArticle>',  methods = ['GET'])
def viewArticle(idArticle):
    from website.controller.article import selectArticle
    return selectArticle(idArticle=idArticle)