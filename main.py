import mysql.connector
from flask import Flask, render_template, request, redirect, url_for,make_response
import json
import requests as rs
from datetime import datetime



app = Flask(__name__, template_folder='templates')

def req():
  link= "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL"
  r = rs.get(link)
  return r.text

def dolar(a):
  dl = json.loads(req())
  return round((a / float(dl['USDBRL']['bid'])),2)

def eur(a):
  eu= json.loads(req())
  return round((a / float(eu['EURBRL']['bid'])),2)

def conec():
  connection = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
  )
  cursor = connection.cursor()
  return connection,cursor

@app.route('/')
def home():

  return render_template('new_login.html')


@app.route('/vish')
def vish():
     return render_template('problem_register.html')


@app.route('/process_login', methods=["POST"])
def process_login():
  connection,cursor = conec()

  info = request.form['info'] 
  email = request.form['email'] 



  if info =='cadastrar' :
    sql_select_Query = "select * from user.users where email = (%s);"
    dt_is = (email,)
    cursor.execute(sql_select_Query,dt_is)
    conting = len(cursor.fetchall())

    if conting > 0 :
       return render_template('problem_register.html')
    
    else :
      #cadastra o usuario
      nome =  request.form['nome']
      senha = request.form['senha']
      sql_insert_Query = "INSERT INTO user.users (nome, email, senha) VALUES (%s, %s, %s)"
      dt_is = (nome,email,senha)
      cursor.execute(sql_insert_Query,dt_is)
      # connection.commit()
      # cursor.close()
      # connection.close()

      #consulta o user_id
      sql_select_Query = "select * from user.users where email = %s "
      dt_is = (email,)
      cursor.execute(sql_select_Query,dt_is)
      rows = cursor.fetchall()
      #userid= rows.to_list[0]
      connection.commit()
      cursor.close()
      connection.close()
      print(str(rows[0][0]))
      return render_template('process_login.html',uid=str(rows[0][0]))
  
  elif info=='login':
    senha = request.form['senha']
    sql_select_Query = "select * from user.users where email = (%s) and senha = (%s);"
    dt_is = (email,senha)
    cursor.execute(sql_select_Query,dt_is)
    rows = cursor.fetchall()

    if len(rows) < 1 :
       return render_template('problem_register.html')
    else :
       return render_template('process_login.html',uid=str(rows[0][0]))

@app.route('/principal', methods=["GET","POST"])
def principal():
  #uid = request.args.get('userid')
  return render_template('main_style.html')
  

@app.route('/user_data',methods=["POST"]) # mexer nesse metodo
def user_data():
    
  connection,cursor = conec()

  headers = request.json

  # Example of accessing specific headers
  uid = headers.get('uid')#user_id

  #userid= request.form['usrid']
  sql_select_Query = "select user_id,nome from user.users where user_id = %s  " # mexer nesse user_id
  dt_is = (uid,)

  cursor.execute(sql_select_Query,dt_is)
  rows = cursor.fetchall()
  result = {
      'nome': rows[0][1]
  }
  cursor.close()
  connection.close()

  return result    

@app.route('/econ_data',methods=["GET","POST"]) # mexer nesse metodo
def econ_data():
    
  connection,cursor = conec()

  headers = request.json

  # Example of accessing specific headers
  uid = headers.get('uid')#user_id
  #userid= request.form['usrid']
  sql_select_Query = "select sum(value) as value, currency from cotations.financial t0   where t0.user_id = %s  group by 2 order by 2 desc"# mexer nesse user_id
  dt_is = (uid,)

  cursor.execute(sql_select_Query,dt_is)
  rows = cursor.fetchall()
  print(rows)
  if rows == []:
     
    result = {
    'currency_a': 'USD',
    'doll': float(0),
    'currency_b': 'EUR',
    'eur': float(0)
  }
    print(rows)

    return result
  
  else  :

    if len(rows) >1 :
      result = {
        'currency_a': rows[0][1],
        'doll': float(rows[0][0]),
        'currency_b': rows[1][1],
        'eur': float(rows[1][0])
      }
      print(rows)

      return result
    
    else:
       if rows[0][1] == 'USD' :
          result = {
          'currency_a': rows[0][1],
          'doll': float(rows[0][0]),
          'currency_b': 'EUR',
          'eur': float(0)
          }
          print(rows)

          return result
       else :
          result = {
          'currency_b': rows[0][1],
          'eur': float(rows[0][0]),
          'currency_a': 'USD',
          'doll': float(0)
          }
          print(rows)

          return result
          
          

