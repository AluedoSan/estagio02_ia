from flask import Flask, render_template, request
from src.algorithm import Algorithm as alg
import mysql.connector
import numpy as np


app = Flask(__name__)
app.secret_key = '@lG0r1t1m0-Agr0N0m1@'

#*BANCO DE DADOS CONEXÃO
host = 'localhost'  
user = 'root' 
password = 'root' 
database = 'estagio' 

#! ROTA DE LOGIN
@app.route('/', methods=['GET','POST'])
def index():
    
    return render_template('index.html')

#! ROTA DE ADMIN
@app.route('/admin', methods=['GET', 'POST'])
def register():
    
    return render_template('admin.html')

#! ROTA DE HISTÓRICO
@app.route('/historic')
def historic():
    return render_template('historic.html')

#* ROTA DE TESTES
@app.route('/teste')
def teste():
    return render_template('teste.html')

#! ROTA DO ALGORITIMO
@app.route('/algorithm')
def algorithm_screen():
    return render_template("algorithm.html", PH = '', potassio = '', fosforo = ''
                           , rainfall = '', nitrogenio = '', temp = '', water = '')

#! ROTA DA FUNÇÃO DO ALGORITIMO
@app.route('/algorithm/calc', methods=['POST'])
def algorithm_calc():
    #*Criando conexão com o banco de dados
    conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
    cursor = conn.cursor()
    #* Código para pegar os valores do usuário
    PH = request.form.get('PH')
    fosforo = request.form.get('fosforo')
    potassio = request.form.get('potassio')
    nitrogenio = request.form.get('nitrogenio')
    rainfall = request.form.get('rainfall')
    temp = request.form.get('temp')
    water = request.form.get('water')

    #* Código para transformar todos os valores em Float
    PH = float(PH)
    fosforo = float(fosforo)
    potassio = float(potassio)
    nitrogenio = float(nitrogenio)
    rainfall = float(rainfall)
    temp = float(temp)
    water = float(water)

    #! Instância da minha classe
    instance_algorithm = alg(PH, fosforo, potassio, nitrogenio, rainfall, temp, water)
    result, porcent = instance_algorithm.calc()

    graphic1, graphic2 = instance_algorithm.graphic()

    #*Guardando informações
    insert_query = "INSERT INTO algorithms (PH, P, K, N, temp, water, resultado) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (PH, fosforo, potassio, nitrogenio, temp, water, result)
    cursor.execute(insert_query, data)
    conn.commit()
    cursor.close()
    conn.close()

    return render_template("algorithm.html",result = result, porcent = porcent, PH=PH, potassio = potassio, 
                           fosforo = fosforo, rainfall = rainfall, nitrogenio = nitrogenio, temp = temp,
                           water = water, graphic1 = graphic1, graph_path='/static/grafico_confusao.html')


if __name__ == '__main__':
    app.run(debug=True)
