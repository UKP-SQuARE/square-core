import logging
from typing import Dict, List

from evaluator.app.models import (
    SUPPORTED_SKILL_TYPES,
    DatasetMetadata,
    ExtractiveDatasetSample,
    ExtractiveQADatasetMapping,
    MultipleChoiceDatasetSample,
    MultipleChoiceQADatasetMapping,
)

logger = logging.getLogger(__name__)


class DatasetFormatter:
    def __init__(self) -> None:
        self.supported_skill_types = list(SUPPORTED_SKILL_TYPES.keys())

    def format(self, dataset, dataset_metadata: DatasetMetadata, sample_ids=None):
        """
        Formats the given dataset into a generic (per skill_type) format.

        Args:
            dataset (:class:`Dataset` or :class:`DatasetDict`:): Dataset from huggingface.
            dataset_metadata (:class:`DatasetMetadata`): Metadata about the dataset.
            sample_ids (List[str]): Optional list of sample-ids. When specified, only samples with the respective ids will be returned.
                                    Otherwise all samples in the dataset will be returned.
                                    The returned samples will be in the same order as the passed sample-ids.

        Returns: List of samples in the dataset in an universal format depending on the datasets skill_type.
        """

        if dataset_metadata.skill_type not in self.supported_skill_types:
            skill_type = dataset_metadata.skill_type
            raise ValueError(
                f"Evaluation of '{skill_type}' datasets is currently not supported. Currently supported: {self.supported_skill_types}"
            )

        if dataset_metadata.skill_type == "extractive-qa":
            samples = self.__map_extractive_dataset(dataset, dataset_metadata.mapping)
        elif dataset_metadata.skill_type == "multiple-choice":
            samples = self.__map_multiple_choice_dataset(
                dataset, dataset_metadata.mapping
            )

        if sample_ids is not None:
            samples = self.__get_samples_subset(samples, sample_ids)

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

    def __get_samples_subset(self, samples, sample_ids):
        """
        Retrieves only the specified subset of samples from the given dataset.

        Args:
            samples (List[]): List of samples in generic dataset-format.
            sample_ids (List[str]): A list of sample-ids. Only samples with the respective ids will be returned.
                                    The returned samples will be in the same order as the passed sample-ids.

        Returns: List of samples from the passed samples that are included in sample_ids.
        """
        subset = []
        for sample_id in sample_ids:
            for sample in samples:
                if sample["id"] == sample_id:
                    subset.append(sample)
                    break
        return subset

    def __map_extractive_dataset(self, dataset, mapping: ExtractiveQADatasetMapping):
        """
        Takes an extractive-qa dataset and maps it to a list consisting of ExtractiveDatasetSample.

        Args:
            dataset (:class:`Dataset` or :class:`DatasetDict`:): Extractive-qa dataset from huggingface.
            mapping (:class:`ExtractiveQADatasetMapping`): Mapping for the dataset.

        Returns:
        :List[ExtractiveDatasetSample]: List of samples in ExtractiveDatasetSample format.
        """
        extractive_qa_dataset = [
            ExtractiveDatasetSample(
                id=sample[mapping.id_column],
                question=sample[mapping.question_column],
                context=sample[mapping.context_column],
                answers=self.__get_value(sample, mapping.answers_column),
            ).dict()
            for sample in dataset
        ]
        return extractive_qa_dataset

    def __map_multiple_choice_dataset(
        self, dataset, mapping: MultipleChoiceQADatasetMapping
    ):
        """
        Takes a multiple-choice dataset and maps it to a list consisting of MultipleChoiceDatasetSample.

        Args:
            dataset (:class:`Dataset` or :class:`DatasetDict`:): Multiple-choice dataset from huggingface.
            mapping (:class:`MultipleChoiceQADatasetMapping`): Mapping for the dataset.

        Returns:
        :List[MultipleChoiceDatasetSample]: List of samples in MultipleChoiceDatasetSample format.
        """
        multiple_choice_dataset = []
        for sample in dataset:
            choices = self.__get_choices_as_list(sample, mapping.choices_columns)
            multiple_choice_dataset.append(
                MultipleChoiceDatasetSample(
                    id=sample[mapping.id_column],
                    question=sample[mapping.question_column],
                    choices=choices,
                    answer_index=self.__get_answer_index(sample, mapping, choices),
                ).dict()
            )
        return multiple_choice_dataset

    def __get_choices_as_list(
        self, sample, choices_column_names: List[str]
    ) -> List[str]:
        """
        Extracts all the answer-choices from the sample and returns them as a list.

        Args:
            sample (dict): Sample from the dataset.
            choices_column_names (List[str]): Names of the columns.

        Returns:
        :List[str]: List of answer-choices.
        """

        choices = []

        if len(choices_column_names) == 1:
            # there is one column containing a dict, with one dict-entry containing a list of choices
            choices = self.__get_value(sample, choices_column_names[0])
        elif len(choices_column_names) > 1:
            # there is one separate column per choice
            choices = [sample[column_name] for column_name in choices_column_names]
        else:
            raise ValueError("Cannot map choices of multiple-choice dataset")

        return choices

    def __get_answer_index(
        self, sample, mapping: MultipleChoiceQADatasetMapping, choices
    ) -> int:
        """
        Maps each choice to a key as specified in the datasets metadata and then returns the index of the correct choice.
        If no mapping is specified in the metadata, numeric keys are assumed (choice1 = 0, choice2 = 1, ...)

        Args:
            sample (dict): Sample from the dataset.
            mapping (:class:`MultipleChoiceQADatasetMapping`): Mapping for the dataset that the sample is from.
            choices (List[str]): List of answer-choices.

        Returns:
        :int: Index of the choice that is the correct answer.
        """
        answer_key = self.__get_value(sample, mapping.answer_index_column)
        if mapping.choices_key_mapping_column is None:
            # there is no key-mapping specified, so we assume numeric keys
            answer_keys = range(0, len(choices), 1)
        else:
            answer_keys = self.__get_value(sample, mapping.choices_key_mapping_column)
        # get the position of the answer-key from the key-mapping
        answer_index = answer_keys.index(answer_key)
        return answer_index
