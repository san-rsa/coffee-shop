from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
@requires_auth('get:drinks')
def get_drinks(payload):

    drinks = Drink.query.all

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST']) 
@requires_auth('post:drinks')
def add_new_drinks(payload):
    add = request.get_json()

    try:
        recipe = add['recipe']
        if isinstance(recipe, dict):
            recipe = [recipe]

        drink = Drink()

        drink.title = add['title']
        drink.recipe = json.dumps(recipe)
        drink.insert()

    except BaseException:
        abort(400)

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def delete_drinks(payload, id):
    add = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

        try:
            drink.title = add['title']
            drink.recipe = add['recipe']

            drink.update()

        except BaseException:
            abort(400)

            return jsonify({
                'success':True,
                'drinks': [drink.long()]
            })    , 200



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        Drink.delete()

    except BaseException:
        abort(400)

        return jsonify({
            'success': True,
            'delete': id
        }), 200        


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def page_not_found(error): 
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(AuthError)
def auth_error(error): 
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
        }), error.status_code

@app.errorhandler(401)
def unauthorized(error): 
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
        }), 401


@app.errorhandler(500)
def internal_server_error(error): 
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
        }), 500     


@app.errorhandler(400)
def bad_request(error): 
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
        }), 400           


@app.errorhandler(405)
def method_not_allowed(error): 
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
        }), 405

