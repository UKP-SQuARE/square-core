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
    def __init__(self):
        self.sample_ids = []

    def format(self, predictions):
        return list(map(self.map, predictions)), self.sample_ids

    def map(self, prediction):
        self.sample_ids.append(prediction.id)
        return prediction.output


class SquadPredictionFormatter(SimplePredictionFormatter):
    def map(self, prediction):
        self.sample_ids.append(prediction.id)
        return {
            "id": prediction.id,
            "prediction_text": prediction.output,
        }


class SquadV2PredictionFormatter(SimplePredictionFormatter):
    no_answer_found = "No answer found."

    def map(self, prediction):
        self.sample_ids.append(prediction.id)
        return {
            "id": prediction.id,
            "prediction_text": prediction.output,
            "no_answer_probability": prediction.output_score
            if prediction.output == self.no_answer_found
            else 0.0,
        }
