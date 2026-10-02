• LLM01: Prompt Injection – Attackers manipulate user inputs or external data sources to make the model override its original instructions or safety rules.

• LLM02: Sensitive Information Disclosure – The LLM unintentionally leaks confidential, proprietary, or private data through its responses.

• LLM03: Supply Chain Vulnerabilities – Compromised third-party components, vulnerable pre-trained models, tainted datasets, or insecure plugins put the system at risk.

• LLM04: Data and Model Poisoning – Attackers corrupt pre-training data, fine-tuning data, or embeddings to introduce hidden backdoors, biases, or vulnerabilities.

• LLM05: Improper Output Handling – Downstream components accept the LLM's raw output without proper validation or sanitization, leading to secondary injection or remote code execution.

• LLM06: Excessive Agency – An LLM-based agent is given too much autonomy, permissions, or tool-access (like executing code or deleting files), letting attackers trigger damaging actions.

• LLM07: System Prompt Leakage – Attackers use jailbreaking or smart prompting to trick the model into revealing its hidden system instructions or developer prompts.

• LLM08: Vector and Embedding Weaknesses – Flaws in vector databases or embedding generation allow data manipulation, unauthorized data retrieval, or system bypasses.

• LLM09: Misinformation – The model presents false, fabricated, or hallucinated information as absolute fact, which users or automated systems trust blindly.

• LLM10: Unbounded Consumption – Attackers trigger resource-heavy operations or infinite loops that drain system compute, token budgets, or cause a denial of service (DoS).



you need impliment defense in depth architecture for guardrails