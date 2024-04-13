![logo](carefirst/experiments/02_demos/images/carefirst_banner.png "CareFirst")

## Capstone: CAREFirst - Companion AI Response and Emergency First-aid

This repository holds the codebase for a capstone project created by students in the UC Berkeley Master of Information and Data Science degree.

**Our website** - [CareFirst](https://rmarin.mids255.com/)

**The Team** - Charlie Glass, Bronte Pendergast, Ambika Gupta, Ricardo Marin, Jessica Stockham

### Problem & Motivation

People seeking information on their mild to serious health issues are often caught between two extremes. They are either overloaded with information from scouring various medical websites or journals with mixed/ambiguous answers, or they are under-observed or treated by busy hospitals and urgent cares. Built as a conversational AI chatbot, CareFirst provides a singular, medically-sourced solution that can guide users on what the medical issue may be, how it may be treated, and where they should go for medical attention. 
<br />
Our goal is always the same: help you find the best possible solution to your first-aid needs. That's why we don't just rely on AI conversation. We encourage feedback from our users and our very own verified medical professionals. See transparent feedback on CareFirst AI on our website Model page.

### Data Science Approach and Impact

CareFirst is a Retrieval Augmented Generation app with health information backed by Red Cross Guidelines: a trusted medical source that we parse through so you don't have to!

Our impact as an AI application is guided by three key principles:

* Trust - Opposed to asking ChatGPT, an AI solution with trusted and transparent sources that provide the verified medical advice to use when generating a response.
* Communication - The AI proactively asks the user customized follow-up questions. Built with a knowledge graph of medical scenarios that we know need to be mapped to the user’s question before we can respond.
* Safety - Guardrails powered by NeMo Guardrails and GPT3.5 to detect potential emergency situations.

### Evaluation

Our AI application is evaluated across three measures: technical metrics, Subject Matter Experts (SMEs) feedback and User feedback.

**Metrics:**

We experimented with three different Large Language Models in the development of the CareFirst AI application and compared to the baseline answers that GPT3.5 would provide based on a large sample of first-aid intents and the associated reference answers.

* Carefirst, implemented with GPT3.5, has the highest semantic similarity with the reference answer (Sentence BERT - 0.7)
* Carefirst, implemented with GPT3.5, has the most sequences of similar words to the reference answer (ROUGE-L - 0.45)
* 77% of Carefirst’s answers are retrieved from the same source as the reference answer.

Our baseline GPT3.5 answers were the furthest from our reference answers, with CareFirst implemented with Gemma-7b-it and Mistral-7B-Instruct-v0.2 performing better than the baseline but with lower performance than CareFirst implemented with GPT3.5 

**Subject Matter Experts:**

4 board-certified physicians practicing general surgery, trauma surgery, and internal medicine and 1 licensed Emergency Medical Technician (EMT) reviewed CareFirst responses.

Overall, CareFirst was rated a 7.2 for trustworthiness; reviewing on a scale of 0 to 10 the correctness of the information provided in the response. CareFirst was rated a 6.7 for comprehensiveness; reviewing on a scale of 0 to 10 the completeness of the information provided in the response.

Feedback received included:
* CareFirst appropriately asks for additional symptoms as needed
* CareFirst accurately provides guidelines for when and where to seek further care
* CareFirst can provide more specialized care with further triaging and user profiling

### Acknowledgements

Thank you for the advice and support from Professor Mark Butler, Professor James Winegar, Professor Korin Reid, Professor Fred Nugen. 
Thank you for the user testing from SMEs, friends, and family.