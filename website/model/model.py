from website import db

class Cliente(db.Model):
    codiceCliente = db.Column(db.String(8), primary_key=True)
    fattureCumulative = db.Column(db.String(6))
    valutaCliente = db.Column(db.Integer, db.ForeignKey('valuta.codValuta'))
    vendite = db.relationship('Vendita')

class Valuta(db.Model):
    codValuta = db.Column(db.Integer, primary_key=True)
    budOCons = db.Column(db.String(10), primary_key=True) #budget o consuntivo
    tassoCambioMedio = db.Column(db.Float)

class Vendita(db.Model):
    nrMovimentoV = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10),db.ForeignKey('valuta.budOCons'))  # budget o consuntivo
    nrArticolo = db.Column(db.String(11))
    nrOrigine = db.Column(db.String(8), db.ForeignKey('cliente.codiceCliente'))
    qta = db.Column(db.Integer)
    importoVenditeVL = db.Column(db.Float)  #importo totale delle vendite in valuta locale

class Consumo(db.Model):
    nrMovimentoC = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10))  # budget o consuntivo
    codiceMP = db.Column(db.String(10))
    nrArticolo = db.Column(db.String(10), db.ForeignKey('vendita.nrArticolo'))
    nrDocumentoODP = db.Column(db.String(11))
    qtaC = db.Column(db.Integer)
    importoTotaleC = db.Column(db.Float)

class Impiego(db.Model):
    idImpiego = db.Column(db.Integer, primary_key=True)
    nrArticolo = db.Column(db.String(10))
    tipo = db.Column(db.String(10))  # budget o consuntivo
    nrODP = db.Column(db.String(11), db.ForeignKey('consumo.nrDocumentoODP'))
    descrizione = db.Column(db.String(20)) #qua metto il reparto
    areaProd = db.Column(db.String(3), db.ForeignKey('risorsa.areaProd'))  #qua metto il codice
    risorsa = db.Column(db.String(5), db.ForeignKey('risorsa.codRisorsa'))
    tempoRisorsa = db.Column(db.Float)
    qtaOutput = db.Column(db.Integer)

class Risorsa(db.Model):
    codRisorsa = db.Column(db.String(5), primary_key=True)
    areaProd = db.Column(db.String(3), primary_key=True)
    costoOrarioBudget = db.Column(db.Float)
    costoOrarioConsuntivo = db.Column(db.Float)
