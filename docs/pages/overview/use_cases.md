# Use Cases

- <b>Question-Answering:</b> Central location to store and ask question with pretrained *skills*, each skill created to handle a specific questions-answering task (domain-specific e.g covid19, biomedical, ... or factoid question that based on Freebase knowledge graph). A user can implement skill model on their own or in more simple way is to use third-party API such as t5 or elli5 from huggingface.
- <b>Semantic search:</b> Query from the plethora of skills deployed on our platform.
- <b>Deploy new skills:</b> Apart from the skills that are already published by other users, develop your own skill as REST API, deploy it and publish its endpoints on square. 
- <b>Explainability:</b> Get model explanations via [Checklist](https://github.com/marcotcr/checklist). Only available for selected models but we are continuously working
to bring you more.
