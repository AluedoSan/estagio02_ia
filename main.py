from flask import Flask, render_template, request, flash
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Flask(__name__)
app.secret_key = 'abcdario'

@app.route('/')
def index():
    return render_template('index.html')



@app.route("/algorithm")
def algorithm():
    return render_template("algorithm.html", PH='', P='', K='', rainfall='', N='', temp='', water='')


@app.route('/calc', methods=['POST'])
def calc():
    #Parte do código para pegar os valores do usuário
    PH = request.form.get('PH')
    P = request.form.get('P')
    K = request.form.get('K')
    rainfall = request.form.get('rainfall')
    N = request.form.get('N')
    temp = request.form.get('temp')
    water = request.form.get('water')
    #Parte para transformar todos os valores em Float
    PH = float(PH)  
    P = float(P)
    K = float(K)
    rainfall = float(rainfall)
    N = float(N)
    temp = float(temp)
    water = float(water)

    #Parte para pegar o dataset
    cropdf = pd.read_csv("C:\\Users\\alexa\\Estagio02_flask\\Crop_recommendation.csv")
    cropdf.head()

    #Parte para tirar a coluna label do dataset
    X = cropdf.drop('label', axis=1)
    y = cropdf['label']

    #Parte do treino do algoritmo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                        shuffle=True, random_state=0)

    model = KNeighborsClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    result = model.predict([[N, P, K, temp, water, PH, rainfall]])
    accuracy = accuracy_score(y_test, y_pred)
    confusion = confusion_matrix(y_test, y_pred)
    classification_rep = classification_report(y_test, y_pred)

    #transformar em porcentagem
    accuracy_porcent = accuracy * 100
    # Criar uma figura interativa para a matriz de confusão
    fig_1 = ff.create_annotated_heatmap(confusion, x=list(model.classes_), y=list(model.classes_), colorscale='Blues')
    fig_1.update_layout(
    title='Matriz de Confusão',
    xaxis=dict(title='Predicted'),
    yaxis=dict(title='Actual')
    )
    
    classification_rep = classification_report(y_test, y_pred, output_dict=True)

    # Extrair métricas do relatório de classificação
    class_names = list(classification_rep.keys())[:-3]  # Remove as linhas "accuracy", "macro avg" e "weighted avg"

    # Criar listas para armazenar os valores de métricas
    precision = []
    recall = []
    f1_score = []

    for class_name in class_names:
        precision.append(classification_rep[class_name]['precision'])
        recall.append(classification_rep[class_name]['recall'])
        f1_score.append(classification_rep[class_name]['f1-score'])

    # Criar gráficos de barras interativos para as métricas do relatório de classificação
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=class_names,
        y=precision,
        name='Precisão'
    ))

    fig.add_trace(go.Bar(
        x=class_names,
        y=recall,
        name='Revocação'
    ))

    fig.add_trace(go.Bar(
        x=class_names,
        y=f1_score,
        name='Pontuação F1'
    ))

    fig.update_layout(
        title='Métricas do Relatório de Classificação por Classe',
        xaxis=dict(title='Classes'),
        yaxis=dict(title='Valor'),
        barmode='group'
    )
   

    # Criado uma figura Plotly
    fig = make_subplots(rows=2, cols=1)

    # Adicionado um gráfico de barras
    fig.add_trace(go.Bar(
        x=['A', 'B', 'C'],
        y=[10, 20, 15],
        name='Gráfico de Barras'
    ))

    # Adicionado um gráfico de dispersão
    fig.add_trace(go.Scatter(
        x=[1, 2, 3],
        y=[30, 15, 25],
        name='Gráfico de Dispersão'
    ))

    # Salvar a figura em um arquivo HTML
    fig.write_html("graficos.html")
    fig_1.show()
    fig.show()
    return render_template('algorithm.html', result=result, accuracy_porcent=accuracy_porcent)




if __name__ == '__main__':
    app.run(debug=True)
