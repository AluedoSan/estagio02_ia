from flask import Flask, render_template, request, flash
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


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
    PH = request.form.get('PH')
    P = request.form.get('P')
    K = request.form.get('K')
    rainfall = request.form.get('rainfall')
    N = request.form.get('N')
    temp = request.form.get('temp')
    water = request.form.get('water')

    PH = float(PH)  
    P = float(P)
    K = float(K)
    rainfall = float(rainfall)
    N = float(N)
    temp = float(temp)
    water = float(water)

    cropdf = pd.read_csv("C:\\Users\\alexa\\EstagioIA\\Crop_recommendation.csv")
    cropdf.head()

    X = cropdf.drop('label', axis=1)
    y = cropdf['label']

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.3, shuffle=True, random_state=0)


    model = KNeighborsClassifier()
    model.fit(X_train, y_train)

    result = model.predict([[N, P, K, temp, water, PH, rainfall]])

    return render_template('algorithm.html', PH=PH, P=P, K=K, rainfall=rainfall, N=N, temp=temp, water=water, result=result)




if __name__ == '__main__':
    app.run(debug=True)
