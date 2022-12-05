import logging
from typing import Dict, List

from evaluator.models import ExtractiveDatasetSample, MultipleChoiceDatasetSample

logger = logging.getLogger(__name__)


class DatasetFormatter:
    def __init__(self) -> None:
        self.supported_skill_types = ["extractive-qa", "multiple-choice"]

    def format(self, dataset, dataset_metadata, sample_ids=None):
        """
        Formats the given dataset into a generic (per skill-type) format.

        Args:
            dataset_name (str): Name of the dataset on huggingface.
            dataset_metadata (dict): Metadata about the dataset.
            sample_ids (List[str]): Optional list of sample-ids. When specified, only samples with the respective ids will be returned.
                                    Otherwise all samples in the dataset will be returned.
                                    The returned samples will be in the same order as the passed sample-ids.

        Returns: List of samples in the dataset in an universal format depending on the datasets skill-type.
        """

        if dataset_metadata["skill-type"] not in self.supported_skill_types:
            skill_type = dataset_metadata["skill-type"]
            raise ValueError(
                f"Evaluation of '{skill_type}' datasets is currently not supported. Currently supported: {self.supported_skill_types}"
            )

        if dataset_metadata["skill-type"] == "extractive-qa":
            dataset = self.__map_extractive_dataset(dataset_metadata, dataset)
        elif dataset_metadata["skill-type"] == "multiple-choice":
            dataset = self.__map_multiple_choice_dataset(dataset_metadata, dataset)

        if sample_ids is not None:
            samples = self.__get_samples_subset(dataset, sample_ids)
        else:
            samples = dataset
        return samples

    def __get_value(self, obj, field_name):
        """
        Extracts the value of the given field name from the given object.

        Returns: The value of specified field on the object. False if the field does not exist.
        """
        value = obj
        try:
            for field_name in field_name.split("."):
                value = value[field_name]
        except KeyError:
            value = False
        return value

    def __get_samples_subset(self, dataset, sample_ids):
        """
        Retrieves only the specified subset of samples from the given dataset.

        Args:
            dataset (List[]): Dataset in generic format.
            sample_ids (List[str]): Metadata about the dataset.
            sample_ids (List[str]): A list of sample-ids. Only samples with the respective ids will be returned.
                                    The returned samples will be in the same order as the passed sample-ids.

        Returns: List of samples from the dataset that are included in sample_ids.
        """
        subset = []
        for sample_id in sample_ids:
            for sample in dataset:
                if sample["id"] == sample_id:
                    subset.append(sample)
                    break
        return subset

    def __map_extractive_dataset(self, dataset_metadata, dataset):
        """
        Takes an extractive-qa dataset and maps it to a list consisting of ExtractiveDatasetSample.

        Args:
            dataset_metadata (dict): Metadata about the dataset.
            dataset: A multiple-choice dataset.

        Returns:
        :List[ExtractiveDatasetSample]: List of samples in ExtractiveDatasetSample format.
        """
        extractive_qa_dataset = [
            ExtractiveDatasetSample(
                id=sample[dataset_metadata["mapping"]["id-column"]],
                question=sample[dataset_metadata["mapping"]["question-column"]],
                context=sample[dataset_metadata["mapping"]["context-column"]],
                answers=self.__get_value(
                    sample, dataset_metadata["mapping"]["answer-text-column"]
                ),
            ).dict()
            for sample in dataset
        ]
        return extractive_qa_dataset

    def __map_multiple_choice_dataset(self, dataset_metadata, dataset):
        """
        Takes a multiple-choice dataset and maps it to a list consisting of MultipleChoiceDatasetSample.

        Args:
            dataset_metadata (dict): Metadata about the dataset.
            dataset: A multiple-choice dataset.

        Returns:
        :List[MultipleChoiceDatasetSample]: List of samples in MultipleChoiceDatasetSample format.
        """
        multiple_choice_dataset = []
        for sample in dataset:
            choices = self.__get_choices_as_list(sample, dataset_metadata)
            multiple_choice_dataset.append(
                MultipleChoiceDatasetSample(
                    id=sample[dataset_metadata["mapping"]["id-column"]],
                    question=sample[dataset_metadata["mapping"]["question-column"]],
                    choices=choices,
                    answer_index=self.__get_answer_index(
                        sample, dataset_metadata, choices
                    ),
                ).dict()
            )
        return multiple_choice_dataset

    def __get_choices_as_list(self, sample, dataset_metadata) -> List[str]:
        """
        Extracts all the answer-choices from the sample and returns them as a list.

        Args:
            sample (dict): Sample from the dataset.
            dataset_metadata (dict): Metadata about the dataset that the sample is from.

        Returns:
        :List[str]: List of answer-choices.
        """

        choices = []
        choices_column_names = dataset_metadata["mapping"]["choices-columns"]

        if len(choices_column_names) == 1:
            # there is one column containing a dict, with one dict-entry containing a list of choices
            choices = self.__get_value(sample, choices_column_names[0])
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
        answer_key = self.__get_value(
            sample, dataset_metadata["mapping"]["answer-index-column"]
        )
        if dataset_metadata["mapping"]["choices-key-mapping-column"] is None:
            # there is no key-mapping specified, so we assume numeric keys
            answer_keys = range(0, len(choices), 1)
        else:
            answer_keys = self.__get_value(
                sample, dataset_metadata["mapping"]["choices-key-mapping-column"]
            )
        # get the position of the answer-key from the key-mapping
        answer_index = answer_keys.index(answer_key)
        return answer_index
