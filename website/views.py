#in views definiamo le routes
from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
from website import db
from website.models import Cliente, Valuta, Vendita, Consumo, Impiego, Risorsa

views = Blueprint('views', __name__)

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

@views.route('/scostamenti')
def fai():
    print(db.session)
    llista = []
    lista = db.session.query(Vendita.nrArticolo).distinct().all()
    for i in range(len(lista)):
        llista.append(lista[i])
    print(lista)
    print(llista)
    print(" quanti articoli ho: " + str(len(lista)))


    if len(listaTotali) < 1 :
        qtaBudget = 0  # qtaTOTALE RIGA D8 exe scostamenti
        for i in range(len(lista)):  # for con il distinct
            #
            qtasingola = 0
            prezzosingolo = 0.00
            prezzotot = 0.00
            volume = 0
            tipo = "BUDGET"
            arttocheck = lista[i].nrArticolo
            #
            print("TABELLA RICAVI => " + tipo + " => " + arttocheck)
            artB = Vendita.query.filter_by(nrArticolo=arttocheck, tipo=tipo).all()
            for j in range(len(artB)):  # for con il group by
                qtasingola = qtasingola + artB[j].qta
                prezzosingolo = artB[j].importoVenditeVL
                prezzosingolo = conversioneValuta(prezzosingolo, artB[j].nrOrigine, tipo)
                prezzotot = prezzotot + prezzosingolo
            volume = qtasingola
            listaQuantitaBudget.append(volume)
            prezzotot = prezzotot / volume  # questo sarebbe il prezzo unitario, non cambio variabile
            listaPrezziBudget.append(round(prezzotot, 2))
            qtaBudget = qtaBudget + volume
            print(str(volume) + "  " + str(round(prezzotot, 2)))
        print("TOTALE QUANTITA' TUTTI ARTICOLI => " + str(qtaBudget))

        # QUA CALCOLIAMO IL MIX
        for i in range(len(lista)):  # for per trovare il mix
            mixBudget.append(round(((listaQuantitaBudget[i] / qtaBudget) * 100), 3))
            print(str(round(mixBudget[i], 3)) + " %" + "  |  " + lista[i].nrArticolo)

        # QUA CALCOLIAMO IL RICAVO TOTALE
        ricavoBudget = 0.00
        for i in range(len(lista)):
            ricavoBudget = ricavoBudget + listaQuantitaBudget[i] * listaPrezziBudget[i]
        ricavoBudget = round(ricavoBudget,2)
        print(" RICAVI TOTALI: " + " a " + tipo + "  =>  " + str(round(ricavoBudget, 2)))

        print()
        print()
        # PARTE A CONSUNTIVO: QUARTA COLONNA DI EXCEL
        qtaCons = 0  # qtaTOTALE RIGA J8 exe scostamenti
        for i in range(len(lista)):  # for con il distinct
            #
            qtasingola = 0
            prezzosingolo = 0.00
            prezzotot = 0.00
            volume = 0
            tipo = "Consuntivo"
            arttocheck = lista[i].nrArticolo
            #
            print("TABELLA RICAVI => " + tipo + " => " + arttocheck)
            artB = Vendita.query.filter_by(nrArticolo=arttocheck, tipo=tipo).all()
            for j in range(len(artB)):  # for con il group by
                qtasingola = qtasingola + artB[j].qta
                prezzosingolo = artB[j].importoVenditeVL
                prezzosingolo = conversioneValuta(prezzosingolo, artB[j].nrOrigine, tipo)
                prezzotot = prezzotot + prezzosingolo
            volume = qtasingola
            listaQuantitaCons.append(volume)
            prezzotot = prezzotot / volume  # questo sarebbe il prezzo unitario, non cambio variabile
            listaPrezziCons.append(round(prezzotot, 2))
            qtaCons = qtaCons + volume
            print(str(volume) + "  " + str(round(prezzotot, 2)))
        print("TOTALE QUANTITA' TUTTI ARTICOLI => " + str(qtaCons))

        # QUA CALCOLIAMO IL MIX
        for i in range(len(lista)):  # for per trovare il mix
            mixCons.append(round(((listaQuantitaCons[i] / qtaCons) * 100), 2))
            print(str(round(mixCons[i], 3)) + " %" + "  |  " + lista[i].nrArticolo)

        # QUA CALCOLIAMO IL RICAVO TOTALE CONSUNTIVO
        ricavoCons = 0.00
        for i in range(len(lista)):
            ricavoCons = ricavoCons + listaQuantitaCons[i] * listaPrezziCons[i]
        ricavoCons = round(ricavoCons, 2)
        print(" RICAVI TOTALI: " + " a " + tipo + "  =>  " + str(round(ricavoCons, 2)))

        # MIX STANDARD!!!
        qtaTotStandard = qtaCons
        for i in range(len(lista)):
            listaQuantitaMixStd.append(round(((qtaTotStandard * mixBudget[i]) / 100)))
            print(str(round(listaQuantitaMixStd[i])))
        ricaviMixStd = 0.00
        for i in range(len(lista)):
            ricaviMixStd = ricaviMixStd + listaQuantitaMixStd[i] * listaPrezziBudget[i]
        ricaviMixStd = round(ricaviMixStd, 2)
        print(" RICAVI TOTALI MIX STANDARD => " + str(round(ricaviMixStd, 2)))

        # MIX EFFETTIVO!!!
        qtatotEffettiva = qtaCons
        for i in range(len(lista)):
            mixMixEffettivo.append(round(((listaQuantitaCons[i] / qtatotEffettiva) * 100), 3))
            print(str(round(mixMixEffettivo[i], 3)) + " %" + "  |  " + lista[i].nrArticolo)
        ricaviMixEffettivo = 0.00
        for i in range(len(lista)):
            ricaviMixEffettivo = ricaviMixEffettivo + listaQuantitaCons[i] * listaPrezziBudget[i]
        ricaviMixEffettivo = round(ricaviMixEffettivo, 2)
        print(" RICAVI TOTALI MIX EFFETTIVO => " + str(round(ricaviMixEffettivo)))
        print()
        print(" TABELLA RICAVI ")
        print(" ricavi budget => " + str(round(ricavoBudget)) + "  |  " + " ricavi mix std => " + str(
            round(ricaviMixStd)) + "  |  " + " ricavi mix effettivo => " + str(
            round(ricaviMixEffettivo)) + "  |  " + " ricavi consuntivo => " + str(round(ricavoCons)))
        print()
        print()

        # PARTE DA SISTEMARE
        # COSTI VARIABILI --- PARTE BUDGET
        for i in range(len(lista)):  # for con il distinct
            tipo = "BUDGET"
            arttocheck = lista[i].nrArticolo
            # cerco tutti i consumi dell'articolo che sto controllando => MATERIE PRIME
            # mi serve il totale di quantità prodotte per il determinato articolo
            qtaProd = 0  # qtaprodotta BUDGET
            artCC = Impiego.query.filter_by(tipo=tipo, nrArticolo=arttocheck).all()  # lista
            artCCC = []  # lista vuota di impieghi
            ODPPrecedente = ' '  # flag per fare il distinct
            for j in range(len(artCC)):
                if artCC[j].nrODP != ODPPrecedente:
                    if artCC[j].qtaOutput != 0:
                        qtaProd = qtaProd + artCC[j].qtaOutput
                        artCCC.append(artCC[j])
                        ODPPrecedente = artCC[j].nrODP
            print(artCCC)
            print(str(qtaProd) + " quantità prodotta per => " + arttocheck)
            artC = Consumo.query.filter_by(tipo=tipo, nrArticolo=arttocheck).all()
            costoUnitarioSomma = 0.00
            for j in range(
                    len(artC)):  # TROVIAMO IL COSTO UNITARIO PER PRODOTTO DELLE MP facendo costo totale / quantita
                if qtaProd != 0:
                    costoUnitarioSomma = costoUnitarioSomma + artC[j].importoTotaleC
            if qtaProd == 0:
                qtaProd = 1
            costoUnitarioSomma = costoUnitarioSomma / qtaProd
            listaCostiUnitariMPBudget.append(round(costoUnitarioSomma, 2))

            # cerco gli impieghi dell'articolo => LAVORAZIONE
            costoOrarioSommaUnita = 0
            artCC = Impiego.query.filter_by(tipo=tipo, nrArticolo=arttocheck).all()
            for j in range(len(artCC)):  # TROVIAMO COSTO UNITARIO DELLA LAVORAZIONE
                areaProdToCheck = artCC[j].areaProd
                risToCheck = artCC[j].risorsa
                # facciamo l'accesso alla tabella risorsa per la singola riga
                risorsaUsata = Risorsa.query.filter_by(codRisorsa=risToCheck, areaProd=areaProdToCheck).first()
                # siccome siamo a budget piglio la colonna euro a budget
                euroAllOra = risorsaUsata.costoOrarioBudget
                if artCC[j].qtaOutput != 0:
                    costoOrarioSommaUnita = costoOrarioSommaUnita + ((euroAllOra * artCC[j].tempoRisorsa))
            costoOrarioSommaUnita = costoOrarioSommaUnita / qtaProd
            print(costoOrarioSommaUnita)
            listaCostiUnitariLAVBudget.append(round(costoOrarioSommaUnita, 2))
            listaCostiUnitariBudget.append(listaCostiUnitariLAVBudget[i] + listaCostiUnitariMPBudget[i])
            print(arttocheck + "  |  " + "costo unitario MP => " + str(
                round(listaCostiUnitariMPBudget[i], 2)) + "  |  " + " costo unitario LAV =>" + str(
                round(listaCostiUnitariLAVBudget[i], 2)) + "  ==> COSTO UNITARIO PRODOTTO: " + str(
                round(listaCostiUnitariBudget[i], 2)) + "  |  qta prodotta => " + str(
                qtaProd) + "  |  qta venduta => " + str(listaQuantitaBudget[i]))

        print()
        print()

        # RICORDARSI DI DIVIDERE PER QUANTITA PRODOTTA PURE QUA
        # COSTI VARIABILI --- PARTE CONSUNTIVO
        for i in range(len(lista)):  # for con il distinct
            tipo = "CONSUNTIVO"
            arttocheck = lista[i].nrArticolo
            qtaProd = 0  # qtaprodotta BUDGET
            # cerco tutti i consumi dell'articolo che sto controllando => MATERIE PRIME
            artCC = Impiego.query.filter_by(tipo=tipo, nrArticolo=arttocheck).all()
            ODPPrecedente = ' '  # flag per fare il distinct
            for j in range(len(artCC)):
                if artCC[j].nrODP != ODPPrecedente:
                    if artCC[j].qtaOutput != 0:
                        qtaProd = qtaProd + artCC[j].qtaOutput
                        ODPPrecedente = artCC[j].nrODP
            print(str(qtaProd) + " quantità prodotta per => " + arttocheck)
            artC = Consumo.query.filter_by(tipo=tipo, nrArticolo=arttocheck).all()
            costoUnitarioSomma = 0.00
            for j in range(
                    len(artC)):  # TROVIAMO IL COSTO UNITARIO PER PRODOTTO DELLE MP facendo costo totale / quantita
                if qtaProd != 0:
                    costoUnitarioSomma = costoUnitarioSomma + artC[j].importoTotaleC
            if qtaProd == 0:
                qtaProd = 1
            costoUnitarioSomma = costoUnitarioSomma / qtaProd
            listaCostiUnitariMPCons.append(round(costoUnitarioSomma, 2))

            # cerco gli impieghi dell'articolo => LAVORAZIONE
            costoOrarioSommaUnita = 0
            artCC = Impiego.query.filter_by(tipo=tipo, nrArticolo=arttocheck).all()
            for j in range(len(artCC)):  # TROVIAMO COSTO UNITARIO DELLA LAVORAZIONE
                areaProdToCheck = artCC[j].areaProd
                risToCheck = artCC[j].risorsa
                # facciamo l'accesso alla tabella risorsa per la singola riga
                risorsaUsata = Risorsa.query.filter_by(codRisorsa=risToCheck, areaProd=areaProdToCheck).first()
                # siccome siamo a consuntivo piglio la colonna euro a consuntivo
                euroAllOra = risorsaUsata.costoOrarioConsuntivo
                if artCC[j].qtaOutput != 0:
                    costoOrarioSommaUnita = costoOrarioSommaUnita + ((euroAllOra * artCC[j].tempoRisorsa))
            costoOrarioSommaUnita = costoOrarioSommaUnita / qtaProd
            print(costoOrarioSommaUnita)
            listaCostiUnitariLAVCons.append(round(costoOrarioSommaUnita, 2))
            listaCostiUnitariCons.append(listaCostiUnitariLAVCons[i] + listaCostiUnitariMPCons[i])
            print(arttocheck + "  |  " + "costo unitario MP => " + str(
                round(listaCostiUnitariMPCons[i], 2)) + "  |  " + " costo unitario LAV =>" + str(
                round(listaCostiUnitariLAVCons[i], 2)) + "  ==> COSTO UNITARIO PRODOTTO: " + str(
                round(listaCostiUnitariCons[i], 2)) + "  |  qta prodotta => " + str(
                qtaProd) + "  |  qta venduta => " + str(listaQuantitaCons[i]))

        # CVTot = costi variabili totali!!! => qta * costo unitario
        cvTotBudget = 0.00
        cvTotMixStd = 0.00
        cvTotMixEffettivo = 0.00
        cvTotConsuntivo = 0.00
        for i in range(len(lista)):
            cvTotBudget = cvTotBudget + listaQuantitaBudget[i] * listaCostiUnitariBudget[i]
            cvTotMixStd = cvTotMixStd + listaQuantitaMixStd[i] * listaCostiUnitariBudget[i]
            cvTotMixEffettivo = cvTotMixEffettivo + listaQuantitaCons[i] * listaCostiUnitariBudget[i]
            cvTotConsuntivo = cvTotConsuntivo + listaQuantitaCons[i] * listaCostiUnitariCons[i]
        # calcolo => MOL
        molBudget = ricavoBudget - cvTotBudget
        molMixStd = ricaviMixStd - cvTotMixStd
        molMixEff = ricaviMixEffettivo - cvTotMixEffettivo
        molCons = ricavoCons - cvTotConsuntivo
        # calcolo scostamenti ricavi
        sRBudgetMixStd = ricaviMixStd - ricavoBudget
        sRMixStdMixEff = ricaviMixEffettivo - ricaviMixStd
        sRMixEffCons = ricavoCons - ricaviMixEffettivo
        # calcolo scostamenti costi
        sCBudgetMixStd = cvTotMixStd - cvTotBudget
        sCMixStdMixEff = cvTotMixEffettivo - cvTotMixStd
        scMixEffCons = cvTotConsuntivo - cvTotMixEffettivo
        # calcolo scostamenti MOL
        sBudgetMixStd = molMixStd - molBudget
        sMixStdMixEff = molMixEff - molMixStd
        sMixEffCons = molCons - molMixEff
        print()
        print(" -------------------BUDGET -------------------------")
        print(" RICAVI TOTALI => " + str(round(ricavoBudget)))
        print(" COSTI VARIABILI TOTALI  ==> " + str(round(cvTotBudget)))
        print(" MARGINE OPERATIVO LORDO ==> " + str(round(molBudget)))
        print(" -----------------------------------------------------------")
        print(" SCOSTAMENTI TRA BUDGET / MIXSTD (R/C/MOL) ==> " + str(round(sRBudgetMixStd)) + " | " + str(
            round(sCBudgetMixStd)) + " | " + str(round(sBudgetMixStd)))
        print(" -----------------------------------------------------------")

        print()
        print(" ------------------- MIX STD -------------------------")
        print(" RICAVI TOTALI  => " + str(round(ricaviMixStd)))
        print(" COSTI VARIABILI TOTALI  ==> " + str(round(cvTotMixStd)))
        print(" MARGINE OPERATIVO LORDO ==> " + str(round(molMixStd)))
        print(" -----------------------------------------------------------")
        print(" SCOSTAMENTI TRA MIX STD / MIX EFF (R/C/MOL) ==> " + str(round(sRMixStdMixEff)) + " | " + str(
            round(sCMixStdMixEff)) + " | " + str(round(sMixStdMixEff)))
        print(" -----------------------------------------------------------")

        print()
        print(" ------------------- MIX EFF -------------------------")
        print(" RICAVI TOTALI  => " + str(round(ricaviMixEffettivo)))
        print(" COSTI VARIABILI TOTALI  ==> " + str(round(cvTotMixEffettivo)))
        print(" MARGINE OPERATIVO LORDO ==> " + str(round(molMixEff)))
        print(" -----------------------------------------------------------")
        print(" SCOSTAMENTI TRA MIX EFF / CONSUNTIVO (R/C/MOL) ==> " + str(round(sRMixEffCons)) + " | " + str(
            round(scMixEffCons)) + " | " + str(round(sMixEffCons)))
        print(" -----------------------------------------------------------")

        print()
        print(" ------------------- CONSUNTIVO -------------------------")
        print(" RICAVI TOTALI  => " + str(round(ricavoCons)))
        print(" COSTI VARIABILI TOTALI  ==> " + str(round(cvTotConsuntivo)))
        print(" MARGINE OPERATIVO LORDO ==> " + str(round(molCons)))
        print(" -----------------------------------------------------------")
        #riempimento totali per il print
        listaTotali.append(qtaBudget)
        listaTotali.append(qtaCons)
        listaTotali.append(qtaCons)
        listaTotali.append(qtaCons)
        listaTotali.append(round(ricavoBudget,2))
        listaTotali.append(round(ricaviMixStd,2))
        listaTotali.append(round(ricaviMixEffettivo,2))
        listaTotali.append(round(ricavoCons,2))
        listaTotali.append(round(cvTotBudget,2))
        listaTotali.append(round(cvTotMixStd,2))
        listaTotali.append(round(cvTotMixEffettivo,2))
        listaTotali.append(round(cvTotConsuntivo,2))
        listaTotali.append(round(molBudget,2))
        listaTotali.append(round(molMixStd,2))
        listaTotali.append(round(molMixEff,2))
        listaTotali.append(round(molCons,2))
    return render_template("scostamenti.html", qtaB = listaTotali[0], qtaMS = listaTotali[1], qtaME = listaTotali[2], qtaC = listaTotali[3], rB = listaTotali[4], rMS = listaTotali[5], rME = listaTotali[6], rC = listaTotali[7], cB = listaTotali[8], cMS = listaTotali[9], cME = listaTotali[10], cC = listaTotali[11], mB = listaTotali[12], mMS = listaTotali[13], mME = listaTotali[14], mC = listaTotali[15])


