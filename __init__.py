"""import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

cropdf = pd.read_csv("C:\\Users\\alexa\\EstagioIA\\Crop_recommendation.csv")
cropdf.head()

X = cropdf.drop('label', axis=1)
y = cropdf['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    shuffle=True, random_state=0)

model = KNeighborsClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

newdata = model.predict([[90, 12, 12, 20.879744, 75, 5.5, 220]])
print(newdata)"""
