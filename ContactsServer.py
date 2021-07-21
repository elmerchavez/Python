#from typing import final
from flask import Flask, redirect, url_for, request, make_response, jsonify
from flask_cors import CORS, cross_origin
import psycopg2, psycopg2.extras
from psycopg2 import Error
import traceback

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#******************************************************************************
def getDBConnection():
    """ Returns a connection to the DB. Connection should be closed when finished. """
    return psycopg2.connect(user="postgres", password="password", host="127.0.0.1", port="5432", database="is210")

#******************************************************************************
# Sends a simple text message to let the user know they are connected to the server
@app.route('/')
def index():
    """ Sends a simple message to let the user know they are connected to the server """
    return 'Server is up and running!'

#******************************************************************************
# Returns a JSON object of all the rows of the DB table.  
#
# usage: http://localhost:5000/list
@app.route('/list', methods=['GET'])
def list():
    """ Returns a JSON object of all the rows of the DB 'contacts' table.  """

    try:
        dbconnect = getDBConnection()
        cursor = dbconnect.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM contacts;")
        dbList = getDBList(cursor.fetchall())
        return make_response(jsonify(dbList), 200)

    except (Exception, Error) as error:
        print("Error while connecting to database.", error)
        return make_response("Error. Could not connect to database",400)

    finally:
        if dbconnect:
            cursor.close()
            dbconnect.close()

#******************************************************************************
# Returns a row from the table by specified id.  Returns a string with 
#
# usage: http://localhost:5000/contact?id=x
#      where x=int
@app.route('/contact', methods=['GET'])
def contact():
    """ Returns a JSON object of the database row from the contacts table
        with the corresponding id.   """

    try:
        id = request.args.get('id')
        dbconnect = getDBConnection()
        cursor = dbconnect.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cursor.execute(f'SELECT * FROM contacts WHERE ID={id}')
        dbList = getDBList(cursor.fetchall())
        return make_response(jsonify(dbList), 200)

    except (Exception, Error) as error:
        print("Error while connecting to database.", error)
        return make_response("Error. Could not connect to database",400)

    finally:
        if dbconnect:
            cursor.close()
            dbconnect.close()

#******************************************************************************
# Adds a new row into the table.  Returns the integer id of the row entry 
# successfully added into the DB.
#
# usage: http://localhost:5000/add?first_name=First&last_name=Last .... 
@app.route('/add', methods=['POST', 'GET'])
def addContact():
    """ Adds a new contact into the database """

    firstName = lastName = email = phone = gender = age = ""

    # get the arguments from the client
    firstName = request.args.get('first_name')
    lastName = request.args.get('last_name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    age = request.args.get('age')
    gender = request.args.get('gender')
        
    try:
        # prepare the sql statement
        if age == None or age == "":
            age = "null"
        sqlCmd = f'INSERT INTO contacts (first_name, last_name, phone, email, gender, age) VALUES(\'{firstName}\', \'{lastName}\', \'{phone}\', \'{email}\', \'{gender}\', {age}) returning id'
            
        dbconnect = getDBConnection()
        cursor = dbconnect.cursor()
        cursor.execute(sqlCmd)
        dbList = cursor.fetchone()                  # contains the id created by DB
        dbconnect.commit()
        resp_id = { 'id': dbList[0] }
        return make_response(jsonify(resp_id), 200)

    except (Exception, Error) as error:
        print("Error while connecting to database.", error)
        traceback.print_exc()
        return make_response("Error. Could not connect to database",400)

    finally:
        if dbconnect:
            cursor.close()
            dbconnect.close()
    
#******************************************************************************
# Updates  an existing row into the table by specified id. If the DB was 
# successfully updated, returns the id of the entry updated, -1 otherwise.  
#
# usage: http://localhost:5000/update?id=Id&first_name=First&last_name=Last .... 
@app.route('/update', methods=['POST', 'GET'])
def updateContact():
    """ Updates an existing contact in the database """

    firstName = lastName = email = phone = gender = age = ""

    # get the arguments from the client
    id = request.args.get('id')
    firstName = request.args.get('first_name')
    lastName = request.args.get('last_name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    age = request.args.get('age')
    gender = request.args.get('gender')
        
    try:
        # prepare the sql statement
        if age == "" or age == None:
            age = "null"

        sqlCmd = f'UPDATE contacts SET first_name=\'{firstName}\', last_name=\'{lastName}\', phone=\'{phone}\', email=\'{email}\', gender=\'{gender}\', age={age} WHERE id = {id};'
        dbconnect = getDBConnection()
        cursor = dbconnect.cursor()
        cursor.execute(sqlCmd)
        dbconnect.commit()

        status = "Update Succcessful"
        if cursor.rowcount < 1:
            status = "Could not update database"

        return make_response(status, 200)

    except (Exception, Error) as error:
        print("Error while connecting to database.", error)
        traceback.print_exc()
        return make_response("Error. Could not connect to database",400)

    finally:
        if dbconnect:
            cursor.close()
            dbconnect.close()

#******************************************************************************
# Deletes a row from the table by specified id. If successfully deleted, 
# returns the id of the contact deleted.  If no contact was deleted, or if an
# error occurred in the process, returns -1;
#
# usage: http://localhost:5000/delete?id=x
#      where x=integer
@app.route('/delete', methods=['POST', 'GET'])
def deleteContact():

    id = request.args.get('id')

    try:
        # prepare the sql statement
        sqlCmd = f'DELETE FROM contacts WHERE id = {id};'
        dbconnect = getDBConnection()
        cursor = dbconnect.cursor()
        cursor.execute(sqlCmd)
        dbconnect.commit()
        return make_response(jsonify(cursor.rowcount), 200)

    except (Exception, Error) as error:
        print("Error while connecting to database.", error)
        traceback.print_exc()
        return make_response("Error. Could not connect to database",400)

    finally:
        if dbconnect:
            cursor.close()
            dbconnect.close()


#******************************************************************************
def getDBList(dbResults):
    """ Returns a list of dictionary items corresponding to the columns of the database.
        [ {first_name:value}, {last_name:value}, ... {id:value} ]
    """

    dbList = []
    for row in dbResults:
        entry = {}
        entry['first_name'] = row['first_name']
        entry['last_name'] = row['last_name']
        entry['phone'] = row['phone']
        entry['email'] = row['email']
        entry['gender'] = row['gender']
        entry['age'] = row['age']
        entry['id'] = row['id']
        dbList.append(entry)

    return dbList



if __name__ == '__main__':
   app.run(debug = True)