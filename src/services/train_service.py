from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from xgboost import XGBClassifier
import sys
import os
import joblib
import json
import pandas as pd

# adicionando o diretório 'src' ao sys.path
path = os.path.abspath(os.path.join(os.getcwd(), "..", "src"))
if path not in sys.path:
    sys.path.append(path)

from sensor_service import carregar_dados_bd

class TrainService:
    
    MODEL_DIR = os.path.abspath(
        os.path.join(os.getcwd(), "vectorstore")
    )
    MODEL_PATH = os.path.join(MODEL_DIR, "fault_model.pkl")
    METRICS_PATH = os.path.join(MODEL_DIR, "training_metrics.json")

    @staticmethod
    def train():
        
        os.makedirs(TrainService.MODEL_DIR, exist_ok=True)

        # Decidi usar o XGBClassifier, pois após alguns (muitos) testes foi o melhor modelo que encontrei com uma acurácia e F1 de 87% nas configs atuais.
        # (O modelo ainda pode ser melhorado)

        df = carregar_dados_bd()
        print(f"Shape do DataFrame: {df.shape}")
        print(f"Contagem de nulos: \n{df.isnull().sum()}")
        
        print("Contagem de classes:")
        print(df["fault"].value_counts(normalize=True))
        
        print("Removendo colunas desnecessárias:")
        df = df.drop(columns=[
            "id",
            "created_at"
        ],
        errors="ignore"
        )
        print(f"Shape do DataFrame: {df.shape}")
        print(f"Colunas: {df.columns.tolist()}")
        
        print("separando features e label:")
        X = df.drop("fault", axis=1)
        y = df["fault"]
        print(f"features: {X.shape}")
        print(f"label: {y.shape}")

        min_amostras = 30
        contagem = df["fault"].value_counts()
        classes_boas = contagem[contagem >= min_amostras].index
        df = df[df["fault"].isin(classes_boas)]
        print("Classes depois do filtro:", df["fault"].nunique())
        print(f"Shape do DataFrame: {df.shape}")
        
        X = df.drop("fault", axis=1)
        y = df["fault"]
        print(f"Shape de X: {X.shape}")
        print(f"Shape de y: {y.shape}")

        # Codificação das classes
        encoder = LabelEncoder()
        y = encoder.fit_transform(y)

        # Divisão treino/teste  
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        
        # array de resultado        
        resultados = []

        #Treinando modelo        
        # modelo = ExtraTreesClassifier(
        #     n_estimators=100,
        #     max_depth=40,
        #     min_samples_split=10,
        #     min_samples_leaf=5,
        #     random_state=42,
        #     n_jobs=4
        # )
        
        modelo = XGBClassifier(n_estimators=50, max_depth=20,
            random_state=42,
            eval_metric="mlogloss",
            tree_method="hist"
        )
        
        #adicionando modelo no array de resultado        

        modelo.fit(X_train, y_train)

        pred = modelo.predict(X_test)
        
        resultado = {
            "Modelo": "XGBoost",
            "Accuracy": float(accuracy_score(y_test, pred)),
            "Precision": float(
                precision_score(
                    y_test,
                    pred,
                    average="weighted",
                    zero_division=0,
                )
            ),
            "Recall": float(
                recall_score(
                    y_test,
                    pred,
                    average="weighted",
                    zero_division=0,
                )
            ),
            "F1": float(
                f1_score(
                    y_test,
                    pred,
                    average="weighted",
                    zero_division=0,
                )
            ),
            "Classes": encoder.classes_.tolist(),
            "Total_amostras": len(df),
            "Features": X.columns.tolist(),
        }
        print(resultado)
        
        #Salvando modelo treinado
        joblib.dump(
            {
                "model": modelo,
                "encoder": encoder,
                "features": X.columns.tolist(),
            },
            TrainService.MODEL_PATH,
        )
        
        print(f"\nModelo salvo em:\n{TrainService.MODEL_PATH}")
        
        # Salva métricas
        with open(
            TrainService.METRICS_PATH,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                resultado,
                f,
                indent=4,
                ensure_ascii=False,
            )

        print(f"Métricas salvas em:\n{TrainService.METRICS_PATH}")

        return {
            "model": modelo,
            "encoder": encoder,
            "metrics": resultado,
        }
        
if __name__ == "__main__":
    TrainService.train()