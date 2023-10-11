from flask import Flask, render_template, request, url_for
from src.algorithm import Algorithm as alg
from sqlalchemy import create_engine, Column, Integer, String, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#*BANCO DE DADOS
engine = create_engine('mysql://root:root@localhost/estagio02')
Base = declarative_base()
class Usuario_BD(Base):
    __tablename__ = 'users_bd'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(25))
    email = Column(String(25))
    
class Algoritimo_BD(Base):
    __tablename__ = 'algoritimo_bd'
    id = Column(Integer, primary_key=True)
    ph = Column(Integer)
    p = Column(Integer)
    k = Column(Integer)
    n = Column(Integer)
    chuva = Column(Integer)
    temper = Column(Integer)
    umid = Column(Integer)
    resultado = Column(String(15))

#Base.metadata.create_all(engine)
#*Definição do app para utilizar o Flask
app = Flask(__name__)
app.secret_key = '@lG0r1t1m0-Agr0N0m1@'



#! ROTA DE LOGIN
@app.route('/', methods=['GET','POST'])
def index():
    
    return render_template('index.html')

#! ROTA DE ADMIN
@app.route('/admin')
def register():
    if request.method == 'POST':
         #*Pegando os dados e atribuindo a uma variável
        users=request.form.get('users')
        passwords=request.form.get('passwords')
        emails=request.form.get('emails')
        
        users=str(users)
        passwords=str(passwords)
        emails=str(emails)
        
        #*Banco de dados
        Session = sessionmaker(bind=engine)
        session = Session()
        new_user = Usuario_BD(name=users, password=passwords, email=emails)
        session.add(new_user)
        session.commit()
        session.close()
        return render_template('admin.html', users=users, emails=emails, passwords=passwords)
    else:
        return render_template('admin.html', users='', emails='', passwords='')



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
@app.route('/calc', methods=['POST'])
def algorithm_calc():
    #*Conexão com o banco
    
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


    #*Guardando informações
    Session = sessionmaker(bind=engine)
    session = Session()
    new_exec = Algoritimo_BD(ph=PH, p=fosforo, k=potassio, n=nitrogenio, chuva=rainfall, temper=temp,
                          umid=water, resultado=result)
    session.add(new_exec)
    session.commit()
    # Fechar a sessão
    session.close()
    

    return render_template("algorithm.html",result = result, porcent = porcent, PH=PH, potassio = potassio, 
                           fosforo = fosforo, rainfall = rainfall, nitrogenio = nitrogenio, temp = temp,
                           water = water)


if __name__ == '__main__':
    app.run(debug=True)
