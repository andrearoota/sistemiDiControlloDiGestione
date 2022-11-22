from website import db
from website.model.model import Vendita
from flask import render_template

def selectAllArticles():
    # select Articles from sales
    return db.session.query(Vendita.nrArticolo).distinct().all()

def selectArticle(idArticle):
    # TODO
    # Example
    stmt = db.select(db.func.sum(Vendita.importoVenditeVL)).where(Vendita.nrArticolo == idArticle)
    return {
        "id": idArticle,
        "importoVendite": round(db.session.scalars(stmt).one(), 2)
        }