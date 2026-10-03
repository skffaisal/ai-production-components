# Presidio 

### used for PII detection and de-identification
        
can be used in 

* Texts 
* Images 
* Semi/Structured data

```
uv run python -m spacy download en_core_web_lg
```

spacy.load('en_core_web_lg') -> but here precidio is using this spacy internally

* pre-trained model package is being downloaded
* this is used for NER (named entity recognition) 
* transformers based also can be used using "pip install "presidio-analyzer[transformers]""
* other than spacy, presidio can also be used with alternative NLP engines , like stanza, Hugging face models etc


in production
```
uv add "https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl"

```

This saves the model directly into your pyproject.toml. The next time you or someone else runs uv sync, the model downloads automatically without needing a secondary setup script.

Its also available as a docker service 



Presidio
├── Analyzer                         
├── Application result model         
├── Detection policy                 
├── Pattern custom recognizer        
├── Context-aware recognizer         
├── Advanced/custom recognizers      
├── Anonymization                    
├── Policy engine                    
├── Failure/security behavior        
├── Testing/evaluation               
└── Operational production   




### References: 

```
https://presidio.dataprivacystack.org/getting_started/

https://blog1.neuralengineer.org/microsoft-presidio-an-engineers-introduction-to-pii-detection-and-de-identification-6a7c3fed6e50



```