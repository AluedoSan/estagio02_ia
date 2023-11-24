from flask import Flask, render_template, request, url_for, flash, redirect
from src.algorithm import Algorithm as alg
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DATE, ForeignKey, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import plotly.express as px
import pandas as pd
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import date
from sqlalchemy_pagination import paginate, Page
from flask_bcrypt import Bcrypt, check_password_hash
import time

bcrypt = Bcrypt()
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
    create_user = Column(DATE)

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

#*Definição do app para utilizar o Flask
app = Flask(__name__)
app.secret_key = '@lG0r1t1m0-Agr0N0m1@'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    # Carregue o usuário com base no user_id do banco de dados
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(Usuario_BD).get(id)
    session.close()
    return user

@app.route('/logout', methods=["GET", "POST"])
@login_required
def log_out():
    logout_user()
    flash("Usuário escolheu sair!")
    return redirect('/')

#! ROTA DE LOGIN
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica as credenciais do usuário 
        usuario = request.form['usuario']
        senha = request.form['senha']
        Session = sessionmaker(bind=engine)
        session = Session()
        verify_user = session.query(Usuario_BD).filter_by(usuario=usuario).first()
        
        if verify_user and check_password_hash(verify_user.senha, senha):
            # A senha é válida
            session.close()
            if verify_user.admin:
                login_user(verify_user)
                return redirect(url_for('register'))
            else:
                login_user(verify_user)
                return redirect(url_for('algorithm_screen'))
        else:
            # Senha inválida ou usuário não encontrado
            session.close()
            flash('Credenciais inválidas', 'error')

    return render_template('index.html')


#! ROTA DE ADMIN
@app.route('/admin', methods=['GET','POST'])
@login_required
def register():
    #Banco de dados iniciação
    Session = sessionmaker(bind=engine)
    user_name = current_user.usuario
    with Session() as session:
        all_users = session.query(Usuario_BD).all()
    
    if request.method == "POST":
        #*Pegando os dados e atribuindo a uma variável
        users=request.form.get('users')
        passwords=request.form.get('passwords')
        emails=request.form.get('emails')
        admin = request.form.get('admin')
        hashed_password = bcrypt.generate_password_hash(passwords).decode('utf-8')
        if session.query(Usuario_BD).filter(or_(Usuario_BD.usuario == users, Usuario_BD.email == emails)).first() is None:
        # Se não existirem, adicione ao banco de dados
            users = str(users)
            admin = bool(admin)
            passwords = str(passwords)
            emails = str(emails)
            data = date.today()
            
            user_bd = Usuario_BD(email=emails, usuario=users, senha=hashed_password, admin=admin, create_user=data)
            session.add(user_bd)
            session.commit()
            session.close()
            flash("Usuário adicionado com sucesso!", "success")
            time.sleep(1)
            return redirect(url_for('register'))
        else:
            session.close()
            flash("Usuário ou E-mail já existentes!", "error")
    else:
        session.close()
    return render_template('admin.html', users=all_users, user_name=user_name)


@app.route('/delete', methods=['POST'])
@login_required
def delete():
    Session = sessionmaker(bind=engine)
    user_id = request.form.get('user_id')

    with Session() as session:
        user_to_delete = session.query(Usuario_BD).filter_by(id=user_id).first()
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()
            flash("Usuário removido com sucesso!", "success")
        else:
            flash("Usuário não encontrado.", "error")

    return redirect(url_for('register'))
    

