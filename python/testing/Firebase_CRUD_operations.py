import pyrebase

config = { }

firebase = pyrebase.initialize_app(config)
database = firebase.database()

data = {
        "Age": 12,
        "Name": "bulka",
        "Likes Pizza": False
        }


# add/create data

database.push(data)
database.child("Users").child("FirstPerson").set(data)


# print/read data

bulka = database.child("Users").child("FirstPerson").get()
print(bulka.val())


# update data

database.child("Users").child("FirstPerson").update({"Name": "John"})


# delete data

database.child("Users").child("FirstPerson").child("Age").remove()
database.child("Users").child("FirstPerson").remove()