@app.route('/last_update',methods=['POST'])
def last_update():
  connection,cursor = conec()
  headers = request.json

  # Example of accessing specific headers
  uid = headers.get('uid')#user_id

  #userid= request.form['usrid']
  sql_select_Query = "select  value, currency from cotations.financial where user_id = %s and data = (select max(data) from cotations.financial);"# mexer nesse user_id
  dt_is = (uid,)

  cursor.execute(sql_select_Query,dt_is)
  rows = cursor.fetchall()
  if len(rows) > 0 :
    result = {
    'value': float(rows[0][0]),
    'currency': rows[0][1]
    }
    connection.close()
    cursor.close()
    print(rows)
    return(result)
  else :
    result = {
    'value': None,
    'currency': None
    }
    connection.close()
    cursor.close()
    print(rows)
    return(result)
  
@app.route('/begin_checkout',methods=['GET'])
def begin_checkout():
   return(render_template('begin_checkout.html'))


@app.route('/checkout',methods=['GET'])
def checkout():
   return(render_template('checkout_known.html'))

@app.route('/checkout_venda',methods=['GET'])
def checkout_venda():
   return(render_template('checkout_venda.html'))

@app.route('/checkout_compra',methods=['GET'])
def checkout_compra():
   return(render_template('checkout_compra.html'))

@app.route('/transaction', methods= ['POST'])
def transaction() :
    headers = request.json

    # Example of accessing specific headers
    uid = headers.get('uid')#user_id
    value = headers.get('value') #value
    currency = headers.get('currency')  #currency usd or eur
    currency_quotation = headers.get('quotation') #valor da cotacao da moeda 
    print(headers)
    #print(f"{uid},{value},{currency},{currency_quotation}")

    insert_q = "INSERT INTO cotations.financial (data, value, currency, currency_quotation, user_id) VALUES (CONVERT_TZ(NOW(), 'UTC', 'America/Sao_Paulo'), %s, %s, %s, %s)"

    connection,cursor = conec()
    try :
      dt_is = (value,currency,currency_quotation,uid)
      cursor.execute(insert_q,dt_is)
      connection.commit()
      cursor.close()
      connection.close()
      message = {'message':'data inserted'}

      return message
    
    except Exception as e:
       message = {'message':f"thats a problem here : {e}"}

       return message
       
       



# @app.route('/process_login', methods=["POST"])
# def process_login():
#   connection,cursor = conec()

#   email = request.form['email'] 
#   senha = request.form['senha']

#   sql_select_Query = f"select user_id from user.users where email = (%s) and senha = (%s)"
#   dt_is = (email,senha)
#   cursor.execute(sql_select_Query,dt_is)
#   #print(cursor.fetchall())
#   if request.form['info'] == 'login':
#     if cursor.rowcount() > 0:
#       sql_select_Query = "select user_id from user.users where email = (%s) and senha = (%s)"
#       dt_is = (email,senha)
#       cursor.execute(sql_select_Query,dt_is)
#       if cursor.rowcount() >0 :
#         records = cursor.fetchall()
#         #print(records)

#         resp = make_response(render_template('principal.html'))

#         resp.set_cookie('user_id', 'allan122')

#         return resp

      

#   else:
#     return render_template('login.html')
  
  
# @app.route('/aa', methods=['GET'])
# def aa():
#     return render_template('checkout.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Handle credit card information and shipping address here
    credit_card_number = request.form['credit_card_number']
    expiration_date = request.form['expiration_date']
    cvv = request.form['cvv']
    address = request.form['address']
    
    # Dummy processing, just print the received data for demonstration
    print("Credit Card Number:", credit_card_number)
    print("Expiration Date:", expiration_date)
    print("CVV:", cvv)
    print("Shipping Address:", address)
    
    return 'Payment processed successfully!'


if __name__ == '__main__':
    app.run(debug=True)
