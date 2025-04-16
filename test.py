# from services.webscrapper.priceScrappy import *
# ser = StockDataService("SMHL", 6, "NEPSE")
# ser.fetch_data()
# ser.save_to_csv("../dataPrice/dataPrice_nepse.csv")

from services.webscrapper.nepseScrapper import *
scrapper = NepseScraper()

scrapper.start()
frame = scrapper.fetch_data_interval("04/10/2025", "04/11/2025")
frame.to_csv("dataPrice/stock_data_nepse.csv", index = False)
scrapper.stop()
