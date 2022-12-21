from src import db

class Client(db.Model):
    clientCode = db.Column(db.String(8), primary_key=True)
    cumulativeInvoices = db.Column(db.String(6))
    currency = db.Column(db.Integer, db.ForeignKey('currency.currencyCode'))
    sales = db.relationship('Sales')
    analysisVariances = db.Column(db.Text())

class Currency(db.Model):
    currencyCode = db.Column(db.Integer, primary_key=True)
    budOrCons = db.Column(db.String(10), primary_key=True) # budget o consuntivo
    exchangeRate = db.Column(db.Float)
    analysisVariances = db.Column(db.Text())

class Sales(db.Model):
    movementNumberS = db.Column(db.Integer, primary_key=True)
    budOrCons = db.Column(db.String(10),db.ForeignKey('currency.budOrCons'))  # budget o consuntivo
    articleNumber = db.Column(db.String(11), db.ForeignKey('article.articleNumber'))
    originNumber = db.Column(db.String(8), db.ForeignKey('client.clientCode'))
    quantityS = db.Column(db.Integer)
    salesAmount = db.Column(db.Float)  # importo totale delle vendite in valuta locale

class Consumption(db.Model):
    movementNumberC = db.Column(db.Integer, primary_key=True)
    budOrCons = db.Column(db.String(10))  # budget o consuntivo
    rawMaterialCode = db.Column(db.String(10))
    articleNumber = db.Column(db.String(10), db.ForeignKey('article.articleNumber'))
    nrDocumentoODP = db.Column(db.String(11))
    quantityC = db.Column(db.Integer)
    totalAmountC = db.Column(db.Float)

class Impiego(db.Model):
    idImpiego = db.Column(db.Integer, primary_key=True)
    articleNumber = db.Column(db.String(10), db.ForeignKey('article.articleNumber'))
    budOrCons = db.Column(db.String(10))  # budget o consuntivo
    nrODP = db.Column(db.String(11), db.ForeignKey('consumption.nrDocumentoODP'))
    descrizione = db.Column(db.String(20))
    areaProd = db.Column(db.String(3), db.ForeignKey('risorsa.areaProd'))
    risorsa = db.Column(db.String(5), db.ForeignKey('risorsa.codRisorsa'))
    tempoRisorsa = db.Column(db.Float)
    qtaOutput = db.Column(db.Integer)

class Risorsa(db.Model):
    codRisorsa = db.Column(db.String(5), primary_key=True)
    areaProd = db.Column(db.String(3), primary_key=True)
    costoOrarioBudget = db.Column(db.Float)
    costoOrarioConsuntivo = db.Column(db.Float)

class Article(db.Model):
    articleNumber = db.Column(db.String(11), primary_key=True)
    analysisVariancesCostCenter = db.Column(db.Text())
    analysisVariancesRevenueCenter = db.Column(db.Text())
