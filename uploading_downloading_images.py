import pyrebase

config = {
    "apiKey": "AIzaSyCO56LE4nFc4Th3WDbt_uSiXbeNiKKlouI",
    "authDomain": "safehome-c4576.firebaseapp.com",
    "projectId": "safehome-c4576",
    "databaseURL": "https://safehome-c4576-default-rtdb.firebaseio.com",
    "storageBucket": "safehome-c4576.appspot.com",
    "messagingSenderId": "516133592519",
    "appId": "1:516133592519:web:0a8b1755b92d70877bcde2",
    "measurementId": "G-TXJSM010BL",
    "seviceAccount": "firebase/serviceAccount.json"
}

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()

# uploading images from PC to Firebase
# first argument is the name of the file displayed in firebase
# second ardumend is the path to the image from the PC
storage.child("ioana.jpg").put("images/ioana.jpg")


# download images from Firebace to PC
# first argument is the name of the file displayed in firebase
# second ardumend is the path for the image to be downloaded to the PC
storage.download("ioana.jpg", "images/test_ioana.jpg")
