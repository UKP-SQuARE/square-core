from pydantic import BaseModel, Field


class ChecklistTests(BaseModel):
    qa_type: str
    test_type: str
    capability: str
    test_name: str
    test_name_description: str
    test_type_description: str
    capability_description: str
    test_cases: list

    class Config:
        schema_extra = {
            "example": {
                "qa_type": "span-extraction",
                "test_type": "MFT",
                "capability": "Vocabulary",
                "test_name": "A is COMP than B. Who is more / less COMP??",
                "test_name_description": "Compare person A and person B with different comparative adjective " \
                                         "and test's models ability to understand the comparative words",
                "test_type_description": "MFT stands for Minimum Functionality Test. This testing type is " \
                                         "inspired from unit testing of software engineering. For this type of " \
                                         "testing precise and small testing datasets are created and the models " \
                                         "are tested on that particular test set. MFTs are useful particularly " \
                                         "for detecting when models use alternative approaches to handle " \
                                         "complicated inputs without actually knowing the inside out of the " \
                                         "capability. For MFT test cases, labeled test set is required.",
                "capability_description": "This capability tests whether a model has necessary vocabulary and " \
                                          "whether it has the ability to handle the importance of different words.",
                "test_cases": [
                    {
                        "context": "Caroline is nicer than Marie.",
                        "question": "Who is less nice?",
                        "answer": "Marie"
                    }, ...
                ]
            }
        }


class ChecklistResults(BaseModel):
    skill_id: str
    test_type: str
    capability: str
    test_name: str
    question: str
    context: str
    answer: str
    prediction: str
    success: bool

    class Config:
        schema_extra = {
            "example": {
                "skill_id": "61a9f56c35adbbf1f2433072",
                "test_type": "MFT",
                "capability": "Vocabulary",
                "test_name": "A is COMP than B. Who is more / less COMP??",
                "question": "Who is less nice?",
                "context": "Caroline is nicer than Marie.",
                "answer": "Marie",
                "prediction": "Marie",
                "success": True
            }
        }
