import pyrebase

config = {
    "apiKey": "AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI",
    "authDomain": "safehome-c4576.firebaseapp.com",
    "projectId": "safehome-c4576",
    "databaseURL": "https://safehome-c4576-default-rtdb.firebaseio.com",
    "storageBucket": "safehome-c4576.appspot.com",
    "messagingSenderId": "516133592519",
    "appId": "1:516133592519:web:0a8b1755b92d70877bcde2",
    "measurementId": "G-TXJSM010BL"
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()

data = {
        "Age": 21,
        "Name": "Gosho",
        "Likes Pizza": True
        }

database.push(data)
