from website import db
from website.model.model import Vendita, Consumo, Impiego, Risorsa
from website.controller.currency import currencyConversion
from website.controller.article import selectAllArticlesID, analysesVariancesRevenueCenterByArticle, analysesVariancesCostCenterByArticle
from flask import render_template
from sqlalchemy import and_
import copy
import pandas as pd

__BUDGET_CONSUNTIVO__ = ["BUDGET", "CONSUNTIVO"]

def calcAnalysesVariances():
    '''
    Get the analyses variances.

        Parameters:
            None
        Returns:
            ???
    '''

    articlesRevenueCenter = []
    articlesCostCenter = []

    # Definizione strutture base per la risposta
    analysesVariancesRevenueCenter = {
        "BUDGET": 0,
        "mixStandard": 0,
        "mixEffettivo": 0,
        "CONSUNTIVO": 0
    }

    analysesVariancesCostCenter = {
        "BUDGET": 0,
        "mixStandard": 0,
        "mixEffettivo": 0,
        "CONSUNTIVO": 0
    }

    # Get total for calculate "percentageOutput"
    totalSalesQuantity = {}
    for type in __BUDGET_CONSUNTIVO__:
        stmt = (
            db.select(db.func.sum(Vendita.qta))
            .where(Vendita.tipo == type)
        )
        totalSalesQuantity[type] = db.session.scalars(stmt).one()

    # Loop into articles
    for article in selectAllArticlesID():

        ### Analisi centro di ricavo: ∑(prezzo vendita unitario * volume totale di vendita * percentuale di output)
        articlesRevenueCenter.append(analysesVariancesRevenueCenterByArticle(article.nrArticolo, totalSalesQuantity))

        ### Analisi centro di costo: volume produttivo * ∑(impiego risorsa * costo risorsa)
        articlesCostCenter.append(analysesVariancesCostCenterByArticle(article.nrArticolo))

    # Calcolo budget, mix standard/effettivo e consuntivo per il centro di ricavo
    for item in articlesRevenueCenter:
        for type in ["mixStandard", "mixEffettivo", "BUDGET", "CONSUNTIVO"]:
            analysesVariancesRevenueCenter[type] += item[type]["unitPrice"] * item[type]["quantity"] * item[type]["percentageOutput"]

    # Calcolo budget, mix standard/effettivo e consuntivo per il centro di costo
    for item in articlesCostCenter:
        for type in ["BUDGET", "CONSUNTIVO"]:
            for orderProduction in item[type]:
                totalCost = 0
                for rawMaterial in orderProduction["unitCost"]:
                    totalCost += rawMaterial["unitCostRawMaterial"] * rawMaterial["unitUseRawMaterial"]

                analysesVariancesCostCenter[type] += totalCost * orderProduction["quantity"]

    return {
        "Quantita": totalSalesQuantity,
        "Centro di ricavo": analysesVariancesRevenueCenter,
        "Centri di costo": analysesVariancesCostCenter
    }
    


