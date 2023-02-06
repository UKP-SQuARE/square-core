import logging

logger = logging.getLogger(__name__)


class MetricFormattingError(Exception):
    """
    Raised when there is an error during formatting data into metric format.
    This could e.g. be the case when trying to apply metrics to datasets in combinations that are not supported.
    """

    def __init__(self, metric_name: str, references, e: Exception) -> None:
        msg = f"Error while converting data into format for {metric_name}-metric. Check the dataset-mapping! Maybe the selected dataset cannot be evaluated on the given metric. Error: {e!r}. Sample reference: {references[0]!r}"
        super().__init__(msg)


class Formatter:
    def __init__(self):
        self._formatters = {
            "squad": SquadFormatter(),
            "squad_v2": SquadV2Formatter(),
        }

    def __get_formatter(self, metric_name):
        formatter = self._formatters.get(metric_name)
        if not formatter:
            formatter = SimpleFormatter()
        return formatter

    def format_predictions(self, metric_name, predictions):
        return self.__get_formatter(metric_name).format_predictions(predictions)

    def format_references(self, metric_name, references):
        try:
            return self.__get_formatter(metric_name).format_references(references)
        except KeyError as e:
            raise MetricFormattingError(metric_name, references, e)


class SimpleFormatter:
    def __init__(self):
        self.sample_ids = []

    def format_predictions(self, predictions):
        return list(map(self._map_predictions, predictions)), self.sample_ids

    def format_references(self, references):
        return list(map(self._map_reference, references))

    def _map_predictions(self, prediction):
        self.sample_ids.append(prediction.id)
        return prediction.output

    def _map_reference(self, reference):
        return reference["choices"][reference["answer_index"]]


class SquadFormatter(SimpleFormatter):
    def _map_predictions(self, prediction):
        self.sample_ids.append(prediction.id)
        return {
            "id": prediction.id,
            "prediction_text": prediction.output,
        }

    def _map_reference(self, reference):
        return {
            "id": reference["id"],
            "answers": [
                {"text": answer, "answer_start": 0} for answer in reference["answers"]
            ],
        }


class SquadV2Formatter(SquadFormatter):
    no_answer_found = "No answer found."

    def _map_predictions(self, prediction):
        self.sample_ids.append(prediction.id)
        return {
            "id": prediction.id,
            "prediction_text": prediction.output,
            "no_answer_probability": prediction.output_score
            if prediction.output == self.no_answer_found
            else 0.0,
        }
