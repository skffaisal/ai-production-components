This directory is to show the use of langfuse in an application, consider this as the root directory of buidling your applciations

--------


## Trace 

Trace is basically the complete execution of one logical request/workflow. ie 

Trace = one complete logical execution.

Observation = one measurable operation/step inside that execution.

```
TRACE
"What is our refund policy?"
│
├── Observation: input validation
│
├── Observation: query rewriting
│
├── Observation: retrieve documents
│
├── Generation: LLM call for answer
│
├── Observation: output validation
│
└── Observation: final response
```

eg2:
```
TRACE
request_id=abc123
│
├── OBSERVATION
│   input_guardrail
│
├── OBSERVATION
│   retrieve_documents
│
├── GENERATION
│   gpt-5.6
│
├── OBSERVATION
│   search_database
│
├── GENERATION
│   final_answer
│
└── OBSERVATION
    output_guardrail
```

| Concept         | Meaning                                                    |
| --------------- | ---------------------------------------------------------- |
| **Trace**       | Complete logical execution/request                         |
| **Observation** | A step/operation within the trace                          |
| **Generation**  | Observation representing an LLM/model call                 |
| **Span**        | Observation representing a general operation/workflow step |

and the observation ca be 

```
Trace
 └── Observations
       ├── Span
       ├── Generation
       ├── Event
       ├── Retriever
       ├── Agent
       └── Tool
```
Generation types from documentation:


 * event is the basic building block. An event is used to track discrete events in a trace.
 * span is the generic observation type for durations of units of work in a trace.
 * generation logs generations of AI models incl. prompts, token usage and costs.
 * agent decides on the application flow and can for example use tools with the guidance of a LLM.
 * tool represents a single action that does something, such as a function or API call (for example a weather API).
 * chain is a link between different application steps, like passing context from a retriever to a LLM call.
 * retriever represents a data-retrieval step that only looks something up rather than changing state, such as a call to a vector store, database, or other knowledge source.
 * evaluator represents functions that assess relevance/correctness/helpfulness of a LLM's outputs.
 * embedding is a call to a LLM to generate embeddings and can include model, token usage and costs
 * guardrail is a component that protects against malicious content or jailbreaks.


Custom prices needs to be defined if langfuse does not have the info of the price of model you are using, by going to Project Settings → Model Definitions


## Sessions

Langfuse recommends sessions for multi-turn conversations; each turn can be its own trace while the session groups them together.

Trace = one request/turn

Session = group of related requests/traces

```
Trace: One independent request.

Observation: An individual operation within a trace.

Session: Multiple related traces sharing a session ID.

User ID: Identifies the user across sessions.
```


## Prompt Management
from the local hosted : 3000 ui
prompt management -> prompts -> create