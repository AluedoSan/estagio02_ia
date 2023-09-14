"""import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


cropdf = pd.read_csv("C:\\Users\\alexa\\Estagio02_flask\\Crop_recommendation.csv")
cropdf.head()

X = cropdf.drop('label', axis=1)
y = cropdf['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    shuffle=True, random_state=0)

model = KNeighborsClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

newdata = model.predict([[90, 12, 12, 20.879744, 75, 5.5, 220]])
accuracy = accuracy_score(y_test, y_pred)
confusion = confusion_matrix(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)
print('Relatório de Classificação:')
print(classification_rep)

print('Matriz de Confusão:')
print(confusion)

print(f'Acurácia do modelo: {accuracy * 100:.2f}%')

print(newdata)
newdata = model.predict([[90, 12, 12, 20.879744, 75, 5.5, 220]])
print(f'Previsão para novos dados: {newdata[0]}')
"""