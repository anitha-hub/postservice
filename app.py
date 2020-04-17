from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'user_service'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/user_service'
mongo = PyMongo(app)

@app.route('/addpost',methods=['POST'])
def add_user():
    addpost=mongo.db.post
    name = request.json['name']
    post = request.json['post']

    if name and post and request.method=='POST':
        postinsert_id=addpost.insert({'name':name, 'post':post})
        new_post = addpost.find_one({'_id': postinsert_id})
        output = {'name': new_post['name'], 'post': new_post['post']}
        return jsonify({'result': output})

@app.route('/updatepost/<id>', methods=['PUT'])
def update_post(id):
    updatepost = mongo.db.post
    name = request.json['name']
    post = request.json['post']

    # validate the received values
    if name and post and request.method == 'PUT':
        # save edits
        updatepost.update_one({'_id': ObjectId(id)}, {'$set': {'name': name, 'post':post}})
        resp = jsonify('Post updated successfully!')
        return resp
    else:
        return not_found()

@app.route('/deletepost/<id>', methods=['DELETE'])
def delete_post(id):
    deletepost = mongo.db.post
    deletepost.delete_one({'_id': ObjectId(id)})
    resp = jsonify('Post deleted successfully!')
    resp.status_code = 200
    return resp


if __name__ == '__main__':
    app.run(debug=True)