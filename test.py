from services.webscrapper.priceScrappy import *
ser = StockDataService("SMHL", 6, "NEPSE")
ser.fetch_data()
# ser.save_to_csv("../dataPrice/dataPrice_nepse.csv")