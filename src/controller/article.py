from src import db
from src.model.model import Vendita, Consumo, Impiego, Risorsa, Article, Cliente
from src.controller.currency import currencyConversion
from src.controller.sale import countSales
from flask import render_template
from sqlalchemy import and_
import copy
import ast


__BUDGET_CONSUNTIVO__ = ["BUDGET", "CONSUNTIVO"]

def selectAllArticlesID():
    '''
    Gets article ids from sales table.
    
        Parameters:
            None
        Returns:
            Array

    '''
    firstList = db.select((Vendita.nrArticolo.label("nrArticolo"))).distinct()
    secondList = db.select((Impiego.nrArticolo).label("nrArticolo")).distinct()

    stmt = db.union(firstList, secondList).order_by("nrArticolo")

    return db.session.execute(stmt)


def analysisVariancesRevenueCenterByArticle(idArticle, totalSalesQuantity, market = None, client = None):
    '''
    Get the analyses variances revenue center of article.
    
        Parameters:
            idArticle (string): di article to search
            totalSalesQuantity (dict): {BUDGET: (int), CONSUNTIVO: (int)} 
        Returns:
            (dict): {
                BUDGET: {unitPrice: (float),quantity: (float), percentageOutput: (float)},
                mixStandard: {unitPrice: (float),quantity: (float), percentageOutput: (float)},
                mixEffettivo: {unitPrice: (float),quantity: (float), percentageOutput: (float)},
                CONSUNTIVO: {unitPrice: (float),quantity: (float), percentageOutput: (float)}
            }
    '''

    # Analisi centro di ricavo: prezzo vendita unitario * volume totale di vendita * percentuale di output
    # Prezzo di vendita (unitPrice): prezzo di vendita del prodotto
    # Volume totale di vendita (quantity): volume totale dei beni venduti
    # Percentuale di output (percentageOutput): percentuale di output del prodotto

    # Definizione strutture base
    revenueCenter = {
        "unitPrice": 0,
        "quantity": 0,
        "percentageOutput": 0
    }

    analysisVariancesRevenueCenter = {
        "BUDGET": copy.deepcopy(revenueCenter),
        "mixStandard": copy.deepcopy(revenueCenter),
        "mixEffettivo": copy.deepcopy(revenueCenter),
        "CONSUNTIVO": copy.deepcopy(revenueCenter)
    }

    # Definizione condizioni aggiuntive
    additionalCondition = []
    if market != None:
        additionalCondition.append(Cliente.valutaCliente == market)
    if client != None:
        additionalCondition.append(Cliente.codiceCliente == client)

    for type in __BUDGET_CONSUNTIVO__:
        stmt = (
            db.select(Vendita)
            .join(Cliente)
            .where(Vendita.nrArticolo == idArticle)
            .where(Vendita.tipo == type)
            .filter(and_(*additionalCondition))
        )

        for sale in db.session.execute(stmt).scalars():
            analysisVariancesRevenueCenter[type]["unitPrice"] += currencyConversion(sale.importoVenditeVL, sale.nrOrigine, type)
            analysisVariancesRevenueCenter[type]["quantity"] += sale.qta

        # Prevent ZeroDivisionError: division by zero
        if analysisVariancesRevenueCenter[type]["quantity"] != 0:
            analysisVariancesRevenueCenter[type]["unitPrice"] /= analysisVariancesRevenueCenter[type]["quantity"] # Unit price
            analysisVariancesRevenueCenter[type]["percentageOutput"] = analysisVariancesRevenueCenter[type]["quantity"] / totalSalesQuantity[type] # Percentage output

        analysisVariancesRevenueCenter[type]["quantity"] = totalSalesQuantity[type] # Total sales volume

    # Mix data to calculate mix standard and mix effettivo 
    analysisVariancesRevenueCenter["mixStandard"]["unitPrice"] = analysisVariancesRevenueCenter["BUDGET"]["unitPrice"]
    analysisVariancesRevenueCenter["mixStandard"]["quantity"] = analysisVariancesRevenueCenter["CONSUNTIVO"]["quantity"]
    analysisVariancesRevenueCenter["mixStandard"]["percentageOutput"] = analysisVariancesRevenueCenter["BUDGET"]["percentageOutput"]
    
    analysisVariancesRevenueCenter["mixEffettivo"]["unitPrice"] = analysisVariancesRevenueCenter["BUDGET"]["unitPrice"]
    analysisVariancesRevenueCenter["mixEffettivo"]["quantity"] = analysisVariancesRevenueCenter["CONSUNTIVO"]["quantity"]
    analysisVariancesRevenueCenter["mixEffettivo"]["percentageOutput"] = analysisVariancesRevenueCenter["CONSUNTIVO"]["percentageOutput"]

    return analysisVariancesRevenueCenter


