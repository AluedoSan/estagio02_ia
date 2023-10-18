import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


class Algorithm:
    def __init__(self, ph, fosforo, potassio, water, rainfall, nitrogen, temp):
        self.ph = ph
        self.fosforo = fosforo
        self.water = water
        self.rainfall = rainfall
        self.nitrogen = nitrogen
        self.potassio = potassio
        self.temp = temp

    def calc(self):
        #! carregamento do dataset
        cropdf = pd.read_csv("dataset\Crop_recommendation.csv")
        cropdf.head()

        #* limpar a coluna label do dataset
        X = cropdf.drop('label', axis=1)
        y = cropdf['label']
        X_train, X_test, y_train, self.y_test = train_test_split(X, y, test_size=0.3,
                                                        shuffle=True, random_state=0)
        self.model = KNeighborsClassifier()
        self.model.fit(X_train, y_train)
        self.y_pred = self.model.predict(X_test)

        #* pegar os valores para a predição
        result = self.model.predict([[self.nitrogen, self.fosforo, self.potassio, self.temp,
                                  self.water, self.ph, self.rainfall]])
        
        accuracy = accuracy_score(self.y_test, self.y_pred)

        #* transformar em porcentagem
        accuracy_porcent = accuracy * 100
        number_formated = "{:.2f}".format(accuracy_porcent)
        

        return result[0], number_formated
    
    def estatistic_culture(self, value):
        cropdf = pd.read_csv("dataset\Crop_recommendation.csv")
        cropdf.head()
        # Filtrar o DataFrame para obter apenas as linhas onde 'label' é igual ao valor
        result_df = cropdf.loc[cropdf['label'] == value]
        X = result_df.drop('label', axis=1)
        # Calcular a média e o desvio padrão para as colunas numéricas
        mean_values = X.mean()
        std_dev_values = X.std()
        mean_temperature = mean_values['temperature']
        std_temperature = std_dev_values['temperature']
        mean_humidity = mean_values['humidity']
        std_humidity = std_dev_values['humidity']
        mean_PH = mean_values['ph']
        std_dev_PH= std_dev_values['ph']
        mean_rainfall = mean_values['rainfall']
        std_dev_rainfall = std_dev_values['rainfall']
        mean_nitrogen = mean_values['N']
        std_dev_nitrogen = std_dev_values['N']
        mean_fosforo = mean_values['P']
        std_dev_fosforo = std_dev_values['P']
        mean_potassio = mean_values['K']
        std_dev_potassio = std_dev_values['K']
        
        # Retornar as médias e desvios padrão como um dicionário
        return mean_temperature, std_temperature, mean_humidity, std_humidity, mean_PH, std_dev_PH, mean_rainfall, std_dev_rainfall, mean_nitrogen, std_dev_nitrogen, mean_fosforo, std_dev_fosforo, mean_potassio, std_dev_potassio
