import joblib
SYSTEM_STATES = [
    "normal",
    "baseline",
    "teste",
    "acelerando",
    "motor_desligado"
]

class PredictionService:

    def predict(sensor_json):

        model = joblib.load("ml/model.pkl")

        encoder = joblib.load("ml/label_encoder.pkl")

        X = montar_dataframe(sensor_json)

        pred = model.predict(X)

        return encoder.inverse_transform(pred)[0]