def analysisVariancesCostCenterByArticle(idArticle, totalSalesQuantity, market = None, client = None):
    '''
    Get the analyses variances cost center of article.
    
        Parameters:
            idArticle (string): di article to search
            totalSalesQuantity (dict): {BUDGET: (int), CONSUNTIVO: (int)} 
        Returns:
            (dict): {
                BUDGET: {unitPrice: (float),quantity: (float), percentageOutput: (float)},
                mixStandard: {unitPrice: (float),quantity: (float), percentageOutput: (float)},
                mixEffettivo: {unitPrice: (float),quantity: (float), percentageOutput: (float)},
                CONSUNTIVO: {unitPrice: (float),quantity: (float), percentageOutput: (float)}
            }
    '''

    # Analisi centro di costo: volume produttivo * ∑(impiego risorsa * costo risorsa)
    # Volume produttivo (unitPrice): prezzo di vendita del prodotto
    # Impiego risorsa (quantity): volume totale dei beni venduti
    # Costo risorsa (percentageOutput): percentuale di output del prodotto

    # Definizione strutture base
    costCenter = {
        "totalQuantity": 0,
        "queryQuantity": 0,
        "costs": {
            "costsVariable": 0,
            "costsRawMaterial": 0
        },
    }

    analysisVariancesCostCenter = {
        "BUDGET": None,
        "mixStandard": None,
        "mixEffettivo": None,
        "CONSUNTIVO": None
    }

    # Definizione condizioni aggiuntive
    additionalCondition = []
    if market != None:
        additionalCondition.append(Cliente.valutaCliente == market)
    if client != None:
        additionalCondition.append(Cliente.codiceCliente == client)


    for type in __BUDGET_CONSUNTIVO__:
        tempCostCenter = copy.deepcopy(costCenter)
        ### IMPORTANTE ASSUNZIONE ###
        # Considero l'azienda di tipo "Just in time", perciò utilizzo
        # il totale venduto come totale di produzione
        stmt = (
            db.select(
                db.func.sum(Vendita.qta).label("sumQta")
            )
            .where(Vendita.nrArticolo == idArticle)
            .where(Vendita.tipo == type)
        )
        tempCostCenter["totalQuantity"] = db.session.scalars(stmt).one()
        if tempCostCenter["totalQuantity"] == None or tempCostCenter["totalQuantity"] == 0:
            analysisVariancesCostCenter[type] = tempCostCenter
            continue # Inutile calcolare altro, non essendoci stata produzione data la precedente assunzione

        # Calcolo numero prodotti condizionati dai parametri richiesti
        stmt = (
            db.select(
                db.func.sum(Vendita.qta).label("sumQta")
            )
            .join(Cliente)
            .where(Vendita.nrArticolo == idArticle)
            .where(Vendita.tipo == type)
            .filter(and_(*additionalCondition))
        )
        qtaProduction = db.session.scalars(stmt).one()
        if qtaProduction == None or qtaProduction == 0:
            analysisVariancesCostCenter[type] = tempCostCenter
            continue # Inutile calcolare altro, non essendoci stata produzione data la precedente assunzione

        tempCostCenter["queryQuantity"] = qtaProduction

        # Consumo materie prime
        # Calcolo il consumo unitario di materie prime per articolo
        stmt = (
            db.select(
                db.func.sum(Consumo.importoTotaleC)
                )
            .where(Consumo.nrArticolo == idArticle)
            .where(Consumo.tipo == type)
        )
        tempCostCenter["costs"]["costsRawMaterial"] = db.session.scalars(stmt).one() / tempCostCenter["totalQuantity"] # unit costs
                        
        # Costi variabili
        # Calcolo i costi variabili unitari per articolo
        stmt = (
            db.text("SELECT SUM(costoOrarioBudget * Impiego.tempoRisorsa) AS costoOrarioBudget, SUM(costoOrarioConsuntivo * Impiego.tempoRisorsa) AS costoOrarioConsuntivo \
                FROM Impiego \
                INNER JOIN Risorsa ON Risorsa.codRisorsa = Impiego.risorsa AND Risorsa.areaProd = Impiego.areaProd \
                WHERE Impiego.nrArticolo = :article \
                AND Impiego.tipo = :type")
        )
        item = db.session.execute(stmt, {"article": idArticle, "type": type}).one()    
        if type == __BUDGET_CONSUNTIVO__[0]:
            tempCostCenter["costs"]["costsVariable"] = item.costoOrarioBudget
        else:
            tempCostCenter["costs"]["costsVariable"] = item.costoOrarioConsuntivo


        tempCostCenter["costs"]["costsVariable"] /= tempCostCenter["totalQuantity"] # unit costs

        analysisVariancesCostCenter[type] = tempCostCenter

    # Mix data to calculate mix standard and mix effettivo
    # Mix standard
    if analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[0]] != None:
        tempCostCenter = copy.deepcopy(costCenter)
        mixVolumeBudget = (analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[0]]["queryQuantity"] / totalSalesQuantity[__BUDGET_CONSUNTIVO__[0]]) * 100
        tempCostCenter["queryQuantity"] = mixVolumeBudget / 100 * totalSalesQuantity[__BUDGET_CONSUNTIVO__[1]]
        tempCostCenter["costs"]["costsRawMaterial"] = analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[0]]["costs"]["costsRawMaterial"]
        tempCostCenter["costs"]["costsVariable"] = analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[0]]["costs"]["costsVariable"]
        analysisVariancesCostCenter["mixStandard"] = tempCostCenter

    # Mix effettivo
    if analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[1]] != None:
        tempCostCenter = copy.deepcopy(costCenter)
        mixVolumeConsuntivo = (analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[1]]["queryQuantity"] / totalSalesQuantity[__BUDGET_CONSUNTIVO__[1]]) * 100
        tempCostCenter["queryQuantity"] = mixVolumeConsuntivo / 100 * totalSalesQuantity[__BUDGET_CONSUNTIVO__[1]]
        tempCostCenter["costs"]["costsRawMaterial"] = analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[0]]["costs"]["costsRawMaterial"]
        tempCostCenter["costs"]["costsVariable"] = analysisVariancesCostCenter[__BUDGET_CONSUNTIVO__[0]]["costs"]["costsVariable"]
        analysisVariancesCostCenter["mixEffettivo"] = tempCostCenter

    return analysisVariancesCostCenter



def selectArticle(idArticle):
    '''
    Get the analyses variances of article.

        Parameters:
            idArticle (string): di article to search
            totalSalesQuantity (dict): {BUDGET: (float), CONSUNTIVO: (int)} 
        Returns:
            JSON
    '''
    from src.controller.analysisVariances import calcanalysisVariances
    
    stmt = db.select(Article).where(Article.nrArticolo == idArticle)
    response = db.session.execute(stmt).one() 

    return {
        "id": idArticle,
        "vendite": ast.literal_eval(response.Article.analysisVariancesRevenueCenter),
        "costi": ast.literal_eval(response.Article.analysisVariancesCostCenter),
        "analysisVariances": calcanalysisVariances([response.Article])
        }