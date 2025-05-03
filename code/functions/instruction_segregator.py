import pandas as pd
from os import listdir
class csv_file():
    def __init__(self, file:str = "", header:bool = None, crop:tuple = (None, None), window_size:int = 15, csv_location:str = "", std_threshold:int = 175, minimum_size_of_instruction:int = 80, maximum_size_of_instruction:int = 130):
        df = pd.read_csv(file, header = header).iloc[crop[0]:crop[1]]

        x = []

        for i in range(0, len(df) - window_size, window_size):
            data = df.iloc[i:i+window_size, 0].values
            if data.std() > std_threshold:
                x.extend([1]*window_size)
            else:
                x.extend([0]*window_size)

        X = []
        file_counter = len(listdir(csv_location)) + 1

        for i in range(len(x)):
            if x[i] == 1:
                X.append(list(df.iloc[i, :]))
            elif x[i] == 0 and x[i - 1] == 1:
                if len(X) > minimum_size_of_instruction and len(X) < maximum_size_of_instruction:
                    pd.DataFrame(X).to_csv("{0}/{1:03d}.csv".format(csv_location, file_counter), header=None, index=False)
                    file_counter += 1
                X = []

class plotter():
    def __init__(self, file:str = "", header:bool = None, crop:tuple = (None, None), window_size:int = 15, std_threshold:int = 175, rows:range = range(3)):
        df = pd.read_csv(file, header = header).iloc[crop[0]:crop[1]]

        x = []

        for i in range(0, len(df) - window_size, window_size):
            data = df.iloc[i:i+window_size, 0].values
            if data.std() > std_threshold:
                x.extend([1]*window_size)
            else:
                x.extend([0]*window_size)

        X = []

        columns = len(list(df.iloc[1, :]))
        for i in range(len(x)):
            if x[i] == 1:
                X.append(list(df.iloc[i, :]))
            else:
                X.append([0]*columns)
        
        X = pd.DataFrame(X)

        import matplotlib.pyplot as plt

        for i in rows:
            plt.plot(range(len(X)), X[i])
        plt.show()