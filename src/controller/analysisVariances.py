from src import db
from src.controller.article import (analysisVariancesCostCenterByArticle,
                                    analysisVariancesRevenueCenterByArticle,
                                    selectAllArticlesID)
from src.controller.sale import countSales
from src.model.model import Article
import ast

__BUDGET_CONSUNTIVO__ = ["BUDGET", "CONSUNTIVO"]

def calcanalysisVariances(idArticles, withCache = True, market = None, client = None):
    '''
    Get the analyses variances.

        Parameters:
            idArticles (array): array of id
            withCache (bool): calculate with cached data
        Returns:
            (dict): {
                Quantity: { BUDGET: (float), mixStandard: (float), mixEffettivo: (float), CONSUNTIVO: (float) },
                RevenueCenter: { BUDGET: (float), mixStandard: (float), mixEffettivo: (float), CONSUNTIVO: (float) },
                CostCenter: { BUDGET: (float), mixStandard: (float), mixEffettivo: (float), CONSUNTIVO: (float) },
                Mol: { BUDGET: (float), mixStandard: (float), mixEffettivo: (float), CONSUNTIVO: (float) }
            }
    '''

    articlesRevenueCenter = []
    articlesCostCenter = []

    # Definizione strutture base per la risposta
    analysisVariancesRevenueCenter = {
        "BUDGET": 0,
        "mixStandard": 0,
        "mixEffettivo": 0,
        "CONSUNTIVO": 0
    }

    analysisVariancesCostCenter = {
        "BUDGET": 0,
        "mixStandard": 0,
        "mixEffettivo": 0,
        "CONSUNTIVO": 0
    }

    mol = {
        "BUDGET": 0,
        "mixStandard": 0,
        "mixEffettivo": 0,
        "CONSUNTIVO": 0
    }

    quantity = {
        "BUDGET": 0,
        "mixStandard": 0,
        "mixEffettivo": 0,
        "CONSUNTIVO": 0
    }

    for idArticle in idArticles:
        if withCache:
            stmt = db.select(Article).where(Article.nrArticolo == idArticle.nrArticolo)
            for item in db.session.execute(stmt):
                # Analisi centro di ricavo: ∑(prezzo vendita unitario * volume totale di vendita * percentuale di output)
                articlesRevenueCenter.append(eval(item.Article.analysisVariancesRevenueCenter))
                # Analisi centro di costo: volume produttivo * ∑(impiego risorsa * costo risorsa)
                articlesCostCenter.append(eval(item.Article.analysisVariancesCostCenter))
    
        else:
            # Get total for calculate "percentageOutput"
            totalSalesQuantity = countSales()

            # Analisi centro di ricavo: ∑(prezzo vendita unitario * volume totale di vendita * percentuale di output)
            articlesRevenueCenter.append(analysisVariancesRevenueCenterByArticle(idArticle.nrArticolo, totalSalesQuantity, market, client))
            # Analisi centro di costo: volume produttivo * ∑(impiego risorsa * costo risorsa)
            articlesCostCenter.append(analysisVariancesCostCenterByArticle(idArticle.nrArticolo, totalSalesQuantity, market, client))

    # Calcolo budget, mix standard/effettivo e consuntivo per il centro di ricavo
    for item in articlesRevenueCenter:
        for type in ["mixStandard", "mixEffettivo", "BUDGET", "CONSUNTIVO"]:
            analysisVariancesRevenueCenter[type] += item[type]["unitPrice"] * item[type]["quantity"] * item[type]["percentageOutput"]
            quantity[type] += item[type]["quantity"] * item[type]["percentageOutput"]

    # Calcolo budget, mix standard/effettivo e consuntivo per il centro di costo
    for item in articlesCostCenter:
        for type in ["mixStandard", "mixEffettivo", "BUDGET", "CONSUNTIVO"]:
            if item[type] != None:
                totalCost = item[type]["costs"]["costsVariable"] + item[type]["costs"]["costsRawMaterial"]
                analysisVariancesCostCenter[type] += totalCost * item[type]["queryQuantity"]

    # Calcolo margine operativo lordo (mol)
    for type in ["mixStandard", "mixEffettivo", "BUDGET", "CONSUNTIVO"]:
        mol[type] = analysisVariancesRevenueCenter[type] - analysisVariancesCostCenter[type]

    return {
        "Quantity": quantity,
        "RevenueCenter": analysisVariancesRevenueCenter,
        "CostCenter": analysisVariancesCostCenter,
        "Mol": mol
    }
    


