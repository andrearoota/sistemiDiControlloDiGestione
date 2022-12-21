from src import db
from src.model.model import Sales

__BUDGET_CONSUNTIVO__ = ["BUDGET", "CONSUNTIVO"]

def countSales():
    '''
    Count sales group by budget/consuntivo.
    
        Parameters:
            None
        Returns:
            (dict): {BUDGET: (int), CONSUNTIVO: (int)} 

    '''
    totalSalesQuantity = dict()
    for type in __BUDGET_CONSUNTIVO__:
        stmt = (
            db.select(db.func.sum(Sales.quantityS))
            .where(Sales.budOrCons == type)
        )
        totalSalesQuantity[type] = db.session.scalars(stmt).one()

    return totalSalesQuantity

