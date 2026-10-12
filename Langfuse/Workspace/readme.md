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

you can create multiple prompts in the lanfuse ui , test it in the plaground then use it in code 

multiple versions will be creted , but the version with label production will be imported in code

now we can trace generations linked to a particular prompt in observability

The default cache TTL is 60 seconds, we can chnage it in the code if wanted 

## Score

A score is a quality judgment attached to a trace, observation, or session.

The four score types


| Type          | Example                                     | When to use it                              |
| ------------- | ------------------------------------------- | ------------------------------------------- |
| `NUMERIC`     | `0.9`                                       | A relevance or quality rating               |
| `CATEGORICAL` | `"correct"`                                 | A classification from predefined categories |
| `BOOLEAN`     | `1` or `0`                                  | Pass/fail checks                            |
| `TEXT`        | `"The answer omitted an important detail."` | Qualitative reviewer notes                  |



Manual Scoring Interface :

in Observabilility --> tracing -> any observation--> Annotation --> Add Score

but first Score Config is required

Add Score --> Add Score Config

then eg:


| Field       | Value                                                       |
| ----------- | ----------------------------------------------------------- |
| Name        | `answer_quality`                                            |
| Data type   | `CATEGORICAL`                                               |
| Categories  | `good`, `partially_correct`, `incorrect`                    |
| Description | `Human assessment of the overall quality of an AI response` |


you can also later go to Score settings and change the settings if needed

You should be able to select answer_quality and assign one of the three categories for each observation

User Feedback:

| Field       | Value                                                     |
| ----------- | --------------------------------------------------------- |
| Name        | `user_feedback`                                           |
| Data type   | `BOOLEAN`                                                 |
| Description | `End-user feedback on whether an AI response was helpful` |

after the 12_user_feedback_test.py code is run, the score is stored in lanfuse, you can go and check in the tracing.







Annotation Queues are designed for structured human review: reviewers work through a collection of traces, apply consistent score configurations, and record judgments. Those human judgments can later help validate the LLM judge