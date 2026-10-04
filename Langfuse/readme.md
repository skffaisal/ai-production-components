get self hosted docker compose version from : https://langfuse.com/self-hosting/deployment/docker-compose

same docker-compose.yml is copied here 

then docker compose up -d

Thats it, now can can create a project by going into http://localhost:3000/

get 
```
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_BASE_URL=http://localhost:3000
```

and start using this in the projects you are building 


# Checklist 1

Phase 1: Tracing fundamentals
Install the SDK, trace an LLM call, and read the trace in the UI.
Understand traces, observations, generations, spans, sessions, and users.
Add metadata, tags, user_id, and session_id, and use the integrations for OpenAI, LangChain, or LlamaIndex.
Trace a full agent workflow (retrieval, tool calls, nested steps), not just single LLM calls.
Check that token usage and cost are tracked correctly, including for models Langfuse doesn't know.

Done when: you can take any bad response from your app and find exactly which step caused it.

Phase 2: Prompt management
Move prompts out of your code into Langfuse and link prompt versions to traces.
Use labels such as production and staging. Applications fetch labeled versions at runtime, so a prompt change needs no code change or redeploy. 
langfuse
Handle caching and fallbacks so a Langfuse outage doesn't break your app.
Iterate on prompts in the Playground, and replay a traced call there.

Done when: you can roll out and roll back a prompt change without touching code, and tell whether version 5 beat version 4.

Phase 3: Scores and evaluation methods

This is the core skill.

User feedback: thumbs up/down sent as scores.
Manual review: annotation queues, where reviewers work through traces and label them.
LLM-as-a-judge: write a good judge prompt, run it on live traffic, and inspect the judge's own execution trace when it misbehaves.
Code evaluators: deterministic checks like format, length, regex, and schema validation. These have been generally available since May 28, 2026, and run on live observations. 
langfuse
Understand the score types (numeric, categorical, boolean) and score analysis, and validate your judge against human labels.

Done when: you have at least three different evaluators running on one app, and you can show how closely your LLM judge agrees with human reviewers.

Phase 4: Datasets
Build datasets from three sources: manual items, CSV import, and production traces. "Add to dataset" works on any production observation, and filtered observations can be batch-added. 
langfuse
Cover edge cases and failures, not just happy paths.
Organize datasets in folders, and use dataset versioning. You can fetch a dataset as it existed at a given timestamp and run experiments on it for reproducibility. 
langfuse

Done when: you have a dataset of 50+ real, representative cases that grows from production failures.

Phase 5: Experiments
Experiments are now a top-level concept alongside datasets (this needs v4). They run with or without datasets, and you can compare runs and track progress over time. 
langfuse
Run experiments via the SDK (concurrent execution, automatic tracing, custom evaluators) and via the UI.
Compare prompts, models, and parameters (temperature, chunk size, retriever settings) side by side.
Use structured outputs in experiments and read the results with score analysis.

Done when: you can say "this change improved quality from X to Y, costs Z% more, and is N ms slower," with data.

Phase 6: Production monitoring
Build custom dashboards for latency, cost, quality scores, and error rates, sliced by model, prompt version, user, or tag.
Set up alerts.
Run online evaluation on a sample of live traffic and watch for drift.
Use sessions to evaluate multi-turn conversations.
Handle sampling, masking of sensitive data (PII), and environments (dev/staging/prod).

Done when: a quality regression in production would reach you before a user complains.

Phase 7: CI/CD and automation
The langfuse/experiment-action GitHub Action runs experiments in CI/CD and can block changes based on evaluation results. Gate your prompt or code changes on eval scores. 
langfuse
Use the public API, the Langfuse CLI, and the Agent Skill. The CLI reads and writes traces, prompts, datasets, and scores from the terminal, and the Agent Skill encodes Langfuse's own best practices. 
langfuse
Export data for analysis or fine-tuning datasets.

Done when: a pull request that makes your app worse fails automatically.

Phase 8: Deployment and enterprise
Self-host with Docker Compose, then learn the Kubernetes/Helm architecture. Langfuse's stack includes ClickHouse, Postgres, Redis, and S3-compatible storage.
Configure SSO, projects and organizations, and API key management.
Know the licensing split. Core Langfuse is MIT-licensed, and the optional Enterprise license adds project-level RBAC, audit logs, and data retention policies. 
langfuse
Think through data residency, compliance, retention, and cost at scale.

Done when: you can explain to a security team how your Langfuse deployment handles their data.

Phase 9: OpenTelemetry link-up

Send traces from a second service into the same Langfuse trace using context propagation.
Ingest from OTel-based instrumentation libraries, and export to another backend.
Capstone project

Build one app that uses every phase: a RAG or agent app with prompts in Langfuse, three evaluators, a production-sourced dataset, CI-gated experiments, a dashboard with alerts, and a self-hosted deployment. Write a short README on what failed, what you measured, and what you changed. That project is what you show employers.

# Checklist 2

0. Architecture / Data Model
1. Python SDK v4
2. Instrumentation
3. Trace Design
4. LLM Observability
5. Framework Integrations
6. Prompt Management
7. RAG Observability
8. Agents / Tools
9. Scores
10. Evaluation
11. LLM-as-a-Judge
12. Code Evaluators
13. Datasets
14. Experiments
15. Online Evaluation
16. Human Evaluation
17. User Feedback
18. Metrics / Dashboards
19. Alerts
20. Sampling / Performance
21. Privacy / Masking
22. Security Observability
23. Releases / Versioning
24. API / Data Platform
25. CLI / MCP awareness
26. RBAC / Organizations / Projects
27. Authentication / SSO
28. Retention / Lifecycle
29. Self-hosted Architecture
30. Docker Compose
31. Production Storage
32. Security / HTTPS / Secrets
33. Backups / DR
34. Scaling / HA
35. Kubernetes / Helm
36. Upgrades
37. Langfuse platform monitoring
38. Incident debugging
39. CI/CD evaluation gates
40. Final end-to-end production application




# Resources 

```
https://langfuse.com/academy


```