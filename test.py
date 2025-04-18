# from services.webscrapper.priceScrappy import *
# ser = StockDataService("SMHL", 6, "NEPSE")
# ser.fetch_data()
# ser.save_to_csv("../dataPrice/dataPrice_nepse.csv")

from services.webscrapper.nepseScrapper import *
scrapper = NepseScraper(NepseScraper.Type.HEADFULL)
scrapper.browse(page = NepseScraper.Page.STOCK_TRADING)
frame = scrapper.fetch_data_symbol("(ADBL)", "04/10/2023", "04/11/2025")
frame.to_csv("dataPrice/stock_data_nepse.csv", index = True)
scrapper.stop()
