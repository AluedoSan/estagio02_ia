from flask import Flask, render_template, request, url_for, flash, redirect
from src.algorithm import Algorithm as alg
from sqlalchemy import create_engine, Column, Integer, String, Boolean,delete, DATE, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import plotly.express as px
import pandas as pd
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import date

#*BANCO DE DADOS
engine = create_engine('mysql://root:root@localhost/estagio02')
Base = declarative_base()
class Usuario_BD(Base, UserMixin):
    __tablename__ = 'user_bd'
    id = Column(Integer, primary_key=True)
    usuario = Column(String(255))
    senha = Column(String(25))
    email = Column(String(25))
    admin = Column(Boolean)

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
    data = Column(DATE)
    user_id = Column(Integer, ForeignKey('user_bd.id'))
    
    user_relation = relationship('Usuario_BD')
#Base.metadata.create_all(engine)
#*Definição do app para utilizar o Flask
app = Flask(__name__)
app.secret_key = '@lG0r1t1m0-Agr0N0m1@'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Carregue o usuário com base no user_id do banco de dados
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(Usuario_BD).get(user_id)
    session.close()
    return user

#! ROTA DE LOGIN
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifique as credenciais do usuário (substitua isso pela lógica real)
        usuario = request.form['usuario']
        senha = request.form['senha']
        Session = sessionmaker(bind=engine)
        session = Session()
        verify_user = session.query(Usuario_BD).filter_by(usuario=usuario).first()
        session.close()
        if verify_user and senha == verify_user.senha and verify_user.admin == True:
            login_user(verify_user)
            return redirect(url_for('register'))
        elif verify_user and senha == verify_user.senha:
            login_user(verify_user)
            return redirect(url_for('algorithm_screen'))
        else:
            flash('Credenciais inválidas', 'error')

    return render_template('index.html')


#! ROTA DE ADMIN
@app.route('/admin', methods=['GET','POST'])
@login_required
def register():
    Session = sessionmaker(bind=engine)
    session = Session()
    all_users = session.query(Usuario_BD).all()
    if request.method == "POST":
        #*Pegando os dados e atribuindo a uma variável
        users=request.form.get('users')
        passwords=request.form.get('passwords')
        emails=request.form.get('emails')
        admin = request.form.get('admin')
        
        #*Arrumando o tipo das variáveis
        users = str(users)
        admin = bool(admin)
        passwords=str(passwords)
        emails=str(emails)
        
        #*Banco de dados
        
        user_bd = Usuario_BD(email=emails, usuario=users, senha=passwords, admin=admin)
        session.add(user_bd)
        session.commit()
        session.close()
        return render_template('admin.html', users=users, emails=emails)
    else:
        session.close()
        return render_template('admin.html',users=all_users)



#! ROTA DE HISTÓRICO
@app.route('/historic')
@login_required
def historic():
    return render_template('historic.html')

#* ROTA DE TESTES
@app.route('/teste')
def teste():
    return render_template('teste.html')

#! ROTA DO ALGORITIMO
@app.route('/algorithm')
@login_required
def algorithm_screen():
    user_log = current_user.usuario
    return render_template("algorithm.html", PH = '', potassio = '', fosforo = ''
                           , rainfall = '', nitrogenio = '', temp = '', water = '', user_log=user_log)

#! ROTA DA FUNÇÃO DO ALGORITIMO
@app.route('/calc', methods=['POST'])
@login_required
def algorithm_calc():
    user_log = current_user.usuario
    user_id = current_user.id
    
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
    data = date.today()

    #! Instância da minha classe
    instance_algorithm = alg(PH, fosforo, potassio, nitrogenio, rainfall, temp, water)
    result, porcent, veracid = instance_algorithm.calc()
    
    #*Guardando informações
    Session = sessionmaker(bind=engine)
    session = Session()
    new_exec = Algoritimo_BD(ph=PH, p=fosforo, k=potassio, n=nitrogenio, chuva=rainfall, temper=temp,
                            umid=water, resultado=result, data=data, user_id = user_id)
    session.add(new_exec)
    session.commit()
    # Fechar a sessão
    session.close()
    #estatisticas = instance_algorithm.estatistic_culture(result)
    mean_temperature, std_dev_temperature, mean_humidity, std_dev_humidity, mean_PH, std_dev_PH, mean_rainfall, std_dev_rainfall, mean_nitrogen, std_dev_nitrogen, mean_fosforo, std_dev_fosforo, mean_potassio, std_dev_potassio = instance_algorithm.estatistic_culture(result)
    #Deixando os números com 2 casas decimais
    mean_temperature = round(mean_temperature, 2)
    mean_humidity = round(mean_humidity, 2)
    mean_fosforo = round(mean_fosforo, 2)
    mean_nitrogen = round(mean_nitrogen, 2)
    mean_PH = round(mean_PH, 2)
    mean_potassio = round(mean_potassio, 2)
    mean_rainfall = round(mean_rainfall, 2)

    std_dev_temperature = round(std_dev_temperature, 2)
    std_dev_fosforo = round(std_dev_fosforo, 2)
    std_dev_humidity = round(std_dev_humidity, 2)
    std_dev_PH = round(std_dev_PH, 2)
    std_dev_rainfall = round(std_dev_rainfall, 2)
    std_dev_nitrogen = round(std_dev_nitrogen, 2)
    std_dev_potassio = round(std_dev_potassio, 2)
    
    # Dados do usuário
    user_data = {
    'PH': PH,
    'fósforo': fosforo,
    'potassio': potassio,
    'nitrogenio': nitrogenio,
    'chuva': rainfall,
    'temperatura': temp,
    'umidade': water
    }

    # Dados médios
    mean_data = {
        'PH': mean_PH,
        'fósforo': mean_fosforo,
        'potassio': mean_potassio,
        'nitrogenio': mean_nitrogen,
        'chuva': mean_rainfall,
        'temperatura': mean_temperature,
        'umidade': mean_humidity 
    }

    # Criar um DataFrame com os dados
    df = pd.DataFrame({'Variavel': list(user_data.keys()) + list(mean_data.keys()),
                    'Valor': list(user_data.values()) + list(mean_data.values()),
                    'Origem': ['Usuário'] * 7 + ['Média'] * 7})

    # Criar o gráfico de barras agrupadas com o Plotly
    fig = px.bar(df, x='Variavel', y='Valor', color='Origem',
                title='Comparação de Dados do Usuário e Média', barmode='group')

    fig.update_xaxes(title='Variável')
    fig.update_yaxes(title='Valor')
    

    return render_template("algorithm.html",result = result, porcent = porcent, PH=PH, potassio = potassio, 
                           fosforo = fosforo, rainfall = rainfall, nitrogenio = nitrogenio, temp = temp,
                           water = water, mean_temperature=mean_temperature,
                           std_dev_temperature=std_dev_temperature,
                           mean_humidity=mean_humidity,
                           std_dev_humidity=std_dev_humidity,
                           mean_PH=mean_PH,
                           std_dev_PH=std_dev_PH,
                           mean_rainfall=mean_rainfall,
                           std_dev_rainfall=std_dev_rainfall,
                           mean_nitrogen=mean_nitrogen,
                           std_dev_nitrogen=std_dev_nitrogen,
                           mean_fosforo=mean_fosforo,
                           std_dev_fosforo=std_dev_fosforo,
                           mean_potassio=mean_potassio,
                           std_dev_potassio=std_dev_potassio,
                           veracid=veracid,
                           graphic = fig.to_html(full_html=False),
                           user_log=user_log)


if __name__ == '__main__':
    app.run(debug=True)
