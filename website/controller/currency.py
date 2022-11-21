from website.model.model import Cliente

# Secondo me possiamo salvare nel DB le conversioni e prenderle da lì, per rendere
# il codice più dinamico

def currencyConversion (prezzo, codiceCliente, tipo) :
    subtotaleInEuro = prezzo
    clien1 = Cliente.query.filter_by(codiceCliente=codiceCliente).first()
    valClien = clien1.valutaCliente
    #print(" CONVERSIONE VALUTA ----> " + codiceCliente + " codice valuta: " + str(valClien))
    if valClien == 2:  # caso in cui il cliente paga in dollari
        if tipo == "BUDGET":
            subtotaleInEuro = subtotaleInEuro * 0.94868  # conversione dollaro/euro a budget
        else:
            subtotaleInEuro = subtotaleInEuro * 0.8338  # conversione dollaro/euro a consuntivo
    elif valClien == 3:  # caso in cui il cliente paga in yen
        if tipo == "BUDGET":
            subtotaleInEuro = subtotaleInEuro * 0.0081300813  # conversione yen/euro a budget
        else:
            subtotaleInEuro = subtotaleInEuro * 0.00740685875  # conversione yen/euro a consuntivo
    return subtotaleInEuro