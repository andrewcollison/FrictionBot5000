from turtle import pd
import pandas as pd
import matplotlib.pyplot as plt

def processData():
    testName = 't3'
    fileName = 't3_1_sg.csv'
    testLoc = './Results/' + str(testName)
    fileLoc = testLoc + '/' + fileName

    data = pd.read_csv(fileLoc, header = None, parse_dates=True)
    data[0] = pd.to_datetime(data[0])
    print(data.head())
    print(data.dtypes)
    ts = data[0][0]
    data.insert(2, column = 'time_elapsed', value = data[0] - ts)
    # print(ts)
    print(data.head())

    plt.plot(data['time_elapsed'], data[1])
    plt.show()
    

processData()