import pandas as pd
class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataSingleton(metaclass=SingletonMeta):
    
    def __init__(self):
        stock = pd.read_csv('Proyecto/Data/ExistenciasNew.csv')
        sales = pd.read_csv('Proyecto/Data/FacturacionCorregida.csv',parse_dates=['Fecha'],dayfirst=True ,sep=';')
        products = pd.read_csv('Proyecto/Data/MaestroCorregido.csv', sep=';')

        self.products = self.__clean_products(products)
        self.sales = self.__clean_sales(sales)
        self.stock = self.__clean_stock(stock)

        self.sales_prod, self.stock_prod = self.__create_merges(sales,products)
        self.groupby_sales = self.__create_consolidated(sales_prod)

        self.subcategories_list = self.__create_subcategories_list(sales_prod)
        self.materials_list = self.__create_materials_list(sales_prod)

        self.__add_pos_cols(sales_prod)
        self.__add_pos_cols(products)
        self.__add_pos_cols(stock_prod)
        self.__add_pos_cols(groupby_sales)
    