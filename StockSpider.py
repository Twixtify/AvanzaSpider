import time
import datetime
import threading
import StockMethod


class StockSpider(threading.Thread):
    def __init__(self, _id, stock_url, options, folder_path):
        """
        Constructor of StockSpider
        :param stock_url: Supplied stock on Avanza.
        :param options: What options to track on Avanza
        :param folder_path: Path to folder where data is to be written down
        """
        if not stock_url:
            print("No url provided in spider constructor!\nExiting...")
            exit(1)
        threading.Thread.__init__(self)
        self.id = _id
        self.stock_url = stock_url
        self.stock_soup = StockMethod.get_soup(self.stock_url)
        self.stock_name = self.stock_soup.find_all('title')[0].text.split(" - ")[0]
        if not options:
            print("Warning! No options provided in " + self.stock_name +
                  "\nUsing default ['Köp', 'Sälj', 'Senast', 'Tid'] options")
            self.options = ['Köp', 'Sälj', 'Senast', 'Tid']
        else:
            self.options = options
        if not folder_path:
            print("Warning! No folder provided in '" + self.stock_name + "'\nUsing script folder")
            self.dir_path = StockMethod.get_file_dir()
        else:
            self.dir_path = folder_path
        print("Initialized spider", self.id, "'" + self.stock_name + "' :", datetime.datetime.now())

    def get_stock_values(self):
        """
        Obtain, for example, the buy, sell and present price of stock
        :return: List of values corresponding to list of actions
        """
        values = []
        try:
            for tag in self.stock_soup.find_all("li", attrs={"class": "tLeft"}):  # attrs = specific tags for prices
                action = tag.find_all("span", recursive=False)[0].text
                if action in self.options:
                    value = tag.find_all("span", recursive=False)[1].text
                    values.append(value)
                    #  print(action, ":", value)
            return values
        except AttributeError:
            raise

    def upd_soup(self):
        self.stock_soup = StockMethod.get_soup(self.stock_url)

    def run(self):
        """
        Start scraping the provided stock url 'stock_url'
        :return: None
        """
        t_sleep = 60
        try:
            # Closing time for stock market #
            t_end = datetime.datetime.today().replace(hour=17, minute=30, second=0)
            #################################
            opt_str = StockMethod.lst_to_str(self.options)
            print("Started spider", self.id, "'" + self.stock_name + "'")
            # Main loop for each spider
            while (t_end-datetime.datetime.today()).total_seconds() > 0:
                self.upd_soup()  # update soup with values
                stock_values_lst = self.get_stock_values()  # save values
                stock_values_str = StockMethod.lst_to_str(stock_values_lst)
                StockMethod.write_to_file(folder=self.dir_path, filename=self.stock_name,
                                          file_data=stock_values_str, opt=opt_str)
                print(self.id, "'" + self.stock_name + "' sleeping for", t_sleep, "seconds...")
                time.sleep(t_sleep)
            print("Work complete!\tShutting down spider", self.id, "'" + self.stock_name + "'")
            return
        except OverflowError as oe:
            print(oe, "in", self.stock_name)


def main(workers=10):
    """
    Main method
    :param workers: How many spiders to run, will not be more than the number of stock urls found
    :return: None
    """
    options = ['Köp', 'Sälj', 'Senast', 'Tid']  # Which options to track
    try:
        # Make folder for data gathering if needed
        path_data_folder = StockMethod.mkfolder("StockData")
        # Load list of stocks
        path_stock_urls = StockMethod.get_stock_urls(folder=path_data_folder, filename='Stock List')
        # Fix links
        StockMethod.fix_file_urls(path_stock_urls)
        # Start a spider for each link
        with open(path_stock_urls, 'r') as file:
            worker_id = 0
            spiders = []
            # Initialize each spider/worker
            for stock_url in file:
                if workers > 0:
                    spiders.append(StockSpider(_id=worker_id, stock_url=stock_url, options=options,
                                               folder_path=path_data_folder))
                    worker_id = worker_id + 1
                    workers = workers - 1
                else:
                    break
            # Start scraping each stock
            for spider in spiders:
                spider.start()
    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    main(workers=20)
#        print("Text column to seconds:", StockMethod.get_seconds(StockMethod.read_column(file_path, _row=3, _col=3)))
