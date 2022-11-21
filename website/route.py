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
    return render_template("home.html")

@route.route("/analysesVariances")
def analysesVariances():
    from website.controller.analysesVariances import calcAnalysesVariances
    return calcAnalysesVariances()

@route.route('/database/import')
def databaseImport():
    from website.controller.importFromXLSX import importFromXLSX
    return importFromXLSX()

@route.route('/specificaArticolo',  methods = ['GET', 'POST'])
def art():
    z = 0 #una flag
    if request.method == "POST":
        #faccio un bel load prima poi recupo l'indice di quello che devo trovare e mostro tutti i risultati del singolo articolo
        lista = db.session.query(Vendita.nrArticolo).distinct().all()
        print(lista)
        nrArt = request.form.get('nrArt')
        x = Vendita.query.filter_by(nrArticolo = nrArt).first() #controllo che ci sia almeno una vendita di quel prodotto per vedere se l'articolo esiste
        if x :
            # recuperare indice per poi accedere a tutti i dati del singolo articolo
            indice = 0
            trovato = 'false'
            for i in range(len(lista)):
                if trovato == 'false':
                    if nrArt != lista[i].nrArticolo:
                        indice = indice + 1
                        print(indice)
                    else:
                        trovato = 'true'
                    # se lo ho trovato scorre lista ma senza entrare ed aggiornare l'indice
            print(indice)
            i = indice
            z = 1
            flash('ARTICOLO TROVATO ', category = 'success')
            return render_template("specificaArticolo.html", z=z, nrArt = nrArt, puB = listaPrezziBudget[i], qtvB = listaQuantitaBudget[i], mB = mixBudget[i], cmpB = listaCostiUnitariMPBudget[i], clavB = listaCostiUnitariLAVBudget[i], puMS = listaPrezziBudget[i], qtvMS = listaQuantitaMixStd[i], mMS = mixBudget[i], cmMS = listaCostiUnitariMPBudget[i], clavMS = listaCostiUnitariLAVBudget[i], puME = listaPrezziBudget[i], mME = mixMixEffettivo[i], cmME = listaCostiUnitariMPBudget[i], clavME = listaCostiUnitariLAVBudget[i], puC = listaPrezziCons[i], qtvC = listaQuantitaCons[i], mC = mixCons[i], cmpC = listaCostiUnitariMPCons[i], clavC = listaCostiUnitariLAVCons[i])
        else:
            flash(' INSERISCI UN CODICE VALIDO!! ', category = 'error')
    return render_template("specificaArticolo.html", z=z )

@route.route('/chiSiamo')
def chiSiamo():
    return render_template("chiSiamo.html")

@route.route('/modifica')
def modify():
    #modificare il tipo dell'art 841 e 814 a consuntivo basandoci sul nrMovimento
    tochange = 'Consuntivo'
    db.session.query(Vendita).filter(Vendita.nrMovimentoV == 35089).update({'tipo': tochange})
    db.session.commit()
    query = Vendita.query.filter_by(nrMovimentoV = 35089).first()
    print(query.tipo)

    #altro articolo

    db.session.query(Vendita).filter(Vendita.nrMovimentoV == 35550).update({'tipo': tochange})
    db.session.commit()
    query = Vendita.query.filter_by(nrMovimentoV = 35550).first()
    print(query.tipo)

    return render_template("base.html")

def conversioneValuta (prezzo, codiceCliente, tipo) :
    subtotaleInEuro = prezzo
    clien1 = Cliente.query.filter_by(codiceCliente=codiceCliente).first()
    valClien = clien1.valutaCliente
    #print(" CONVERSIONE VALUTA ----> " + codiceCliente + " codice valuta: " + str(valClien))
    if valClien == 2:  # caso in cui il cliente paga in dollari
        if tipo == "BUDGET":
            subtotaleInEuro = subtotaleInEuro * 0.94868  # conversione dollaro/euro a budget
        else:
            subtotaleInEuro = subtotaleInEuro * 0.8338  # conversione dollaro/euro a consuntivo
    elif valClien == 3:  # caso in cui il cliente paga in yen
        if tipo == "BUDGET":
            subtotaleInEuro = subtotaleInEuro * 0.0081300813  # conversione yen/euro a budget
        else:
            subtotaleInEuro = subtotaleInEuro * 0.00740685875  # conversione yen/euro a consuntivo
    return subtotaleInEuro

def CalcoloRisorsa (tempoImpiegato, tipo, ris, aProd) :
    return


