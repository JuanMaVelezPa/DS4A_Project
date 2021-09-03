from dataManager import DataManager
prueba=DataManager().all_incorporated()
prueba.loc[(prueba['REF']=='XA0189:00001:') &(prueba['TIENDA']=='VENTAS DIGITALES')]
#prueba2=DataManager().sales_ref_month_sin_ventas_mayores()
print(prueba.loc[(prueba['REF']=='XA0189:00001:') &(prueba['TIENDA']=='VENTAS DIGITALES')])