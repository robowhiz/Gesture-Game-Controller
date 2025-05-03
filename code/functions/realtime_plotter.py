from websockets.sync.client import connect
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class websocketplotter:
    _data_buffer_head = 0
    _websocket = None
    _no_of_bytes = None
    _ylimt = None
    
    def __init__(self, no_of_axis:int = 1, plot_size:int = 100, sample_frequency:int = None, plot_frequency:int = 1, ylimt:list = None):
        """
        Initialize the WebsocketPlotter.

        Parameters:
            no_of_axis (int): Number of data axes.
            plot_size (int): Size of the plot.
            sample_frequency (int): Frequency of data sampling.
            plot_frequency (int): Frequency of plot updates.
            ylimt (list): Set the boundary to the y axis of the plot
        """
        self.no_of_axis = no_of_axis
        self.plot_size =  plot_size
        self.sample_frequency =  sample_frequency
        self.data_buffer = np.array([[0.0] * no_of_axis] * plot_size)
        self.plot_frequency = sample_frequency//plot_frequency
        self._ylimt = ylimt
        
        plt.figure()
        plt.ion()
        plt.show()

    def initialize_connection(self, ipaddress:str, port:int = 81, no_of_bytes:int = None):
        """
        Initialize the websocket connection.

        Parameters:
            ipaddress (str): IP address of the websocket.
            port (int): Port number.
            no_of_bytes (int): Number of bytes to read from the websocket.
            
        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            self._websocket = connect(f"ws://{ipaddress}:{port}")
            self._no_of_bytes = no_of_bytes
            print("connected")
            return True
        except Exception as e:
            print("Connection Error")
            print(e)
            return False
        

    def read_websocket(self):
        """
        Read data from the websocket.

        Returns:
            bytes: Data read from the websocket.
        """
        return bytes.fromhex(self._websocket.recv(self._no_of_bytes).hex())

    def _plot(self, length):
        """
        Plot the data.

        Parameters:
            length (int): Length of data to plot.
        """
        df = pd.DataFrame(self.data_buffer)
        first = df[:length]
        second = df[length:]

        df = pd.concat([second, first]).reset_index(drop = True)

        plt.cla()
        for i in range(self.no_of_axis):
            if self._ylimt != None:
                plt.ylim(self._ylimt)
            plt.plot(range(self.plot_size), df[i])
        plt.legend([i + 1 for i in range(self.no_of_axis)])
        plt.pause(0.001)

    def plot(self, data:np.ndarray):
        """
        Update the data buffer and plot if needed.

        Parameters:
            data (np.ndarray): Data to update the buffer.
        """
        try:
            for i in range(self.no_of_axis):
                self.data_buffer[self._data_buffer_head][i] = data[i]
            
            self._data_buffer_head = (self._data_buffer_head + 1) % self.plot_size

            if self._data_buffer_head % self.plot_frequency == 0:
                self._plot(self._data_buffer_head)

        except Exception as e:
            print(e)
            print("closing the web socket")
            self._websocket.close()
    
    def close(self):
        print("closing the web socket")
        self._websocket.close()