from src.model.model import Client, Currency
from src import db

def currencyConversion (initialValue, clientCode, type):
    '''
    Returns the converted value with the exchange rate.

        Parameters:
			initialValue (float): Value to convert
			clientCode (string): id client
			type (string): Budget/Consuntivo
        Returns:
            converted value (float)
    '''

    # SQLite is case-sensitive
    type = type.upper()
    
    # Get exchange rate from database
    stmt = (db.select(Currency.exchangeRate)
    .select_from(Client)
    .join(Currency, Currency.currencyCode == Client.currency)
    .where(Client.clientCode == clientCode)
    .where(Currency.budOrCons == type)
    )
    return initialValue / db.session.scalars(stmt).one()