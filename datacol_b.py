import csv
import json
import random
import threading
import time
from itertools import groupby
from operator import itemgetter

import matplotlib
import numpy as np
import pandas as pd
import requests
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

somevar = [0, 0]

# training algorithm
ddos = pd.read_csv("trainingset.csv")
x = ddos.drop("Column5", axis=1)
y = ddos["Column5"]
sc = StandardScaler()
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0, random_state=0)
x_train = sc.fit_transform(x_train)


def kmeans():
    kmeans = KMeans(n_clusters=2)  # creating 2 clusters for ddos/notddos
    KMmodel = kmeans.fit(x)  # initial kmean training
    y = KMmodel.labels_
    print(KMmodel.labels_)  # printing labels
    # printing values of centers of both clusters
    print(KMmodel.cluster_centers_)


def Randomforest(x1):
    rfc = RandomForestClassifier(n_estimators=200)  # how many trees in forest
    rfc.fit(x_train, y_train)
    pred_rfc = rfc.predict(x1)

    # print(classification_report(y_test,pred_rfc))
    # print('This models accuracy is:')
    # print(accuracy_score(y_test,pred_rfc))
    return pred_rfc


def collectData():
    # API request + json dump
    r = requests.get(
        "http://192.168.101.129:8181/restconf/operational/opendaylight-inventory:nodes",
        auth=("admin", "admin"),
    )
    data = r.json()
    with open("flowData.json", "w") as f:
        json.dump(data, f)

    with open("flowData.json", "r") as f:
        data = json.load(f)

    numOfCon = len(data["nodes"]["node"][1]["node-connector"])

    for i in range(numOfCon):
        a = data["nodes"]["node"][1]["node-connector"][i]["id"]

        if a == "openflow:2:1":
            b = data["nodes"]["node"][1]["node-connector"][i][
                "opendaylight-port-statistics:flow-capable-node-connector-statistics"
            ]["packets"]["received"]
            c = data["nodes"]["node"][1]["node-connector"][i][
                "opendaylight-port-statistics:flow-capable-node-connector-statistics"
            ]["packets"]["transmitted"]
            d = data["nodes"]["node"][1]["node-connector"][i][
                "opendaylight-port-statistics:flow-capable-node-connector-statistics"
            ]["bytes"]["received"]
            e = data["nodes"]["node"][1]["node-connector"][i][
                "opendaylight-port-statistics:flow-capable-node-connector-statistics"
            ]["bytes"]["transmitted"]

            entry1 = [b, c, d, e]

            with open("flowDataset4.csv", "a", newline="") as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(entry1)

            # read from raw file
            df = pd.read_csv("flowDataset4.csv")
            df = df.dropna()  # drop missing values
            df_out = df.diff()  # calculate difference from previous row
            df_out = df_out.dropna()  # drop missing values again
            df_out.to_csv("flowDataset5.csv", index=False)  # write to new file
            # read new file
            df3 = pd.read_csv("flowDataset5.csv")
            xnew = df3.values[-1].tolist()  # last row in file
            # prediction
            x_test1 = sc.transform([xnew])
            somevar = Randomforest(x_test1)
            print(xnew)
            print(somevar)

            xnew1 = int(somevar[0])  # convert label to int
            xnew2 = [int(xnew[0]), int(xnew[1]), int(xnew[2]), int(xnew[3]), xnew1]
            with open("flowDataset6.csv", "a", newline="") as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_NONE)
                wr.writerow(xnew2)
        else:
            pass


def printit():
    global somevar
    df = pd.read_csv("flowDataset5.csv")
    # df = df.apply(pd.to_numeric)
    x1 = df.values[-1].tolist()
    print(x1)

    x_test1 = sc.transform([x1])
    ynew = Randomforest(x_test1)
    print(ynew)
    somevar = ynew

    # print(metrics.accuracy_score(y_test,pred_rfc))


if __name__ == "__main__":
    x = 0
    while x < 500:
        collectData()
        print(x)
        # printit()

        time.sleep(6)
        x += 1
