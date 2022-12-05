from website import db
from website.model.model import Vendita, Consumo, Impiego, Risorsa
from website.controller.currency import currencyConversion
from flask import render_template
from sqlalchemy import and_
import copy


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

def analysesVariancesRevenueCenterByArticle(idArticle, totalSalesQuantity):
    '''
    Get the analyses variances revenue center of article.
    
        Parameters:
            idArticle (string): di article to search
            totalSalesQuantity (dict): {BUDGET: (float), CONSUNTIVO: (int)} 
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

    analysesVariancesRevenueCenter = {
        "BUDGET": copy.deepcopy(revenueCenter),
        "mixStandard": copy.deepcopy(revenueCenter),
        "mixEffettivo": copy.deepcopy(revenueCenter),
        "CONSUNTIVO": copy.deepcopy(revenueCenter)
    }

    for type in __BUDGET_CONSUNTIVO__:
        stmt = (
            db.select(Vendita)
            .where(Vendita.nrArticolo == idArticle)
            .where(Vendita.tipo == type)
        )

        for sale in db.session.execute(stmt).scalars():
            analysesVariancesRevenueCenter[type]["unitPrice"] += currencyConversion(sale.importoVenditeVL, sale.nrOrigine, type)
            analysesVariancesRevenueCenter[type]["quantity"] += sale.qta

        # Prevent ZeroDivisionError: division by zero
        if analysesVariancesRevenueCenter[type]["quantity"] != 0:
            analysesVariancesRevenueCenter[type]["unitPrice"] /= analysesVariancesRevenueCenter[type]["quantity"] # Unit price
            analysesVariancesRevenueCenter[type]["percentageOutput"] = analysesVariancesRevenueCenter[type]["quantity"] / totalSalesQuantity[type] # Percentage output

        analysesVariancesRevenueCenter[type]["quantity"] = totalSalesQuantity[type] # Total sales volume

    analysesVariancesRevenueCenter["mixStandard"]["percentageOutput"] = analysesVariancesRevenueCenter["BUDGET"]["percentageOutput"]
    analysesVariancesRevenueCenter["mixStandard"]["unitPrice"] = analysesVariancesRevenueCenter["BUDGET"]["unitPrice"]
    analysesVariancesRevenueCenter["mixEffettivo"]["unitPrice"] = analysesVariancesRevenueCenter["BUDGET"]["unitPrice"]

    analysesVariancesRevenueCenter["mixStandard"]["quantity"] = analysesVariancesRevenueCenter["CONSUNTIVO"]["quantity"]
    analysesVariancesRevenueCenter["mixEffettivo"]["quantity"] = analysesVariancesRevenueCenter["CONSUNTIVO"]["quantity"]
    analysesVariancesRevenueCenter["mixEffettivo"]["percentageOutput"] = analysesVariancesRevenueCenter["CONSUNTIVO"]["percentageOutput"]

    return analysesVariancesRevenueCenter


def analysesVariancesCostCenterByArticle(idArticle):
    '''
    Get the analyses variances cost center of article.
    
        Parameters:
            idArticle (string): di article to search
            totalSalesQuantity (dict): {BUDGET: (float), CONSUNTIVO: (int)} 
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
        "quantity": 0,
        "unitCost": [],
    }

    unitCost = {
        "unitUseRawMaterial": 0,
        "unitCostRawMaterial": 0
    }

    analysesVariancesCostCenter = {
        "BUDGET": [],
        "mixStandard": [],
        "mixEffettivo": [],
        "CONSUNTIVO": []
    }

    for type in __BUDGET_CONSUNTIVO__:
        # Calcolo dei costi medi per prodotto
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
        qtaProduction = db.session.scalars(stmt).one()
        if qtaProduction != None or qtaProduction == 0:
            tempCostCenter["quantity"] = qtaProduction
        else:
            continue # Inutile calcolare altro, non essendoci stata produzione data la precedente assunzione 

        # Consumo medio unitario materie prime
        # Calcolo il consumo medio unitario sommando il totale dei consumi e dividendolo per la quantità prodotta
        stmt = (
            db.text("SELECT sum(Consumo.qtaC) as unitUse, sum(Consumo.importoTotaleC) AS unitCost \
                FROM Consumo \
                WHERE Consumo.nrArticolo = :article \
                AND Consumo.tipo = :type \
                GROUP BY nrDocumentoODP ")
        )
        tempUnitCost = copy.deepcopy(unitCost)
        for item in db.session.execute(stmt, {"article": idArticle, "type": type}):
            tempUnitCost["unitCostRawMaterial"] = item.unitCost / item.unitUse # Forse?
            tempUnitCost["unitUseRawMaterial"] = 1 # Forse?
        
        tempUnitCost["unitCostRawMaterial"] /= tempUnitCost["unitUseRawMaterial"] # Consumo medio
        tempCostCenter["unitCost"].append(tempUnitCost)
                        
        # Costo medio unitario impiego
        # Sommo il costo dell'impiego di ogni ordine e divido per il totale prodotto
        countODP = 0
        stmt = (
            db.text("SELECT sum(costoOrarioBudget * Impiego.tempoRisorsa / Impiego.qtaOutput) AS costoOrarioBudget, sum(costoOrarioConsuntivo * Impiego.tempoRisorsa / Impiego.qtaOutput) AS costoOrarioConsuntivo \
                FROM Impiego \
                INNER JOIN Risorsa ON Risorsa.codRisorsa = Impiego.risorsa AND Risorsa.areaProd = Impiego.areaProd \
                WHERE Impiego.nrArticolo = :article \
                AND Impiego.tipo = :type \
                AND Impiego.tempoRisorsa != 0 \
                AND Impiego.qtaOutput != 0 \
                group by Impiego.nrODP")
        )
        tempUnitCost = copy.deepcopy(unitCost)
        tempUnitCost["unitUseRawMaterial"] = 1 # Quanto ci metto a produrre un singolo articolo?
        for item in db.session.execute(stmt, {"article": idArticle, "type": type}):
            countODP += 1
            if type == __BUDGET_CONSUNTIVO__[0]:
                tempUnitCost["unitCostRawMaterial"] += item.costoOrarioBudget
            else:
                tempUnitCost["unitCostRawMaterial"] += item.costoOrarioConsuntivo
        if countODP != 0:
            tempUnitCost["unitCostRawMaterial"] /= countODP
            tempCostCenter["unitCost"].append(tempUnitCost)

        analysesVariancesCostCenter[type].append(tempCostCenter)


    return analysesVariancesCostCenter



def selectArticle(idArticle):
    '''
    Get the analyses variances of article.

        Parameters:
            idArticle (string): di article to search
        Returns:
            JSON
    '''

    # Get total for calculate "percentageOutput"
    totalSalesQuantity = {}
    for type in __BUDGET_CONSUNTIVO__:
        stmt = (
            db.select(db.func.sum(Vendita.qta))
            .where(Vendita.tipo == type)
        )
        totalSalesQuantity[type] = db.session.scalars(stmt).one()
    

    return {
        "id": idArticle,
        "vendite": analysesVariancesRevenueCenterByArticle(idArticle, totalSalesQuantity),
        "costi": analysesVariancesCostCenterByArticle(idArticle),
        #"MOL": MOL
        }