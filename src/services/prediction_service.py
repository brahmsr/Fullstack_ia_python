import joblib
import pandas as pd

from services.train_service import TrainService
from services.fault_labels import is_state


class PredictionService:

    def __init__(self):
        
        

        data = TrainService.load_model()

        self.model = data["model"]
        self.encoder = data["encoder"]
        self.features = data["features"]

    def predict(self, sensor_data):
        faltando = set(self.features) - set(sensor_data.keys())

        if faltando:
            raise ValueError(
                f"Features ausentes: {sorted(faltando)}"
            )

        df = pd.DataFrame([sensor_data])

        df = df[self.features]

        pred = self.model.predict(df)[0]

        probs = self.model.predict_proba(df)[0]

        fault = self.encoder.inverse_transform([pred])[0]

        return {

            "fault": fault,

            "is_state": is_state(fault),

            "confidence": float(max(probs)),

            "probabilities": {

                classe: float(prob)

                for classe, prob in zip(
                    self.encoder.classes_,
                    probs
                )
            }

        }