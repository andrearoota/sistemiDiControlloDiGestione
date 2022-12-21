from pandas import pandas
from src.model.model import Client, Sales, Consumption, Impiego, Risorsa, Currency, Article
from src.controller.article import selectAllArticlesID, analysisVariancesCostCenterByArticle, analysisVariancesRevenueCenterByArticle, countSales
from src.controller.analysisVariances import calcanalysisVariances
from src import db
import json

__FILES_DIRECTORY__ = "storage/"

def importFromXLSX():
    '''
    Import into databases from file XLSX.

        Parameters:
            None
        Returns:
            JSON
    '''

    # Drop all tables and recreate the schema
    db.drop_all()
    db.create_all()
    db.session.commit()

    # Insert Client
    # Read from file .xlsx and insert into database
    df = pandas.read_excel(f"{__FILES_DIRECTORY__}clienti.xlsx")
    records = []
    for i in range(len(df)):
        clientCode = df.iloc[i, 0]
        cumulativeInvoices = df.iloc[i, 2]
        currency = int(df.iloc[i, 3])
        records.append(Client(clientCode=clientCode, cumulativeInvoices=cumulativeInvoices,
                                currency=currency))
        
    db.session.add_all(records)
    db.session.commit()

    # Insert Currency
    # Read from file .xlsx and insert into database
    df = pandas.read_excel(f"{__FILES_DIRECTORY__}tassi Di Cambio.xlsx")
    records = []
    for i in range(len(df)):
        currencyCode = int(df.iloc[i, 0])
        budOrCons = df.iloc[i, 1].upper()
        exchangeRate = str(df.iloc[i, 2])
        exchangeRate = exchangeRate.replace(",",".")
        exchangeRate = float(exchangeRate)
        records.append(Currency(currencyCode=currencyCode, budOrCons=budOrCons, exchangeRate=exchangeRate))

    db.session.add_all(records)
    db.session.commit()

    # Insert Sales
    # Read from file .xlsx and insert into database
    df = pandas.read_excel(f"{__FILES_DIRECTORY__}Vendite.xlsx")
    records = []
    for i in range(len(df)):
        movementNumberS = int(df.iloc[i, 0])
        budOrCons = df.iloc[i, 1].upper()
        articleNumber = df.iloc[i, 3]
        originNumber = df.iloc[i, 5]
        quantityS = int(df.iloc[i, 6])
        salesAmount = str(df.iloc[i, 7])
        salesAmount = salesAmount.replace(",",".")
        salesAmount = float(salesAmount)
        records.append(Sales(movementNumberS=movementNumberS, budOrCons=budOrCons, articleNumber=articleNumber,
                                originNumber=originNumber,
                                quantityS=quantityS, salesAmount=salesAmount))

    db.session.add_all(records)
    db.session.commit()

    # Insert Consumption
    # Read from file .xlsx and insert into database
    df = pandas.read_excel(f"{__FILES_DIRECTORY__}Consumi.xlsx")
    records = []
    for i in range(len(df)):
        movementNumberC = int(df.iloc[i, 0])
        budOrCons = df.iloc[i, 1].upper()
        rawMaterialCode = df.iloc[i, 3]
        articleNumber = df.iloc[i, 5]
        nrDocumentoODP = df.iloc[i, 6]
        quantityC = str(df.iloc[i, 7])
        quantityC = quantityC.replace(",", ".")
        quantityC = float(quantityC)

        totalAmountC = str(df.iloc[i, 8])
        totalAmountC = totalAmountC.replace(",",".")
        totalAmountC = float(totalAmountC)
        records.append(Consumption(movementNumberC=movementNumberC, budOrCons=budOrCons, rawMaterialCode=rawMaterialCode, articleNumber=articleNumber,
                                nrDocumentoODP=nrDocumentoODP, quantityC=quantityC, totalAmountC=totalAmountC))

    db.session.add_all(records)
    db.session.commit()

    # Insert Impiego
    # Read from file .xlsx and insert into database
    df = pandas.read_excel(f"{__FILES_DIRECTORY__}impiego Orario Risorse.xlsx")
    records = []
    for i in range(len(df)):
        idImpiego = i
        articleNumber = df.iloc[i, 0]
        budOrCons = df.iloc[i, 1].upper()
        nrODP = df.iloc[i, 2]
        descrizione = df.iloc[i, 3]
        areaProd = df.iloc[i, 4]
        risorsa = df.iloc[i, 5]
        tempoRisorsa = str(df.iloc[i, 6])
        tempoRisorsa = tempoRisorsa.replace(",", ".")
        tempoRisorsa = float(tempoRisorsa)
        qtaOutput = str(df.iloc[i, 7])
        qtaOutput = qtaOutput.replace(",", ".")
        qtaOutput = float(qtaOutput)
        records.append(Impiego(idImpiego=idImpiego, articleNumber=articleNumber, budOrCons=budOrCons, nrODP=nrODP, descrizione=descrizione,
                                areaProd=areaProd, risorsa=risorsa, tempoRisorsa=tempoRisorsa,
                                qtaOutput=qtaOutput))

    db.session.add_all(records)
    db.session.commit()

    # Insert Risorse
    # Read from file .xlsx and insert into database
    df = pandas.read_excel(f"{__FILES_DIRECTORY__}costo orario risorse - budget.xlsx")
    records = []
    for i in range(len(df)):
        codRisorsa = df.iloc[i, 0]
        areaProd = df.iloc[i, 1]
        costoOrarioBudget = str(df.iloc[i, 2])
        costoOrarioBudget = costoOrarioBudget.replace(",", ".")
        costoOrarioBudget = float(costoOrarioBudget)
        records.append(Risorsa(codRisorsa=codRisorsa, areaProd=areaProd, costoOrarioBudget=costoOrarioBudget))

    df = pandas.read_excel(f"{__FILES_DIRECTORY__}costo orario risorse - consuntivo.xlsx")
    for i in range(len(df)):
        codRisorsa = df.iloc[i, 0]
        areaProd = df.iloc[i, 1]
        for j in range(len(records)):
            if records[i].areaProd == areaProd and records[i].codRisorsa == codRisorsa:
                costoOrarioConsuntivo = str(df.iloc[i, 2])
                costoOrarioConsuntivo = costoOrarioConsuntivo.replace(",", ".")
                records[i].costoOrarioConsuntivo = float(costoOrarioConsuntivo)
                break

    db.session.add_all(records)
    db.session.commit()

    # Insert Article and calc analysis variances
    # Get total for calculate "percentageOutput"
    totalSalesQuantity = countSales()
    records = []
    for article in selectAllArticlesID():

        records.append(Article(
            articleNumber = article.articleNumber,
            analysisVariancesCostCenter = json.dumps(analysisVariancesCostCenterByArticle(article.articleNumber, totalSalesQuantity)).replace('null', 'None'),
            analysisVariancesRevenueCenter = json.dumps(analysisVariancesRevenueCenterByArticle(article.articleNumber, totalSalesQuantity)).replace('null', 'None'),
        ))

    db.session.add_all(records)
    db.session.commit()

    # Calc analysis variances by market
    # Per ogni market faccio analisi scostamenti (Market)
    stmt = db.select(Currency).distinct()
    for market in db.session.execute(stmt): # Calcoli per ogni market
        # Trovo gli articoli venduti in un mercato
        stmt = (
            db.select(Sales.articleNumber.label("articleNumber")).distinct()
            .select_from(Sales)
            .join(Client, Sales.originNumber == Client.clientCode)
            .where(Client.currency == market.Currency.currencyCode)
        )

        # Faccio analisi scostamenti per mercato (Market)
        market.Currency.analysisVariances = json.dumps(calcanalysisVariances(db.session.execute(stmt), False, market.Currency.currencyCode)).replace('null', 'None')
        db.session.commit()

    # Calc analysis variances by client
    # Per ogni cliente faccio analisi scostamenti (Market > Client)
    for client in db.session.execute(db.select(Client)):
        stmt = (
            db.select(Sales.articleNumber.label("articleNumber")).distinct()
            .select_from(Sales)
            .join(Client, Sales.originNumber == Client.clientCode)
            .where(Client.clientCode == client.Client.clientCode)
            .where(Client.currency == client.Client.currency)
        )
        articles = db.session.execute(stmt)

        tempData = {"id": client.Client.clientCode, "analysisVariances": calcanalysisVariances(articles, False, client.Client.currency, client.Client.clientCode), "article": []}

        # Per ogni prodotto faccio analisi scostamenti (Market > Client > Article)
        for item in db.session.execute(stmt):
            tempData["article"].append({"id": item.articleNumber, "analysisVariances": calcanalysisVariances([item], False, client.Client.currency, client.Client.clientCode)})
        
        client.Client.analysisVariances = json.dumps(tempData).replace('null', 'None')
        db.session.commit()

    return "true"