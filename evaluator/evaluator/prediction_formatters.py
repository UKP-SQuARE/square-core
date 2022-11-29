class PredictionFormatter:
    def __init__(self):
        self._formatters = {
            "squad": SquadPredictionFormatter(),
            "squad_v2": SquadV2PredictionFormatter(),
        }

    def format(self, metric_name, predictions):
        formatter = self._formatters.get(metric_name)
        if not formatter:
            formatter = SimplePredictionFormatter()
        return formatter.format(predictions)


class SimplePredictionFormatter:
    def format(self, predictions):
        return list(map(self.map, predictions))

    def map(self, prediction):
        return prediction["prediction"].output


class SquadPredictionFormatter(SimplePredictionFormatter):
    def map(self, prediction):
        return {
            "id": prediction["id"],
            "prediction_text": prediction["prediction"].output,
        }


class SquadV2PredictionFormatter(SimplePredictionFormatter):
    def map(self, prediction):
        return {
            "id": prediction["id"],
            "prediction_text": prediction["prediction"].output,
            "no_answer_probability": 0.0,
        }