#! ROTA DE HISTÓRICO
@app.route('/historic')
@login_required
def historic():
    user_id = current_user.id
    user_name = current_user.usuario
    Session = sessionmaker(bind=engine)
    session = Session()
    id_of_user = session.query(Algoritimo_BD).filter_by(user_id=user_id)
    session.close()
    return render_template('historic.html', id_of_user = id_of_user, user_name=user_name)



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
    #Pegar o ID e nome do usuário
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
    
    #Deixando os números com 2 casas decimais - MÉDIA
    mean_temperature = round(mean_temperature, 2)
    mean_humidity = round(mean_humidity, 2)
    mean_fosforo = round(mean_fosforo, 2)
    mean_nitrogen = round(mean_nitrogen, 2)
    mean_PH = round(mean_PH, 2)
    mean_potassio = round(mean_potassio, 2)
    mean_rainfall = round(mean_rainfall, 2)
    
    #* Verificar diferenças
    dif_PH = PH - mean_PH
    dif_PH = round(dif_PH, 2)
    
    dif_fosforo = fosforo - mean_fosforo
    dif_fosforo = round(dif_fosforo, 2)
    
    dif_potassio = potassio - mean_potassio
    dif_potassio = round(dif_potassio, 2)
    
    dif_nitrogenio = nitrogenio - mean_nitrogen
    dif_nitrogenio = round(dif_nitrogenio, 2)
    
    dif_rainfall = rainfall - mean_rainfall
    dif_rainfall = round(dif_rainfall, 2)
    
    dif_temp = temp - mean_temperature
    dif_temp = round(dif_temp, 2)
    
    dif_water = water - mean_humidity
    dif_water = round(dif_water, 2)

    #Deixando os números com 2 casas decimais - DESVIO PADRÃO
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
    
    #! Detalhes da cultura
    cultures = {
        "arroz": {
            "name": "arroz",
            "soil": "argilosos, latossolos ou nitossolos, bem drenados e ricos em matéria orgânica",
            "altitude": "entre 300 e 600 metros",
            "climate": "Tropical, subtropical ou temperado",
            "irrigation": "inundação, subirrigação e aspersão"
        },
        "milho": {
            "name": "milho",
            "soil": "argilosos, latossolos ou siltosos, bem drenados e ricos em matéria orgânica",
            "altitude": "abaixo de 400 ou acima de 700 metros",
            "climate": "Tropical, subtropical ou temperado",
            "irrigation": "sulco"
        },
        "grão de bico": {
            "name": "grão de bico",
            "soil": "silicoargilosa, bem drenados e ricos em matéria orgânica",
            "altitude": "entre 640 a 760 metros",
            "climate": "subtropical ou temperado",
            "irrigation": "oscilando entre 490 kg/ha a 820 kg/ha"
        },
        "feijão": {
            "name": "feijão",
            "soil": "solos soltos, leves, de textura areno-argiosa, mais ou menos profundos, ricos em matéria orgânica e em elementos fertilizantes",
            "altitude": "0 a 1500 metros",
            "climate": "subtropical",
            "irrigation": "aspersão"
        },
        "feijão bóer": {
            "name": "feijão bóer",
            "soil": "drenados e profundos",
            "altitude": "0 a 1500 metros",
            "climate": "subtropical e tropical",
            "irrigation": "autopropelido e pivô central"
        },
        "feijão traça": {
            "name": "feijão traça",
            "soil": "Solos argilosos, arenosos ou siltosos, bem drenados e ricos em matéria orgânica.",
            "altitude": "0 a 1500 metros",
            "climate": "subtropical e tropical",
            "irrigation": "Necessária em regiões com clima seco."
        },
        "feijão mungo": {
            "name": "feijão mungo",
            "soil": "Solos argilosos",
            "altitude": "640 até 1800 metros",
            "climate": "tropical",
            "irrigation": "Necessária em regiões com clima seco."
        },
        "vigna mungo": {
            "name": "vigna mungo",
            "soil": "Solos argilosos, ricos em matéria orgânica.",
            "altitude": "0 a 1500 metros",
            "climate": "subtropical e tropical",
            "irrigation": "Necessária em regiões com clima seco."
        },
        "lentilha": {
            "name": "lentilha",
            "soil": "Alta fertilidade, boa drenagem e boa carga de matéria orgânica.",
            "altitude": "0 a 3800 metros",
            "climate": "subtropical",
            "irrigation": "Necessária de maneira frequente."
        },
        "romã": {
            "name": "romã",
            "soil": "Abundante em matéria orgânica.",
            "altitude": "0 a 1600 metros",
            "climate": "subtropical e tropical",
            "irrigation": "Frequente até o pagamento da plata, sendo assim depois disso de 2 dias e depois até 7 dias."
        },
        "banana": {
            "name": "banana",
            "soil": "areno-argilosos, ricos em matéria orgânica, com boa profundidade, plano ou levemente inclinado, não sujeitos a inundação",
            "altitude": "0 a 300 metros",
            "climate": "subtropical e tropical",
            "irrigation": "aspersão convencional."
        },
        "manga": {
            "name": "manga",
            "soil": "média fertilidade, de arenosos até argilosos, porém preferencialmente areno-argilosos, profundos, permeáveis, bem drenados, ligeiramente ácidos",
            "altitude": "0 a 1200 metros",
            "climate": "subtropical e tropical",
            "irrigation": "mínimo 50L de água."
        },
        "uva": {
            "name": "uva",
            "soil": "solos soltos e bem drenados com uma pequena porcentagem de cascalho",
            "altitude": "64 a 2473 metros",
            "climate": "subtropical",
            "irrigation": "Em falta de chuva, uma vez por semana."
        },
        "melancia": {
            "name": "melancia",
            "soil": "leve, fértil, com boa quantidade de nitrogênio",
            "altitude": "800 metros",
            "climate": "subtropical",
            "irrigation": "aspersão e gotejamento."
        },
        "melão almiscarado": {
            "name": "melão almiscarado",
            "soil": "areno-argilosos, soltos, profundos, bem drenados e ricos em húmus",
            "altitude": "0 a 1000 metros",
            "climate": "ameno",
            "irrigation": "aspersão e gotejamento."
        },
        "maça": {
            "name": "maça",
            "soil": "argiloso ou argiloso-arenoso",
            "altitude": "1200 a 1400 metros",
            "climate": "frio e úmido",
            "irrigation": "1 vez por dia."
        },
        "laranja": {
            "name": "laranja",
            "soil": "arenoargiloso, profundo, com alta fertilidade, boa drenagem.",
            "altitude": "20 a 500 metros",
            "climate": "tropical e subtropical",
            "irrigation": "Gotejamento."
        },
        "mamão": {
            "name": "mamão",
            "soil": "fertilidade elevada e boa drenagem para evitar encharcamentos.",
            "altitude": "acima de 200 metros",
            "climate": "tropical",
            "irrigation": "métodos de pressurizados."
        },
        "coco": {
            "name": "coco",
            "soil": "arenoso e bem drenado.",
            "altitude": "acima de 400 metros",
            "climate": "tropical",
            "irrigation": "100 a 240 litros por dia."
        },
        "algodão": {
            "name": "algodão",
            "soil": "arenosos, drenados, com bastante argila e matéria orgânica.",
            "altitude": "entre 200 a 1000 metros.",
            "climate": "quente e úmido.",
            "irrigation": "localizadas ou por aspersão."
        },
        "juta": {
            "name": "juta",
            "soil": " fertilidade elevada.",
            "altitude": "acima de 200 metros",
            "climate": "tropical e úmido",
            "irrigation": "métodos de irrigação mecanizadas."
        },
        "café": {
            "name": "café",
            "soil": "bem drenados e aerados, ricos em nutrientes e matéria orgânica.",
            "altitude": "entre 600 a 1200 metros.",
            "climate": "tropical",
            "irrigation": "Gotejamento."
        },
    }
    
    selected_culture = None

    # Procurar a correspondência na string result
    for culture_name, values in cultures.items():
        if result == culture_name:
            selected_culture = values
            break
    

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
                           user_log=user_log,
                           dif_PH=dif_PH,
                           dif_fosforo=dif_fosforo,
                           dif_potassio=dif_potassio,
                           dif_nitrogenio=dif_nitrogenio,
                           dif_rainfall=dif_rainfall,
                           dif_temp=dif_temp,
                           dif_water=dif_water,
                           selected_culture = selected_culture)



if __name__ == '__main__':
    app.run(debug=True)
