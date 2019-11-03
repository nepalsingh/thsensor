from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import bcrypt, uuid, datetime
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("serviceAccountKey.json")


app = Flask(__name__)
api = Api(app)

default_app = initialize_app(cred)
db = firestore.client()
users = db.collection(u'users')
devices = db.collection(u'devices')
temperatures = db.collection(u'temperature')

# userexists
# verifyPWD
# verifyCred
# class register user
# class register device for user
# class for post/get sensor data
# 

def usersExists(username):


    if  users.document(username).get().to_dict():
        return True
    else:
        return False
    
def deviceExists(username,deviceid):
    if not usersExists(username):
        return generateReturnDictionary(301, "Invalid Username")
    
    if devices.document(username+':'+deviceid).get().to_dict():
        return True
    else:
        return False

def verifyPWD(username, password):
    if usersExists(username):
        hashed_pw = users.document(username).get().to_dict()

        if bcrypt.hashpw(password.encode('utf8'),hashed_pw["password"]) == hashed_pw["password"]:
            return True
        else:
            return False

def verifyCred(username,password):
    if not usersExists(username):
        return generateReturnDictionary(301,"Invalid Username"), True
    
    if not verifyPWD(username,password):
        return generateReturnDictionary(302, "Invalid Password"), True

    return None, False

def generateReturnDictionary(status,msg):
    retJson = {
        "Status": status,
        "msg": msg
    }
    return jsonify(retJson)

class ResisterUser(Resource):
    def post(self):
        posteddata = request.get_json()

        username = posteddata["username"]
        password = posteddata["password"]
        firstname = posteddata["firstname"]
        lastname = posteddata["lastname"]
        phone = posteddata["phone"]


        if usersExists(username):
            return generateReturnDictionary(303,"User Already Exists")
        
        hash_pw = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
        
        posteddata["password"] = hash_pw
        posteddata["Date"] = datetime.datetime.utcnow()

        users.document(username).set(posteddata)

        return generateReturnDictionary(200, "Successfully Register " + username)


class RegisterDevice(Resource):
    def post(self):
        posteddata = request.get_json()

        username = posteddata["username"]
        password = posteddata["password"]
        deviceid = posteddata["deviceid"]
        
        retJson, error = verifyCred(username,password)

        if error:
            return retJson
        
        if deviceExists(username,deviceid):
            return generateReturnDictionary(304, "Invalid Device, Device might alredy Registered")
        
        posteddata.pop("password",None)
        posteddata["Date"] = datetime.datetime.utcnow()

        devices.document(username+':'+deviceid).set(posteddata)

        return generateReturnDictionary(200,"Device added Successfully")

class DeviceList(Resource):
    def post(self):

        posteddata = request.get_json()

        username = posteddata["username"]
        password = posteddata["password"]

        retJson, error = verifyCred(username,password)

        if error:
            return jsonify(retJson)

        user_devices = [docs.to_dict() for docs in devices.where(u"username", u"==",username).stream()]    
        return jsonify(user_devices)

class Temperature(Resource):
    def post(self):
        posteddata = request.get_json()

        username = posteddata["username"]
        password = posteddata["password"]
        deviceid = posteddata["deviceid"]
        temperature = posteddata["temperature"]
        humidity = posteddata["humidity"]

        retjson, error = verifyCred(username,password)

        if error:
            return jsonify(retjson) 

        if not deviceExists(username,deviceid):
            return generateReturnDictionary(305,"Invalid Device")

        posteddata.pop("password",None)
        posteddata["Date"] = datetime.datetime.utcnow()


        temperatures.document().set(posteddata)

        return generateReturnDictionary(200, "Temperature is Updated Successfully")
 
class TempratureList(Resource):
    def post(self):
        posteddata = request.get_json()

        username = posteddata["username"]
        password = posteddata["password"]

        retJson, error = verifyCred(username,password)

        if error:
            return jsonify(retJson)
        user_temperatures = [ doc.to_dict() for doc in temperatures.where(u"username",u"==",username).stream()]
        return jsonify(user_temperatures)

api.add_resource(ResisterUser,'/registeruser')
api.add_resource(RegisterDevice,'/registerdevice')
api.add_resource(DeviceList,'/devicelist')
api.add_resource(Temperature,'/temperature')
api.add_resource(TempratureList, '/tempraturelist')

if __name__ == __name__:
    app.run(host='0.0.0.0',port=5100)