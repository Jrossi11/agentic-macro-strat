# 🌐 Agentic Supply & Demand Modeling 

Jacaranda Capital Partners is an event-driven, multi-agent AI system designed to detect, analyze, and model commodity supply and demand shocks before they are fully priced into the market. 

By continuously ingesting unstructured data from X (Twitter) and web search APIs, the system utilizes a specialized crew of Large Language Models (LLMs) to filter noise, extract fundamental catalysts (e.g., strikes, weather anomalies, geopolitical shifts), and translate them into structured trading signals.

---

## 🏗️ System Architecture

The pipeline is orchestrated using a multi-agent framework where specialized AI personas handle distinct steps of the data-to-alpha lifecycle.

### The Agents
* **📡 The Scout (Data Ingestion):** Continuously monitors targeted X lists, keywords, and scheduled web searches to catch breaking news regarding specific commodities.
* **🔎 The Analyst (Extraction):** Parses the Scout's raw feed, filters out spam/echo-chamber noise, and extracts concrete events into a strict JSON schema detailing the catalyst, impacted region, and severity.
* **🧮 The Quant (Modeling & Context):** Cross-references the Analyst's output with historical market data and past events (via RAG in a Vector Database) to update the internal supply/demand ledger. Then contrasting it against current market momentum and generates actionable alerts with confidence scores, routing them to a dashboard or webhook.
* 
---

## 🛠️ Tech Stack

* **Orchestration:** LangGraph 
* **LLMs:**  Gemini? Grok?
* **Data Sources:** X API (Pro), Tavily Web Search API, Yahoo Finance API ?
* **Storage:** ? 
  * *Market Data:*  ?
* **Data Validation:** ?

---
