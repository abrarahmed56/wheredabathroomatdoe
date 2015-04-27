from flask import Flask, render_template, request
from pymongo import Connection
import json, random
from bson.objectid import ObjectId

app = Flask(__name__)
conn = Connection()
db = conn['c']

@app.route("/")
def home():
    return render_template("index.html")

#creds to chesley because this code is based on his
@app.route("/hw", methods=['GET', 'POST', 'DELETE', 'PUT'])
@app.route("/hw/<id>", methods=['GET', 'POST', 'DELETE', 'PUT'])
def hw(id=None):
    method = request.method
    j = request.get_json()
    print method, id, j
    #print "j: " + str(j)
    if method == "GET":
        cursor = db.homeworks.find()
        dicts = [cursor[i] for i in range(cursor.count())]
        for d in dicts:
            d['_id'] = str(d['_id'])
        print "hi"
        return json.dumps(dicts)
        print "hi"
        print "j: " + str(j)
    elif method == "POST":
        data = json.loads(request.data)
        d = {
            'clas': data['clas'],
            'homework': data['homework'],
            'deadline': data['deadline']
        }
        json.dumps({'_id':str(db.homeworks.insert(d))})
        '''elif method == "DELETE":
        db.homeworks.remove({'_id': ObjectId(id)}, multi=False)'''
    elif method == "PUT":
        print "db: "
        for x in db.homeworks.find():
            print x
        print "id: " + str(id)
        #print "objectid: " + str(ObjectId(id))
        print json.loads(request.data)
        db.homeworks.remove({'_id': ObjectId(id)}, multi=False)
        print 'put'
    '''if id == None:
        id = j['a']
    #print "j2: " + str(j)
    if method == "POST":
        j['_id'] = id
        try:
            #print "j4: " + str(j)
            x = db.homeworks.update({'_id': id}, j, upsert=True)
            #x = db.homeworks.findOne({'_id': id})
            #for x in db.homeworks.find():
            #print str(x)
            #print "try"
            #print "id: " + str(db.homeworks.find())
            #print "update: " + str(db.homeworks.update(
        except:
            j.pop('_id', None)
            x = db.homeworks.update({'_id': id}, j)
            print "except"'''
    #x = random.random();
    #print "id: " + str(id)
    
    #print "x: " + str(x)
    #return json.dumps({'result': x})
    #return json.dumps({'_id': str(db.homeworks.insert(j))})
    return "HI"

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
