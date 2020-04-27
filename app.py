from flask import Flask
from flask import jsonify
from flask import request
from flask_mongoengine import MongoEngine
from mongoengine import *
from mongoengine import connect
from mongoengine.connection import disconnect
import jwt
import json
import requests
from functools import wraps


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
app.config['MONGODB_DB'] = 'post_service'
db = MongoEngine(app)
connect('db',host='localhost', port=27017,alias='postdb')

class PostDetails(Document):
    name = StringField(index=True)
    post = StringField()
    user_id=StringField()

disconnect(alias='postdb')

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
        if not token:
            return jsonify({'message': 'a valid token is missing'})

        data=jwt.decode(token, app.config['SECRET_KEY'])
        public_id=data['public_id']
        current_user = requests.get("http://127.0.0.1:5001/userpublicid/{}".format(public_id))
        current_user=current_user.json()

        return f(current_user, *args, **kwargs)

    return decorator

@app.route('/addpost',methods=['POST'])
@token_required
def add_post(current_user):
    name = request.json['name']
    post = request.json['post']
    if name and post and request.method == 'POST':

        post = PostDetails.objects.create(name=name, post=post, user_id=current_user['_id'])
        post.save()
        return (jsonify({'message': 'Post Registered successfully'}))

@app.route('/updatepost', methods=['PUT'])
@token_required
def update_post(current_user):
    name = request.json['name']
    post = request.json['post']
    # validate the received values
    if name and post and request.method == 'PUT':
        # save edits
        PostDetails.objects.filter(user_id=current_user['_id']).update(name=name, post=post)
        resp = jsonify('Post updated successfully!')
        return resp
    else:
        return not_found()

@app.route('/deletepost/<id>', methods=['DELETE'])
@token_required
def delete_post(current_user,id):
    result=PostDetails.objects.get(pk=id,user_id=current_user['_id'])
    result.delete()
    resp = jsonify('Post deleted successfully!')
    resp.status_code = 200
    return resp

@app.route('/post', methods=['GET'])
@token_required
def post_list(current_user):
    posts=PostDetails.objects.filter(user_id=current_user['_id']).all()
    output = []
    for p in posts:
        post_data = {}
        post_data['name'] = p.name
        post_data['post'] = p.post

        output.append(post_data)

    return jsonify({'list_of_authors': output})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002,debug=True)