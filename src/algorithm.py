import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
        self.cropdf = pd.read_csv("dataset\Crop_recommendation.csv")
        self.cropdf.head()

        #* limpar a coluna label do dataset
        X = self.cropdf.drop('label', axis=1)
        y = self.cropdf['label']
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
    
    def estatisc(self):
        # Filtrar o DataFrame para obter apenas as linhas onde 'label' é igual a 'mango'
        mango_df = self.cropdf[self.cropdf['label'] == 'mango']

        # Calcular média e desvio padrão para as variáveis numéricas no DataFrame filtrado
        mean_values_mango = mango_df.mean()
        std_dev_values_mango = mango_df.std()

        # Exibir média e desvio padrão para as variáveis das linhas de manga
        print("Média das variáveis para as linhas de manga:")
        print(mean_values_mango)
        print("\nDesvio padrão das variáveis para as linhas de manga:")
        print(std_dev_values_mango)


                


    def graphic(self):
        confusion = confusion_matrix(self.y_test, self.y_pred)
        classification_rep = classification_report(self.y_test, self.y_pred)
        
        #* Criar uma figura interativa para a matriz de confusão
        fig_1 = ff.create_annotated_heatmap(confusion, x=list(self.model.classes_), 
                                            y=list(self.model.classes_), colorscale='Blues')
        fig_1.update_layout(
        title='Matriz de Confusão',
        xaxis=dict(title='Predicted'),
        yaxis=dict(title='Actual')
        )


        classification_rep = classification_report(self.y_test, self.y_pred, output_dict=True)
    
        # Extrair métricas do relatório de classificação
        # Remove as linhas "accuracy", "macro avg" e "weighted avg"
        class_names = list(classification_rep.keys())[:-3]  
        
        #* Criar listas para armazenar os valores de métricas
        precision = []
        recall = []
        f1_score = []

        for class_name in class_names:
            precision.append(classification_rep[class_name]['precision'])
            recall.append(classification_rep[class_name]['recall'])
            f1_score.append(classification_rep[class_name]['f1-score'])

        #* Criar gráficos de barras interativos para as métricas do relatório de classificação
        fig = go.Figure()

        #* Criar gráficos de barras interativos para as métricas do relatório de classificação
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
    
        #* Criado uma figura Plotly
        fig = make_subplots(rows=2, cols=1)

        #* Adicionado um gráfico de barras
        fig.add_trace(go.Bar(
            x=['A', 'B', 'C'],
            y=[10, 20, 15],
            name='Gráfico de Barras'
        ))

        #* Adicionado um gráfico de dispersão
        fig.add_trace(go.Scatter(
            x=[1, 2, 3],
            y=[30, 15, 25],
            name='Gráfico de Dispersão'
        ))

        #* Salvar a figura em um arquivo HTML
        fig_1.write_html("grafico_confusao.html")

        return fig, fig_1
