import os
import sys
import time
import codecs
import requests
from bs4 import BeautifulSoup

###########################################


def get_stock_urls(folder, filename='Stock List', url_stock_list='https://www.avanza.se/aktier/lista.html'):
    """
    Gather and write list of stock urls to file
    :param folder: Path to folder for writing file
    :param filename: File which urls are written to
    :param url_stock_list: Where to find the stocks
    :return: Path to file with stock urls
    """
    try:
        if connected(requests.get(url_stock_list)):
            r_obj_list = requests.get(url_stock_list)
        else:
            print("Not able to connect with:", url_stock_list)
            raise ConnectionError
        soup_stock_list = BeautifulSoup(r_obj_list.text, 'html.parser')
        path_file = join_path(body=folder, head=filename)
        with codecs.open(path_file, 'w', encoding='utf-8') as file:
            for section in soup_stock_list.find_all("tbody"):
                for link in section.find_all("a", attrs={"class": ["ellipsis", "href"]}):
                    file.write(url_stock_list + link.get('href') + '\n')
            print("Successfully gathered stocks to <", filename, "> in", folder)
            return path_file
    except (FileExistsError, ConnectionError) as e:
        print(e)
        raise e

###########################################


def fix_file_urls(path_file):
    """
    Correct urls in file
    :param path_file:
    :return: None
    """
    fixed_urls = []
    # First loop: Read each url, replace it with correct link and save to variable
    with codecs.open(path_file, 'r', encoding='utf-8') as file:
        for url in file:
            fixed_urls.append(url.replace("lista.html/aktier/", ''))
    # Second loop: Write the corrected urls to the file again
    with codecs.open(path_file, 'w', encoding='utf-8') as upd_file:
        for new_url in fixed_urls:
            upd_file.write(new_url)
    print("Done fixing urls!")

###########################################


def get_soup(stock_url):
    """
    Make a request to url of stock. Check response to get request.
    :return: BeautifulSoup object to parse price and time from.
    """
    try:
        html = requests.get(stock_url, allow_redirects=False)
        if connected(html) is True:
            return BeautifulSoup(html.text, 'html.parser')
        else:
            html.raise_for_status()
    except ConnectionError as e:
        print(e)
        print("Not able to connect with " + stock_url)
        pass

###########################################


def connected(request):
    """
    Check if request object was successful
    :param request: requests object.
    :return: True/False
    """
    if request.status_code == requests.codes.ok:
        return True
    else:
        print("Failed to connect. Status code: ", request.status_code)
        return False

###########################################


def isfloat(value):
    """
    Check if able to convert value to float
    :param value: string
    :return: True or False
    """
    try:
        float(value)
        return True
    except ValueError:
        return False

###########################################


def line_in_file(filename, _line):
    """
    Check if _line is in file filename.
    :param filename: Name of file
    :param _line: Line in file
    :return: Boolean True or False
    """
    try:
        with codecs.open(filename, 'r', encoding="utf-8") as file:
            for line in file:
                if _line in line.rstrip():
                    return True
            return False
    except FileNotFoundError:
        print("File ", filename, " not found!")


def write_to_file(folder, filename, file_data, opt):
    """
    Append text to file.
    :param folder: base folder
    :param filename: Name of file
    :param file_data: Data to be appended to file (end of file)
    :param opt: Optional parameter to write to file.
    :return:
    """
    file_path = join_path(body=folder, head=filename)
    with codecs.open(file_path, 'a', encoding="utf-8") as file:
        if line_in_file(file_path, _line=filename) is False:
            file.write(filename + '\n')
            print("Name [" + filename + "] written in:", filename)
        if line_in_file(file_path, _line=opt) is False:
            file.write(opt + '\n')
            print("Options [", opt, "] written in:", filename)
        if line_in_file(file_path, _line=file_data) is False:
            file.write(file_data + '\n')
            print("Success! " + filename + ": [", file_data, "]")
        else:
            print("No data written to file <" + filename + ">")

###########################################


def read_column(file_path, _row, _col):
    """
    :param file_path:
    :param _row: Where to start reading from
    :param _col: Which column do return
    :return: Return, if possible, values of column 'col' in file 'filename'
    """
    tmp = []
    try:
        with codecs.open(file_path, 'r', encoding='utf-8') as file:
            for row, line in enumerate(file):
                if row >= _row:
                    line = line.rstrip()
                    try:
                        tmp.append(line.split('\t')[_col])
                    except IndexError:
                        if not tmp:
                            print(IndexError, " list index _col =", _col, " out of range at row =", row, "in",
                                  file_path, "\n", "Stopped reading file.")
                        else:
                            print("Obtained values from rows [", _row, ":", row-1, "] at col", _col, "in", file_path)
                            return tmp
    except FileNotFoundError:
        print("File ", file_path, " not found!")
        raise FileNotFoundError
    if not tmp:  # Check if list is empty, return None if true
        print("Warning! Could not find any column values in", file_path)
        return
    return tmp

###########################################


def get_seconds(t_lst, form='%H:%M:%S'):
    """
    :param t_lst: Time as a string
    :param form: Format
    :return: Total number of seconds for time "t" of format "form"
    """
    tmp_lst = []
    if not t_lst and t_lst is not None:
        try:
            for t_str in t_lst:
                tmp = time.strptime(t_str, form)
                tmp_lst.append(tmp.tm_hour * 3600 + tmp.tm_min * 60 + tmp.tm_sec)
        except ValueError as e:
            print(e)
            return
        return tmp_lst
    print("Warning! Provided list is empty in", __name__ + "." + get_seconds.__name__)  # StockMethod.get_seconds

###########################################


def lst_to_str(lst):
    return "\t".join(lst).replace(",", ".")

###########################################


def mkfolder(dirname, path_body=None):
    """
    Create folder to write stock data to
    :param dirname: name of directory to write data in
    :param path_body: Path to folder where dirname will be created
    :return: Path to dirname
    """
    if path_body is None:
        path_body = get_file_dir()
    if os.path.isdir(path_body):
        path_head = os.path.join(path_body, dirname)
        try:
            os.mkdir(path_head)
            print("Created folder " + dirname + " in " + path_body)
            return path_head
        except FileExistsError:
            pass
    else:
        raise FileNotFoundError(path_body + " is not a directory!")  # costume error message
    return path_head

###########################################


def get_platform():
    """
    Determine operating system
    :return: number depending on platform
    """
    # Python 3+ use the following
    if sys.platform.startswith('linux'):
        print('OS is linux')
        return 0
    elif sys.platform.startswith('win'):
        print('OS is windows')
        return 1

###########################################


def join_path(body, head):
    """
    :param body: Base path
    :param head: Files to join at the end of base path
    :return: Join path and files to a string (indep. of OS)
    """
    return os.path.join(body, head)

###########################################


def get_file_dir():
    """
    Get current file directory
    :return: Current working file directory
    """
    return os.path.dirname(os.path.abspath(__file__))  # folder where script is run

###########################################


if __name__ == '__main__':
    mkfolder(dirname="StockData")
    print("StockMethod.py")
