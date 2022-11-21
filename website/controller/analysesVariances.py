from website import db
from website.model.model import Vendita, Consumo, Impiego, Risorsa
from website.controller.currency import currencyConversion
from flask import render_template


def calcAnalysesVariances():

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

    print(db.session)
    llista = []
    lista = db.session.query(Vendita.nrArticolo).distinct().all()
    for i in range(len(lista)):
        llista.append(lista[i])
        print(lista)
        print(llista)
        print(" quanti articoli ho: " + str(len(lista)))
        
        tipo = "BUDGET"

        if len(listaTotali) < 1:
            qtaBudget = 0  # qtaTOTALE RIGA D8 exe scostamenti
            for i in range(len(lista)):  # for con il distinct
                #
                qtasingola = 0
                prezzosingolo = 0.00
                prezzotot = 0.00
                volume = 0
                arttocheck = lista[i].nrArticolo
                #
                print("TABELLA RICAVI => " + tipo + " => " + arttocheck)
                artB = Vendita.query.filter_by(
                    nrArticolo=arttocheck, tipo=tipo).all()
                for j in range(len(artB)):  # for con il group by
                    qtasingola = qtasingola + artB[j].qta
                    prezzosingolo = artB[j].importoVenditeVL
                    prezzosingolo = currencyConversion(
                        prezzosingolo, artB[j].nrOrigine, tipo)
                    prezzotot = prezzotot + prezzosingolo
                volume = qtasingola
                listaQuantitaBudget.append(volume)
                # questo sarebbe il prezzo unitario, non cambio variabile
                prezzotot = prezzotot / volume
                listaPrezziBudget.append(round(prezzotot, 2))
                qtaBudget = qtaBudget + volume
                print(str(volume) + "  " + str(round(prezzotot, 2)))
            print("TOTALE QUANTITA' TUTTI ARTICOLI => " + str(qtaBudget))

            # QUA CALCOLIAMO IL MIX
            for i in range(len(lista)):  # for per trovare il mix
                mixBudget.append(
                    round(((listaQuantitaBudget[i] / qtaBudget) * 100), 3))
                print(str(round(mixBudget[i], 3)) +
                    " %" + "  |  " + lista[i].nrArticolo)

            # QUA CALCOLIAMO IL RICAVO TOTALE
            ricavoBudget = 0.00
            for i in range(len(lista)):
                ricavoBudget = ricavoBudget + \
                    listaQuantitaBudget[i] * listaPrezziBudget[i]
            ricavoBudget = round(ricavoBudget, 2)
            print(" RICAVI TOTALI: " + " a " + tipo +
                "  =>  " + str(round(ricavoBudget, 2)))

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
                artB = Vendita.query.filter_by(
                    nrArticolo=arttocheck, tipo=tipo).all()
                for j in range(len(artB)):  # for con il group by
                    qtasingola = qtasingola + artB[j].qta
                    prezzosingolo = artB[j].importoVenditeVL
                    prezzosingolo = currencyConversion(
                        prezzosingolo, artB[j].nrOrigine, tipo)
                    prezzotot = prezzotot + prezzosingolo
                volume = qtasingola
                listaQuantitaCons.append(volume)
                # questo sarebbe il prezzo unitario, non cambio variabile
                prezzotot = prezzotot / volume
                listaPrezziCons.append(round(prezzotot, 2))
                qtaCons = qtaCons + volume
                print(str(volume) + "  " + str(round(prezzotot, 2)))
            print("TOTALE QUANTITA' TUTTI ARTICOLI => " + str(qtaCons))

            # QUA CALCOLIAMO IL MIX
            for i in range(len(lista)):  # for per trovare il mix
                mixCons.append(round(((listaQuantitaCons[i] / qtaCons) * 100), 2))
                print(str(round(mixCons[i], 3)) + " %" +
                    "  |  " + lista[i].nrArticolo)

            # QUA CALCOLIAMO IL RICAVO TOTALE CONSUNTIVO
            ricavoCons = 0.00
            for i in range(len(lista)):
                ricavoCons = ricavoCons + listaQuantitaCons[i] * listaPrezziCons[i]
            ricavoCons = round(ricavoCons, 2)
            print(" RICAVI TOTALI: " + " a " + tipo +
                "  =>  " + str(round(ricavoCons, 2)))

            # MIX STANDARD!!!
            qtaTotStandard = qtaCons
            for i in range(len(lista)):
                listaQuantitaMixStd.append(
                    round(((qtaTotStandard * mixBudget[i]) / 100)))
                print(str(round(listaQuantitaMixStd[i])))
            ricaviMixStd = 0.00
            for i in range(len(lista)):
                ricaviMixStd = ricaviMixStd + \
                    listaQuantitaMixStd[i] * listaPrezziBudget[i]
            ricaviMixStd = round(ricaviMixStd, 2)
            print(" RICAVI TOTALI MIX STANDARD => " + str(round(ricaviMixStd, 2)))

            # MIX EFFETTIVO!!!
            qtatotEffettiva = qtaCons
            for i in range(len(lista)):
                mixMixEffettivo.append(
                    round(((listaQuantitaCons[i] / qtatotEffettiva) * 100), 3))
                print(str(round(mixMixEffettivo[i], 3)) +
                    " %" + "  |  " + lista[i].nrArticolo)
            ricaviMixEffettivo = 0.00
            for i in range(len(lista)):
                ricaviMixEffettivo = ricaviMixEffettivo + \
                    listaQuantitaCons[i] * listaPrezziBudget[i]
            ricaviMixEffettivo = round(ricaviMixEffettivo, 2)
            print(" RICAVI TOTALI MIX EFFETTIVO => " +
                str(round(ricaviMixEffettivo)))
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
                artCC = Impiego.query.filter_by(
                    tipo=tipo, nrArticolo=arttocheck).all()  # lista
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
                artC = Consumo.query.filter_by(
                    tipo=tipo, nrArticolo=arttocheck).all()
                costoUnitarioSomma = 0.00
                for j in range(
                        len(artC)):  # TROVIAMO IL COSTO UNITARIO PER PRODOTTO DELLE MP facendo costo totale / quantita
                    if qtaProd != 0:
                        costoUnitarioSomma = costoUnitarioSomma + \
                            artC[j].importoTotaleC
                if qtaProd == 0:
                    qtaProd = 1
                costoUnitarioSomma = costoUnitarioSomma / qtaProd
                listaCostiUnitariMPBudget.append(round(costoUnitarioSomma, 2))

                # cerco gli impieghi dell'articolo => LAVORAZIONE
                costoOrarioSommaUnita = 0
                artCC = Impiego.query.filter_by(
                    tipo=tipo, nrArticolo=arttocheck).all()
                for j in range(len(artCC)):  # TROVIAMO COSTO UNITARIO DELLA LAVORAZIONE
                    areaProdToCheck = artCC[j].areaProd
                    risToCheck = artCC[j].risorsa
                    # facciamo l'accesso alla tabella risorsa per la singola riga
                    risorsaUsata = Risorsa.query.filter_by(
                        codRisorsa=risToCheck, areaProd=areaProdToCheck).first()
                    # siccome siamo a budget piglio la colonna euro a budget
                    euroAllOra = risorsaUsata.costoOrarioBudget
                    if artCC[j].qtaOutput != 0:
                        costoOrarioSommaUnita = costoOrarioSommaUnita + \
                            ((euroAllOra * artCC[j].tempoRisorsa))
                costoOrarioSommaUnita = costoOrarioSommaUnita / qtaProd
                print(costoOrarioSommaUnita)
                listaCostiUnitariLAVBudget.append(round(costoOrarioSommaUnita, 2))
                listaCostiUnitariBudget.append(
                    listaCostiUnitariLAVBudget[i] + listaCostiUnitariMPBudget[i])
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
                artCC = Impiego.query.filter_by(
                    tipo=tipo, nrArticolo=arttocheck).all()
                ODPPrecedente = ' '  # flag per fare il distinct
                for j in range(len(artCC)):
                    if artCC[j].nrODP != ODPPrecedente:
                        if artCC[j].qtaOutput != 0:
                            qtaProd = qtaProd + artCC[j].qtaOutput
                            ODPPrecedente = artCC[j].nrODP
                print(str(qtaProd) + " quantità prodotta per => " + arttocheck)
                artC = Consumo.query.filter_by(
                    tipo=tipo, nrArticolo=arttocheck).all()
                costoUnitarioSomma = 0.00
                for j in range(
                        len(artC)):  # TROVIAMO IL COSTO UNITARIO PER PRODOTTO DELLE MP facendo costo totale / quantita
                    if qtaProd != 0:
                        costoUnitarioSomma = costoUnitarioSomma + \
                            artC[j].importoTotaleC
                if qtaProd == 0:
                    qtaProd = 1
                costoUnitarioSomma = costoUnitarioSomma / qtaProd
                listaCostiUnitariMPCons.append(round(costoUnitarioSomma, 2))

                # cerco gli impieghi dell'articolo => LAVORAZIONE
                costoOrarioSommaUnita = 0
                artCC = Impiego.query.filter_by(
                    tipo=tipo, nrArticolo=arttocheck).all()
                for j in range(len(artCC)):  # TROVIAMO COSTO UNITARIO DELLA LAVORAZIONE
                    areaProdToCheck = artCC[j].areaProd
                    risToCheck = artCC[j].risorsa
                    # facciamo l'accesso alla tabella risorsa per la singola riga
                    risorsaUsata = Risorsa.query.filter_by(
                        codRisorsa=risToCheck, areaProd=areaProdToCheck).first()
                    # siccome siamo a consuntivo piglio la colonna euro a consuntivo
                    euroAllOra = risorsaUsata.costoOrarioConsuntivo
                    if artCC[j].qtaOutput != 0:
                        costoOrarioSommaUnita = costoOrarioSommaUnita + \
                            ((euroAllOra * artCC[j].tempoRisorsa))
                costoOrarioSommaUnita = costoOrarioSommaUnita / qtaProd
                print(costoOrarioSommaUnita)
                listaCostiUnitariLAVCons.append(round(costoOrarioSommaUnita, 2))
                listaCostiUnitariCons.append(
                    listaCostiUnitariLAVCons[i] + listaCostiUnitariMPCons[i])
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
                cvTotBudget = cvTotBudget + \
                    listaQuantitaBudget[i] * listaCostiUnitariBudget[i]
                cvTotMixStd = cvTotMixStd + \
                    listaQuantitaMixStd[i] * listaCostiUnitariBudget[i]
                cvTotMixEffettivo = cvTotMixEffettivo + \
                    listaQuantitaCons[i] * listaCostiUnitariBudget[i]
                cvTotConsuntivo = cvTotConsuntivo + \
                    listaQuantitaCons[i] * listaCostiUnitariCons[i]
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
            # riempimento totali per il print
            listaTotali.append(qtaBudget)
            listaTotali.append(qtaCons)
            listaTotali.append(qtaCons)
            listaTotali.append(qtaCons)
            listaTotali.append(round(ricavoBudget, 2))
            listaTotali.append(round(ricaviMixStd, 2))
            listaTotali.append(round(ricaviMixEffettivo, 2))
            listaTotali.append(round(ricavoCons, 2))
            listaTotali.append(round(cvTotBudget, 2))
            listaTotali.append(round(cvTotMixStd, 2))
            listaTotali.append(round(cvTotMixEffettivo, 2))
            listaTotali.append(round(cvTotConsuntivo, 2))
            listaTotali.append(round(molBudget, 2))
            listaTotali.append(round(molMixStd, 2))
            listaTotali.append(round(molMixEff, 2))
            listaTotali.append(round(molCons, 2))
        return render_template("analysesVariances.html", qtaB=listaTotali[0], qtaMS=listaTotali[1], qtaME = listaTotali[2], qtaC = listaTotali[3], rB = listaTotali[4], rMS = listaTotali[5], rME = listaTotali[6], rC = listaTotali[7], cB = listaTotali[8], cMS = listaTotali[9], cME = listaTotali[10], cC = listaTotali[11], mB = listaTotali[12], mMS = listaTotali[13], mME = listaTotali[14], mC = listaTotali[15])
