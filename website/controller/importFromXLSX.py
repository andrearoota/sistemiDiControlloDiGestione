from pandas import pandas
from website.model.model import Cliente, Vendita, Consumo, Impiego, Risorsa, Valuta
from website import db

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

    # Insert Cliente
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/clienti.xlsx')
    records = []
    for i in range(len(df)):
        codiceCliente = df.iloc[i, 0]
        fattureCumulative = df.iloc[i, 2]
        valutaCliente = int(df.iloc[i, 3])
        records.append(Cliente(codiceCliente=codiceCliente, fattureCumulative=fattureCumulative,
                                valutaCliente=valutaCliente))
        
    db.session.add_all(records)
    db.session.commit()

    # Insert Valuta
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/tassi Di Cambio.xlsx')
    records = []
    for i in range(len(df)):
        codValuta = int(df.iloc[i, 0])
        budOCons = df.iloc[i, 1].upper()
        tassoCambioMedio = str(df.iloc[i, 2])
        tassoCambioMedio = tassoCambioMedio.replace(",",".")
        tassoCambioMedio = float(tassoCambioMedio)
        records.append(Valuta(codValuta=codValuta, budOCons=budOCons, tassoCambioMedio=tassoCambioMedio))

    db.session.add_all(records)
    db.session.commit()

    # Insert Vendita
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/Vendite.xlsx')
    records = []
    for i in range(len(df)):
        nrMovimentoV = int(df.iloc[i, 0])
        tipo = df.iloc[i, 1].upper()
        nrArticolo = df.iloc[i, 3]
        nrOrigine = df.iloc[i, 5]
        qta = int(df.iloc[i, 6])
        importoVenditeVL = str(df.iloc[i, 7])
        importoVenditeVL = importoVenditeVL.replace(",",".")
        importoVenditeVL = float(importoVenditeVL)
        records.append(Vendita(nrMovimentoV=nrMovimentoV, tipo=tipo, nrArticolo=nrArticolo,
                                nrOrigine=nrOrigine,
                                qta=qta, importoVenditeVL=importoVenditeVL))

    db.session.add_all(records)
    db.session.commit()

    # Insert Consumo
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/Consumi.xlsx')
    records = []
    for i in range(len(df)):
        nrMovimentoC = int(df.iloc[i, 0])
        tipo = df.iloc[i, 1].upper()
        codiceMP = df.iloc[i, 3]
        nrArticolo = df.iloc[i, 5]
        nrDocumentoODP = df.iloc[i, 6]
        qta = int(df.iloc[i, 7])
        importoTotaleC = str(df.iloc[i, 8])
        importoTotaleC = importoTotaleC.replace(",",".")
        importoTotaleC = float(importoTotaleC)
        records.append(Consumo(nrMovimentoC=nrMovimentoC, tipo=tipo, codiceMP=codiceMP, nrArticolo=nrArticolo,
                                nrDocumentoODP=nrDocumentoODP, qtaC=qta, importoTotaleC=importoTotaleC))

    db.session.add_all(records)
    db.session.commit()

    # Insert Impiego
    # Read from file .xlsx and insert into database
    df = pandas.read_excel('inputXLSX/impiego Orario Risorse.xlsx')
    records = []
    for i in range(len(df)):
        idImpiego = i
        nrArticolo = df.iloc[i, 0]
        tipo = df.iloc[i, 1].upper()
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
    df = pandas.read_excel('inputXLSX/costo orario risorse - budget.xlsx')
    records = []
    for i in range(len(df)):
        codRisorsa = df.iloc[i, 0]
        areaProd = df.iloc[i, 1]
        costoOrarioBudget = str(df.iloc[i, 2])
        costoOrarioBudget = costoOrarioBudget.replace(",", ".")
        costoOrarioBudget = float(costoOrarioBudget)
        records.append(Risorsa(codRisorsa=codRisorsa, areaProd=areaProd, costoOrarioBudget=costoOrarioBudget))

    df = pandas.read_excel('inputXLSX/costo orario risorse - consuntivo.xlsx')
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

    return "true"