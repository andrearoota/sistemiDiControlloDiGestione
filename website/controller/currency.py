from website.model.model import Cliente, Valuta
from website import db

def currencyConversion (initialValue, clientCode, type):
    '''
    Returns the converted value with the exchange rate.

            Parameters:
                    initialValue (float): Value to convert
                    clientCode (string): id client
                    type (string): Budget/Consuntivo

            Returns:
                    convertedValue (float)
    '''

    # Get exchange rate from database 
    stmt = db.select(Valuta.tassoCambioMedio).select_from(Cliente).join(Valuta, Valuta.codValuta == Cliente.valutaCliente).where(Cliente.codiceCliente == clientCode).where(Valuta.budOCons == type.upper())
    return initialValue / db.session.scalars(stmt).one()