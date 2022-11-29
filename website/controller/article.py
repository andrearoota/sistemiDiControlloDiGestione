from website import db
from website.model.model import Vendita
from flask import render_template

def selectAllArticlesID():
    '''
    Gets article ids from sales table.
    
        Parameters:
            None
        Returns:
            Array

    '''
    # select Articles from sales
    stmt = db.select(Vendita.nrArticolo).distinct().order_by(Vendita.nrArticolo.asc())
    return db.session.execute(stmt)

def selectArticle(idArticle):
    '''
    Get the analyses variances of article.

        Parameters:
            idArticle (string): di article to search
        Returns:
            JSON
    '''
    # TODO
    # Example
    stmt = db.select(db.func.sum(Vendita.importoVenditeVL)).where(Vendita.nrArticolo == idArticle)
    return {
        "id": idArticle,
        "importoVendite": round(db.session.scalars(stmt).one(), 2)
        }