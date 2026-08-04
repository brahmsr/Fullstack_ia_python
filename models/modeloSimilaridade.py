import numpy as np #funções matemáticas
import pandas as pd #Pra analisar arquivos Excel,csv,bd e etc.
import time #Função com tempo
import matplotlib.pyplot #gráficos
import seaborn as sns #também gráficos

from sklearn.model_selection import train_test_split #separar dados pra treinos e testes
from sklearn.preprocessing import StandardScaler #Padroniza dados
from sklearn.preprocessing import LabelEncoder #OneHotEncoding (Categorias independentes)
from sklearn.metrics import accuracy_score #avalia a exatidão do modelo
from sklearn.neighbors import KNeighborsClassifier #Algoritmo de criação do modelo (nearest neighbors/vizinhos próximos)
from imblearn import under_sampling, over_sampling #balancear os dados
from imblearn.over_sampling import SMOTE #balancear os dados (Synthetic Minority Over-sampling Technique)

import warnings #alerta(penso em tirar dps)
warnings.filterwarnings("ignore") #ignora alerta

# Remove a limitação de exibição de colunas e linhas do pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#pd.options.display_float_format = '{:.2f}'.format

