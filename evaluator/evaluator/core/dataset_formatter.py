import logging
from typing import Dict, List

from evaluator.models import ExtractiveDatasetSample, MultipleChoiceDatasetSample

logger = logging.getLogger(__name__)


class DatasetFormatter:
    def __init__(self) -> None:
        self.supported_skill_types = ["extractive-qa", "multiple-choice"]

    def format(self, dataset, dataset_metadata, sample_ids=None):
        if dataset_metadata["skill-type"] not in self.supported_skill_types:
            skill_type = dataset_metadata["skill-type"]
            raise ValueError(
                f"Evaluation of '{skill_type}' datasets is currently not supported. Currently supported: {self.supported_skill_types}"
            )

        if dataset_metadata["skill-type"] == "extractive-qa":
            dataset = self.__map_extractive_dataset(dataset_metadata, dataset)
        elif dataset_metadata["skill-type"] == "multiple-choice":
            dataset = self.__map_multiple_choice_dataset(dataset_metadata, dataset)

        # only get the correct samples (in the correct order) (TODO: optimize)
        if sample_ids is not None:
            samples = []
            for sample_id in sample_ids:
                for sample in dataset:
                    if sample["id"] == sample_id:
                        samples.append(sample)
                        break
            logger.debug(f"SAMPLES: {len(samples)}")
        else:
            samples = dataset
        return samples

    def __extract(self, row, field_name):
        try:
            field_names = field_name.split(".")
            candidate = row[field_names[0]]
            if len(field_names) > 1:  # nested
                candidate = row[field_names[0]][field_names[1]]
        except KeyError:
            candidate = False
        return candidate

    def __map_extractive_dataset(self, dataset_metadata, dataset):
        extractive_qa_dataset = []
        for sample in dataset:
            # get a list of answer-texts and a list of answer-starts
            answer_texts = self.__extract(
                sample, dataset_metadata["mapping"]["answer-text-column"]
            )
            extractive_qa_dataset.append(
                ExtractiveDatasetSample(
                    id=sample[dataset_metadata["mapping"]["id-column"]],
                    question=sample[dataset_metadata["mapping"]["question-column"]],
                    context=sample[dataset_metadata["mapping"]["context-column"]],
                    answers=answer_texts,
                ).dict()
            )
        logger.debug(
            f"Formatted extractive-qa samples {extractive_qa_dataset[0]}, {extractive_qa_dataset[1]}, {extractive_qa_dataset[2]}"
        )
        return extractive_qa_dataset

    def __map_multiple_choice_dataset(self, dataset_metadata, dataset):
        multiple_choice_qa_dataset = []
        for sample in dataset:
            choices = self.__get_choices_as_list(sample, dataset_metadata)
            multiple_choice_qa_dataset.append(
                MultipleChoiceDatasetSample(
                    id=sample[dataset_metadata["mapping"]["id-column"]],
                    question=sample[dataset_metadata["mapping"]["question-column"]],
                    choices=choices,
                    answer_index=self.__get_answer_index(
                        sample, dataset_metadata, choices
                    ),
                ).dict()
            )
        logger.debug(
            f"Formatted extractive-qa samples {multiple_choice_qa_dataset[0]}, {multiple_choice_qa_dataset[1]}, {multiple_choice_qa_dataset[2]}"
        )
        return multiple_choice_qa_dataset

    def __get_choices_as_list(self, sample, dataset_metadata) -> List[str]:
        """
        Extracts all the answer-choices from the sample and returns them as a list.

        Args:
            sample (dict): Sample from the dataset.
            dataset_metadata (dict): Metadata about the dataset that the sample is from.

        Returns:
        :int: List of answer-choices.
        """

        choices = []
        choices_column_names = dataset_metadata["mapping"]["choices-columns"]

        if len(choices_column_names) == 1:
            # there is one column containing a dict, with one dict-entry containing a list of choices
            choices = self.__extract(sample, choices_column_names[0])
        elif len(choices_column_names) > 1:
            # there is one separate column per choice
            choices = [sample[column_name] for column_name in choices_column_names]
        else:
            raise HTTPException(400, "Cannot map choices of multiple-choice dataset")

        return choices

    def __get_answer_index(self, sample, dataset_metadata, choices) -> int:
        """
        Maps each choice to a key as specified in the datasets metadata and then returns the index of the correct choice.
        If no mapping is specified in the metadata, numeric keys are assumed (choice1 = 0, choice2 = 1, ...)

        Args:
            sample (dict): Sample from the dataset.
            dataset_metadata (dict): Metadata about the dataset that the sample is from.
            choices (List[str]): List of answer-choices.

        Returns:
        :int: Index of the choice that is the correct answer.
        """
        answer_key = self.__extract(
            sample, dataset_metadata["mapping"]["answer-index-column"]
        )
        if dataset_metadata["mapping"]["choices-key-mapping-column"] is None:
            # there is no key-mapping specified, so we assume numeric keys
            answer_keys = range(0, len(choices), 1)
        else:
            answer_keys = self.__extract(
                sample, dataset_metadata["mapping"]["choices-key-mapping-column"]
            )
        # get the position of the answer-key from the key-mapping
        answer_index = answer_keys.index(answer_key)
        return answer_index
