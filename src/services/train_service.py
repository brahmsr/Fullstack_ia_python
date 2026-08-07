from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from datetime import datetime
from xgboost import XGBClassifier
import sys
import os
import joblib
import json
import pandas as pd

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from services.sensor_service import carregar_dados_bd

class TrainService:
    # Decidi usar o XGBClassifier, pois após alguns (muitos) testes foi o melhor modelo que encontrei com uma acurácia e F1 de 87% nas configs atuais.
    # (O modelo ainda pode ser melhorado)

    MODEL_DIR = os.path.join(os.path.dirname(SRC_DIR), "vectorstore")
    MODEL_PATH = os.path.join(MODEL_DIR, "fault_model.pkl")
    METRICS_PATH = os.path.join(MODEL_DIR, "training_metrics.json")
    MIN_SAMPLES = 30
    
    @staticmethod
    def load_data():
        """Carrega os dados do banco de dados"""
        df = carregar_dados_bd()
        print(f"Shape do DataFrame: {df.shape}")
        print(f"Contagem de nulos: \n{df.isnull().sum()}")

        df = df.drop(
            columns=["id", "created_at"],
            errors="ignore"
        )

        contagem = df["fault"].value_counts()

        classes_validas = contagem[
            contagem >= TrainService.MIN_SAMPLES
        ].index

        df = df[df["fault"].isin(classes_validas)]

        X = df.drop(columns="fault")
        X = X.apply(pd.to_numeric)

        y = df["fault"]

        encoder = LabelEncoder()

        y = encoder.fit_transform(y)

        return X, y, encoder
    
    @staticmethod
    def train_model(X_train, y_train):
        #rodei o RandomizedSearchCV e encontrei os melhores parâmetros, então movi para o notebook (foram 4hrs) (ver notebooks/CriacaoModeloPreditivo.ipynb)
        #o que não fez uma diferença muito grande, já que eu tinha conseguido chegar a 87 antes (ganho de pouca % no F1)
        modelo = XGBClassifier(
            subsample=0.8,
            n_estimators=300,
            max_depth=8,
            learning_rate=0.1,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="mlogloss",
            tree_method="hist"
        )

        modelo.fit(X_train, y_train)

        return modelo
        
        
    @staticmethod
    def evaluate(
        model,
        X_test,
        y_test,
        encoder,
        features
    ):
        """Avalia o modelo e gera métricas"""
        
        pred = model.predict(X_test)

        feature_importance = dict(
            sorted(
                zip(
                    features,
                    (float(imp) for imp in model.feature_importances_)
                ),
                key=lambda x: x[1],
                reverse=True
            )
        )

        report = classification_report(
            y_test,
            pred,
            target_names=encoder.classes_,
            output_dict=True,
            zero_division=0
        )

        resultado = {

            "algorithm": "XGBClassifier",

            "trained_at": datetime.now().isoformat(),

            "accuracy": float(
                accuracy_score(
                    y_test,
                    pred
                )
            ),

            "precision": float(
                precision_score(
                    y_test,
                    pred,
                    average="weighted",
                    zero_division=0
                )
            ),

            "recall": float(
                recall_score(
                    y_test,
                    pred,
                    average="weighted",
                    zero_division=0
                )
            ),

            "f1": float(
                f1_score(
                    y_test,
                    pred,
                    average="weighted",
                    zero_division=0
                )
            ),

            "confusion_matrix": confusion_matrix(
                y_test,
                pred
            ).tolist(),

            "classification_report": report,

            "feature_importance": feature_importance,

            "model_parameters": model.get_params(),

            "classes": encoder.classes_.tolist(),

            "features": features

        }

        return resultado
        
    @staticmethod
    def save(
        model,
        encoder,
        features,
        metrics
    ):
        """Salva o modelo e métricas"""
        os.makedirs(
            TrainService.MODEL_DIR,
            exist_ok=True
        )

        joblib.dump(
            {
                "model": model,
                "encoder": encoder,
                "features": features
            },
            TrainService.MODEL_PATH
        )

        with open(
            TrainService.METRICS_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metrics,
                f,
                indent=4,
                ensure_ascii=False
            )

        print("\nModelo salvo em:")
        print(TrainService.MODEL_PATH)

        print("\nMétricas salvas em:")
        print(TrainService.METRICS_PATH)
        
    @staticmethod
    def train():

        X, y, encoder = TrainService.load_data()

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            stratify=y,
            random_state=42
        )

        modelo = TrainService.train_model(
            X_train,
            y_train
        )

        metricas = TrainService.evaluate(
            modelo,
            X_test,
            y_test,
            encoder,
            X.columns.tolist()
        )

        TrainService.save(
            modelo,
            encoder,
            X.columns.tolist(),
            metricas
        )

        print("\nResumo do treinamento\n")

        print(
            json.dumps(
                metricas,
                indent=4,
                ensure_ascii=False
            )
        )

        return {
            "model": modelo,
            "encoder": encoder,
            "metrics": metricas
        }
    @staticmethod
    def is_trained():
        """verifica se o modelo já foi treinado."""
        return (
            os.path.exists(TrainService.MODEL_PATH)
            and os.path.exists(TrainService.METRICS_PATH)
        )
        
    @staticmethod
    def load_model():
        """carrega o modelo treinado."""
        if not TrainService.is_trained():
            raise FileNotFoundError(
                "modelo ainda não foi treinado."
            )

        return joblib.load(TrainService.MODEL_PATH)
     
    @staticmethod
    def get_metrics():

        if not os.path.exists(TrainService.METRICS_PATH):
            return None

        with open(
            TrainService.METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)  

if __name__ == "__main__":
    TrainService.train()