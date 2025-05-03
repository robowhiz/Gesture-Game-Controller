"""
Visulisizing the csv file using matplotlib

plot_folder:
    - plot all the csv file in the folder

plot_files:
    - plot all the csv file in the listr
"""
import pandas as pd
import matplotlib.pyplot as plt
from os import listdir

class plot_folder():
    """plot all the csv file in the folder"""
    def __init__(self, folder:str = "", interval:tuple = (None, None), header:bool = None, rows:range = range(1), columns:tuple = (None, None), sub_plot:bool = False):
        contents = listdir(folder)[interval[0]:interval[1]]
        if not sub_plot:
            for content in contents:
                df = pd.read_csv(f"{folder}{content}", header = header)

                x = list(range(len(df)))
                for i in rows:
                    plt.plot(x[columns[0]:columns[1]], list(df.iloc[columns[0]:columns[1], i]))
                plt.legend([i for i in range(1, len(rows) + 1)])
                plt.title(content)
                plt.show()
        
        else:
            for y in range((len(contents)//4) + 2):
                for j in range(4):
                    if y*4 + j < len(contents):
                        df = pd.read_csv(f"{folder}{contents[y*4 + j]}", header = header)

                        x = list(range(len(df)))
                        plt.subplot(2, 2, j + 1)
                        for i in rows:
                            plt.plot(x[columns[0]:columns[1]], list(df.iloc[columns[0]:columns[1], i]))
                        plt.legend([i for i in range(1, len(rows) + 1)])
                        plt.title(contents[y*4 + j])
                plt.show()
class plot_files():
    """plot all the csv file in the list"""
    def __init__(self, folder:str = "", contents:list = [], header:bool = None, rows:range = range(1)):
        for content in contents:
            df = pd.read_csv(f"{folder}{content}", header = header)

            x = list(range(len(df)))
            for i in rows:
                plt.plot(x, list(df.iloc[:, i]))
            plt.legend([i for i in range(1, len(rows) + 1)])
            plt.title(content)
            plt.show()