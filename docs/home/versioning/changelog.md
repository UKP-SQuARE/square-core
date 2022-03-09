---
slug: versions
title: Changelog
---

# Changelog

## Version 0.0.1

**Datastores:**
* Added
    * Support for encoding and indexing in a very convenient way (using pip packages)
    Multi-gpu support for encoding with SBERT models. 
    * Tutorials for an easy understanding of datastores.

**Models:**
* Added 
  * ONNX models: BERT, Roberta, T5 and BART
  * Automated deployment of ONNX models
  * Improved the model management server and added API to update the parameters of deployed models. This makes it easier to use GPU inference.
* Fixed
  * Issues in the generation pipeline of adapter-transformers

**Explainability:**
* Add checklist tests for Commonsense QA

**UI:**
* Added
  * Landing page
  * Feedback page
  * Commonsense explainability data
* Fixed
  * When providing context on an open domain skill the context was visualized instead of the prediction documents
  Mobile landscape view used default safe area inserts


**Skills:**
* Added
  * documentation of skills, skill-manager, and skill-API
* Updated
  * Changes to .env file setup for better secrets management

**Documentation:**
* Added:
  * Local setup of SQuARE platform
* Updated
  * project README with the new additions
  * documentation website to align with the new changes