@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@views.route('/db')
def riempi():
    # TO DO
    # 1. Svuotare tabella
    # 2. Inserimento di massa

    print(" procedura riempimento database: ")

    print("---------------------------CLIENTE----------------------------------")
    # leggo "Clienti" e riempio la tabella del database "Cliente"
    df = pd.read_excel('inputXLSX/clienti.xlsx', index_col=0)
    # righe del xls
    print(" | " + str(len(df)) + " | " + " entries trovate per la tabella CLIENTE ")
    records = []
    for i in range(len(df)):
        codiceCliente = df.iloc[i, 0]
        fattureCumulative = df.iloc[i, 1]
        valutaCliente = int(df.iloc[i, 2])
        records.append(Cliente(codiceCliente=codiceCliente, fattureCumulative=fattureCumulative,
                                valutaCliente=valutaCliente))
        
    db.session.add_all(records)
    db.session.commit()
    print(" ----------> TABELLA RIEMPITA <-------------")
    print(" ")

    print("---------------------------VALUTA----------------------------------")
    # leggo "tassiDiCambio" e riempio la tabella del database "Valuta"
    df = pd.read_excel('inputXLSX/tassiDiCambio.xlsx', index_col=0)
    print(" | " + str(len(df)) + " | " + " entries trovate per la tabella VALUTA ")
    for i in range(len(df)):
        codValuta = int(df.iloc[i, 0])
        budOCons = df.iloc[i, 1]
        tassoCambioMedio = str(df.iloc[i, 2])
        tassoCambioMedio = tassoCambioMedio.replace(",",".")
        tassoCambioMedio = float(tassoCambioMedio)
        newValuta = Valuta(codValuta=codValuta, budOCons=budOCons, tassoCambioMedio=tassoCambioMedio)
        db.session.add(newValuta)
        db.session.commit()
    print(" ----------> TABELLA RIEMPITA <-------------")
    print(" ")

    print("---------------------------VENDITA----------------------------------")
    # leggo "Vendite" e riempio la tabella del database "Vendita"
    df = pd.read_excel('inputXLSX/Vendite.xlsx', index_col=0)
    print(" | " + str(len(df)) + " | " + " entries trovate per la tabella VENDITE ")
    for i in range(len(df)):
        nrMovimentoV = int(df.iloc[i, 0])
        tipo = df.iloc[i, 1]
        nrArticolo = df.iloc[i, 2]
        nrOrigine = df.iloc[i, 3]
        qta = int(df.iloc[i, 4])
        importoVenditeVL = str(df.iloc[i, 5])
        importoVenditeVL = importoVenditeVL.replace(",",".")
        importoVenditeVL = float(importoVenditeVL)
        newVendita = Vendita(nrMovimentoV=nrMovimentoV, tipo=tipo, nrArticolo=nrArticolo,
                                nrOrigine=nrOrigine,
                                qta=qta, importoVenditeVL=importoVenditeVL)
        db.session.add(newVendita)
        db.session.commit()
    print(" ----------> TABELLA RIEMPITA <-------------")
    print(" ")

    print("---------------------------CONSUMO----------------------------------")
    # leggo "Consumi" e riempio la tabella del database "Consumo"
    df = pd.read_excel('inputXLSX/Consumi.xlsx', index_col=0)
    print(" | " + str(len(df)) + " | " + " entries trovate per la tabella CONSUMO ")
    for i in range(len(df)):
        nrMovimentoC = int(df.iloc[i, 0])
        tipo = df.iloc[i, 1]
        codiceMP = df.iloc[i, 2]
        nrArticolo = df.iloc[i, 3]
        nrDocumentoODP = df.iloc[i, 4]
        qta = int(df.iloc[i, 5])
        importoTotaleC = str(df.iloc[i, 6])
        importoTotaleC = importoTotaleC.replace(",",".")
        importoTotaleC = float(importoTotaleC)
        newConsumo = Consumo(nrMovimentoC=nrMovimentoC, tipo=tipo, codiceMP=codiceMP, nrArticolo=nrArticolo,
                                nrDocumentoODP=nrDocumentoODP, qtaC=qta, importoTotaleC=importoTotaleC)
        db.session.add(newConsumo)
        db.session.commit()
    print(" ----------> TABELLA RIEMPITA <-------------")
    print(" ")

    print("---------------------------IMPIEGO----------------------------------")
    # leggo "impiegoOrarioRisorse" e riempio la tabella del database "Impiego"
    df = pd.read_excel('inputXLSX/impiegoOrarioRisorse.xlsx', index_col=0)
    print(" | " + str(len(df)) + " | " + " entries trovate per la tabella IMPIEGO ")
    for i in range(len(df)):
        idImpiego = i
        nrArticolo = df.iloc[i, 0]
        tipo = df.iloc[i, 1]
        nrODP = df.iloc[i, 2]
        descrizione = df.iloc[i, 3]
        areaProd = df.iloc[i, 4]
        risorsa = df.iloc[i, 5]
        tempoRisorsa = str(df.iloc[i, 6])
        tempoRisorsa = tempoRisorsa.replace(",", ".")
        tempoRisorsa = float(tempoRisorsa)
        qtaOutput = int(df.iloc[i, 7])
        newImpiego = Impiego(idImpiego=idImpiego, nrArticolo=nrArticolo, tipo=tipo, nrODP=nrODP, descrizione=descrizione,
                                areaProd=areaProd, risorsa=risorsa, tempoRisorsa=tempoRisorsa,
                                qtaOutput=qtaOutput)
        db.session.add(newImpiego)
        db.session.commit()
    print(" ----------> TABELLA RIEMPITA <-------------")
    print(" ")

    print("---------------------------RISORSA----------------------------------")
    # leggo "Risorse" e riempio la tabella del database "Risorsa"
    df = pd.read_excel('inputXLSX/costoOrario.xlsx', index_col=0)
    print(" | " + str(len(df)) + " | " + " entries trovate per la tabella RISORSA ")
    for i in range(len(df)):
        idRisorsa = i
        codRisorsa = df.iloc[i, 0]
        areaProd = df.iloc[i, 1]
        costoOrarioBudget = str(df.iloc[i, 2])
        costoOrarioBudget = costoOrarioBudget.replace(",", ".")
        costoOrarioBudget = float(costoOrarioBudget)
        costoOrarioConsuntivo = str(df.iloc[i, 3])
        costoOrarioConsuntivo = costoOrarioConsuntivo.replace(",", ".")
        costoOrarioConsuntivo = float(costoOrarioConsuntivo)
        newRisorsa = Risorsa(idRisorsa=idRisorsa, codRisorsa=codRisorsa, areaProd=areaProd, costoOrarioBudget=costoOrarioBudget,
                                costoOrarioConsuntivo=costoOrarioConsuntivo)
        db.session.add(newRisorsa)
        db.session.commit()
    print(" ----------> TABELLA RIEMPITA <-------------")
    print(" ")
    return

@views.route('/specificaArticolo',  methods = ['GET', 'POST'])
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

@views.route('/chiSiamo')
def chiSiamo():
    return render_template("chiSiamo.html")

@views.route('/modifica')
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


