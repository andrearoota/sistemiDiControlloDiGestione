from pandas import pandas
from website.model.model import Cliente, Vendita, Consumo, Impiego, Risorsa, Valuta
from website import db



def importFromXLSX():
    # TO DO
    # 1. Inserimento di massa
    
    # Drop all tables and recreate the schema
    db.drop_all()
    db.create_all()
    db.session.commit()

    # Insert Cliente
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/clienti.xlsx', index_col=0)
    records = []
    for i in range(len(df)):
        codiceCliente = df.iloc[i, 0]
        fattureCumulative = df.iloc[i, 1]
        valutaCliente = int(df.iloc[i, 2])
        records.append(Cliente(codiceCliente=codiceCliente, fattureCumulative=fattureCumulative,
                                valutaCliente=valutaCliente))
        
    db.session.add_all(records)
    db.session.commit()

    # Insert Valuta
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/tassiDiCambio.xlsx', index_col=0)
    records = []
    for i in range(len(df)):
        codValuta = int(df.iloc[i, 0])
        budOCons = df.iloc[i, 1]
        tassoCambioMedio = str(df.iloc[i, 2])
        tassoCambioMedio = tassoCambioMedio.replace(",",".")
        tassoCambioMedio = float(tassoCambioMedio)
        records.append(Valuta(codValuta=codValuta, budOCons=budOCons, tassoCambioMedio=tassoCambioMedio))

    db.session.add_all(records)
    db.session.commit()

    # Insert Vendita
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/Vendite.xlsx', index_col=0)
    records = []
    for i in range(len(df)):
        nrMovimentoV = int(df.iloc[i, 0])
        tipo = df.iloc[i, 1]
        nrArticolo = df.iloc[i, 2]
        nrOrigine = df.iloc[i, 3]
        qta = int(df.iloc[i, 4])
        importoVenditeVL = str(df.iloc[i, 5])
        importoVenditeVL = importoVenditeVL.replace(",",".")
        importoVenditeVL = float(importoVenditeVL)
        records.append(Vendita(nrMovimentoV=nrMovimentoV, tipo=tipo, nrArticolo=nrArticolo,
                                nrOrigine=nrOrigine,
                                qta=qta, importoVenditeVL=importoVenditeVL))

    db.session.add_all(records)
    db.session.commit()

    # Insert Consumo
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/Consumi.xlsx', index_col=0)
    records = []
    for i in range(len(df)):
        nrMovimentoC = int(df.iloc[i, 0])
        tipo = df.iloc[i, 1]
        codiceMP = df.iloc[i, 2]
        nrArticolo = df.iloc[i, 3]
        nrDocumentoODP = df.iloc[i, 4]
        qta = int(df.iloc[i, 5])
        importoTotaleC = str(df.iloc[i, 6])
        importoTotaleC = importoTotaleC.replace(",",".")
        importoTotaleC = float(importoTotaleC)
        records.append(Consumo(nrMovimentoC=nrMovimentoC, tipo=tipo, codiceMP=codiceMP, nrArticolo=nrArticolo,
                                nrDocumentoODP=nrDocumentoODP, qtaC=qta, importoTotaleC=importoTotaleC))

    db.session.add_all(records)
    db.session.commit()

    # Insert Impiego
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/impiegoOrarioRisorse.xlsx', index_col=0)
    records = []
    for i in range(len(df)):
        idImpiego = i
        nrArticolo = df.iloc[i, 0]
        tipo = df.iloc[i, 1]
        nrODP = df.iloc[i, 2]
        descrizione = df.iloc[i, 3]
        areaProd = df.iloc[i, 4]
        risorsa = df.iloc[i, 5]
        tempoRisorsa = str(df.iloc[i, 6])
        tempoRisorsa = tempoRisorsa.replace(",", ".")
        tempoRisorsa = float(tempoRisorsa)
        qtaOutput = int(df.iloc[i, 7])
        records.append(Impiego(idImpiego=idImpiego, nrArticolo=nrArticolo, tipo=tipo, nrODP=nrODP, descrizione=descrizione,
                                areaProd=areaProd, risorsa=risorsa, tempoRisorsa=tempoRisorsa,
                                qtaOutput=qtaOutput))

    db.session.add_all(records)
    db.session.commit()

    # Insert Risorse
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/costoOrario.xlsx', index_col=0)
    records = []
    for i in range(len(df)):
        idRisorsa = i
        codRisorsa = df.iloc[i, 0]
        areaProd = df.iloc[i, 1]
        costoOrarioBudget = str(df.iloc[i, 2])
        costoOrarioBudget = costoOrarioBudget.replace(",", ".")
        costoOrarioBudget = float(costoOrarioBudget)
        costoOrarioConsuntivo = str(df.iloc[i, 3])
        costoOrarioConsuntivo = costoOrarioConsuntivo.replace(",", ".")
        costoOrarioConsuntivo = float(costoOrarioConsuntivo)
        records.append(Risorsa(idRisorsa=idRisorsa, codRisorsa=codRisorsa, areaProd=areaProd, costoOrarioBudget=costoOrarioBudget,
                                costoOrarioConsuntivo=costoOrarioConsuntivo))

    db.session.add_all(records)
    db.session.commit()

    return "true"