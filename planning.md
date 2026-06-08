# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This project is essentially a searchable guide to NYU professor reviews that draws on student reviews from Rate My Professor across 10 professors from departments of Accounting, Economics, Statistics, English, Math, History, and Nutrition. While the information technically exists online, it's scattered across a myriad of individual professor pages, with no way to ask cross cutting questions like "which accounting professor has exams that mimics the practice exams" or "which prof are academically challenging" unless you read through hundreds of reviews, which would still require you to manually piece together an answer. A RAG system would take the collective student knowledge and turn it into something instantly queryable, generating cited answers based on real student experiences rather than from official university descriptions.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Simon Bowmaker — Economics, NYU Stern. 70 reviews. | ratemyprofessors.com/professor/343380 |
| 2 | Rate My Professors | Gerald McIntyre — Economics, NYU. 107 reviews. | ratemyprofessors.com/professor/228513 |
| 3 | Rate My Professors | Ruslan Flek — Mathematics, NYU. 60 reviews. | ratemyprofessors.com/professor/2556565 |
| 4 | Rate My Professors | Yaqi Duan — Statistics, NYU Stern. 47 reviews. | ratemyprofessors.com/professor/2803763 |
| 5 | Rate My Professors | Xiaojing Meng — Accounting, NYU Stern. 35 reviews. | ratemyprofessors.com/professor/1319425 |
| 6 | Rate My Professors | Kyle Jung — Accounting, NYU Stern. 29 reviews. | ratemyprofessors.com/professor/3075856 |
| 7 | Rate My Professors | Jessy Hsieh — Business, NYU Stern. 46 reviews. | ratemyprofessors.com/professor/1908831 |
| 8 | Rate My Professors | Carol Newell — Business, NYU Stern. 26 reviews. | ratemyprofessors.com/professor/193046 |
| 9 | Rate My Professors | Jennifer Morgan — History, NYU. 38 reviews. | ratemyprofessors.com/professor/53769 |
| 10 | Rate My Professors | Hannah Husby — Nutrition, NYU. 12 reviews. | ratemyprofessors.com/professor/2491744 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 300

**Overlap:** 50

**Reasoning:**
The documents consists of independent short student reviews. Each review is typically 1-4 sentences long and generally covers a specific aspect (exam, teaching, grading, accessibility). A single review rarely exceeds 400 characters, hence using 300 character chunks would mean that each chunk captures roughly one complete review and is still able to preserve its standalone message. If we go to large (let's say 800 characters), each chunk may merge multiple reviews into one chunk, which can confuse the model and result in bad matchups. Likewise, going to small would risk cutting off reviews mid sentence, destroying context. 50 character overlap ensures that the reviews split across a chunk boundary would still carry enough context in each half such that it is retrievable on its own.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers local

**Top-k:** 5

**Production tradeoff reflection:**
If cost wasn't a constraint I would consider the domain specificity, multilingual abilities, and latency. Domain specificity in that MiniLM is trained on general web text and may not encode NYU specific jargon such as "pfa" or "Stern curve" as meaningfully as a model fined tuned on academic review style text. In that case a model like OpenAi's text-embedding-3-large would likely retrieve more precisely. To add on, NYU has many international students and, although it isn't common, there could be reviews that contain non-English phrasing, especially if the project is scaled at a greater level where extracting info from multiple sources becomes viable. In that case a multilingual model like paraphrase-multilingual-MiniLM-L12-v2 would handle them better, at the cost of English accuracy. Furthermore, running the model locally means relaying on your own computer's processing speed compared to cloud based where much of it is based on internet connection. Since the tool is for students during registration hours, the tool needs to be fast so I'd want to test both approaches and determine which actually perfroms better.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Does bowmaker curve grades generously? | Yes. Multiple reviews state he gives around 40% compared to the standard Stern 35% and uses his tenure to expand the curve beyond department requirements. |
| 2 | Kyle Jung a good professor for someone with no accounting background? | No. Multiple reviews consistently describe him as a professor who is hard to follow, with exam medians in the 60s, and students strongly recommend taking anyone else. |
| 3 | Does Professor Duan allow cheat sheets on exams? | Yes. Multiple reviews from 2025 to 2026 state that a cheat sheet is allowed on both the midterm and the final. |
| 4 | What do people say about Professor McIntyre's attitude toward questions in class? | Negative. Multiple reviews describe him as condescending or rude when students ask questions. Several noted that he makes students feel stupid for asking. |
| 5 | Is Professor Husby's Nutrition class easy? | Yes. Reviews consistently call it one of the easiest classes at NYU, with straightforward multiple choice exams, non mandatory attendance, with extra credit. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->
     
1. Because a lot of reviews mention the “stern curve,” the search tool might get tripped up because if you ask about one professor’s grading, it might accidentally pull up reviews of a different professor just because the same phrase is used. 

2. Some profs have deeply divided reviews (love or hate comments). So when the model reads these polarizing reviews, it might write a confusing summary or accidentally pick a side just because one of the opinion popped up slightly more often in the results.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
┌──────────────────────────────────────────────────────────┐
│                   DOCUMENT INGESTION                     │
│  10 prof_"".txt files  =>  load raw text                 │
│  Tool: Python file I/O                                   │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                      CHUNKING                            │
│  300-char chunks 50 overlap                              │
│  Metadata per chunk: professor name, source filename     │
│  Tool: LangChain CharacterTextSplitter                   │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│             EMBEDDING + VECTOR STORE                     │
│  Model: all-MiniLM-L6-v2                                 │
│  Store: ChromaDB (local)                                 │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                     RETRIEVAL                            │
│  Semantic similarity search  top-k 5                     │
│  Returns: chunks + source filenames                      │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                    GENERATION                            │
│  LLM: Groq llama-3.3-70b-versatile                       │
│  Grounding: answer from retrieved context only           │
│  Output: answer + cited source filenames                 │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                  QUERY INTERFACE                         │
│  Tool: Gradio                                            │
│  Input: question text box                                │
│  Output: answer text box + sources text box              │
└──────────────────────────────────────────────────────────┘
```
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
Give Claude the documents section and the chunking strat section from this md, along with a sample txt file to show formatting. Then ask it to implement a script ingest.py that loads all 10 files from a /data folder. Split each into 300 char chunks and 50 overlap using Langchain CharacterTextSplitter and attach source filename and prof name as metadata to each chunk. I will then verify it manually by printing 5 random chunks and making sure that each is readable, is within the chunk limit, and has the correct metadata associated.

**Milestone 4 — Embedding and retrieval:**
Give Claude the retrieval approach section and the output of the ingestion script. Then ask it to implement a retrieve(query,k=5) and embed.py, where it loads chunks, embeds with all-miniLM-L6-v2 and stores in a ChromaDb collection with metadata. I will then manually verify by running 3 of my evaluation plan queries and printing the returned chunks and distance scores, making usre that top results are relevant and distances are below 0.5.


**Milestone 5 — Generation and interface:**
Give Claude the generation section, the retrive function, and the Gradio structure from the proj spec. Then ask it to implement query.py(calling groq) and app.py (Gradio UI). I will then manually verify by testing all 5 eval plan questions, confirming source attribution in every response and asking one out of scope question, making sure it declines rather than hallucinates. 
