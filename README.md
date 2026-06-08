# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This RAG system covers NYU professor reviews that draws on student reviews from Rate My Professor across 10 professors from departments of Accounting, Economics, Statistics, English, Math, History, and Nutrition. While the information technically exists online, it's scattered across individual professor pages with no way to ask cross-cutting questions like "which professor have exams that mimics the practice tests" or "which accounting professor is academically challenging" without digging through hundreds of reviews and manually piecing together the answer yourself. The way that this system works is by taking collective student knowledge from RMP reviews and turn it into something instantly queryable and generate cited answers based on real student experiences rather than from official course descriptions. 

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — Simon Bowmaker | Student reviews | ratemyprofessors.com/professor/343380 |
| 2 | Rate My Professors — Gerald McIntyre | Student reviews | ratemyprofessors.com/professor/228513 |
| 3 | Rate My Professors — Ruslan Flek | Student reviews | ratemyprofessors.com/professor/2556565 |
| 4 | Rate My Professors — Yaqi Duan | Student reviews | ratemyprofessors.com/professor/2803763 |
| 5 | Rate My Professors — Xiaojing Meng | Student reviews | ratemyprofessors.com/professor/1319425 |
| 6 | Rate My Professors — Kyle Jung | Student reviews | ratemyprofessors.com/professor/3075856 |
| 7 | Rate My Professors — Jessy Hsieh | Student reviews | ratemyprofessors.com/professor/1908831 |
| 8 | Rate My Professors — Carol Newell | Student reviews | ratemyprofessors.com/professor/193046 |
| 9 | Rate My Professors — Jennifer Morgan | Student reviews | ratemyprofessors.com/professor/53769 |
| 10 | Rate My Professors — Hannah Husby | Student reviews | ratemyprofessors.com/professor/2491744 |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 char

**Overlap:** 100 char

**Why these choices fit your documents:**
The documents are made up of independent, brief student reviews. Each review is typically 1-4 sentences long and addresses a certain topic (examination, teaching, grading, accessibility). The initial chunk size of 300 characters was too small, resulting in important data like a professor's name and precise statistics ("give ~42%") to sometimes end up in multiple chunks with no overlap, causing retrieval to fail even when the information exists. Increasing to 500 characters with a 100 character overlap allows each chunk to collect one to two entire reviews, while the overlap helps bridge reviews that cross a boundary.

Preprocessing removed all HTML, nav text, RMP boilerplate, thumbs count, tag pills.


**Final chunk count:** 318 chunks across 10 docs


**Sample chunks:**
 
*Chunk 1 — Source: prof_jung_kyle.txt*
```
o condescending. Exams and material are difficult. The curve is good, but only because everyone else
does bad. Don't take this guy unless self-studying is your thing.
 
---
 
Course: ACCT-UB1 | Date: Apr 2026
Jung Jung Jung Sahur, as he calls himself, is best described as well-qualified...
```
 
*Chunk 2 — Source: prof_duan_yaqi.txt*
```
orward because Prof Duan gives you a couple of sample exams that look a lot like the actual exam.
Cheat sheets are allowed as well! She is also incredibly kind and wants everyone to do well in the class.
```
 
*Chunk 3 — Source: prof_bowmaker_simon.txt*
```
re always super engaging. Tests are easy, and similar to the practice exams he gives. W teacher,
everyone should take if possible.
 
---
 
Course: ECONUB217 | Date: Feb 2026
Professor Bowmaker is actually the GOAT...
```
 
*Chunk 4 — Source: prof_newell_carol.txt*
```
her workshop hours.
 
---
 
Course: MULTUB100 | Date: Dec 2020
Newell's a bit opinionated, but I personally liked how comfortable it was speaking in class — she
made it feel more like a friendly discussion rather than an intimidating one.
```
 
*Chunk 5 — Source: prof_husby_hannah.txt*
```
d no surprises. Group project at the end (not hard).
 
---
 
Course: NUTRUE119 | Date: Dec 2023 | Grade: A+
This class is almost unbelievably easy. Husby makes it interesting and she's very understanding
and kind. There are weekly discussion posts but only like 250 words.
```

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` thru the `sentence-transformers` library. The model runs fully local with no API or rate limits. It produces 384 dimensional embeddings optimized for semantic similairy, meaning that it is able to match a query like "does he curve exams" to a review that mentions "Stern curve hurt everyone's grade" even if the exact words aren't overlapping.

**Production tradeoff reflection:**
If cost wasn't a constraint I would consider the domain specificity, multilingual abilities, and latency. Domain specificity in that MiniLM is trained on general web text and may not encode NYU specific jargon such as "pfa" or "Stern curve" as meaningfully as a model fined tuned on academic review style text. In that case a model like OpenAi's text-embedding-3-large would likely retrieve more precisely. To add on, NYU has many international students and, although it isn't common, there could be reviews that contain non-English phrasing, especially if the project is scaled at a greater level where extracting info from multiple sources becomes viable. In that case a multilingual model like paraphrase-multilingual-MiniLM-L12-v2 would handle them better, at the cost of English accuracy. Furthermore, running the model locally means relying on your own computer's processing speed compared to cloud based where much of it is based on internet connection. Since the tool is for students during registration hours, the tool needs to be fast so I'd want to test both approaches and determine which actually perfroms better.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The system prompt passed to `llama-3.3-70b-versatile` thru Groq:

```
You are a helpful assistant for NYU students looking for honest, student-sourced information 
about professors and courses.

You will be given a question and a set of retrieved student reviews as context.


RULES:
1. Answer ONLY using the information in the provided context. Do not use any outside knowledge.
2. If the context does not contain enough information to answer the question, say exactly: 
   "I don't have enough information in my sources to answer that."
3. Do not make up facts, statistics, or student opinions that are not in the context.
4. Be direct and specific — students want actionable answers.
5. Always end your response with a "Sources:" line listing the filenames the answer draws from.
```

I made sure to clearly label the provided student reviews before asking the AI a question so that it wouldn't confuse our facts with its own knowledge. Also used a low temp setting (0.2) to make sure that the AI's answers are accurate and factual and not hallucinating.


**How source attribution is surfaced in the response:**

The model is instructed to end every response with a `sources:` line that list the filenames it drew from. The `ask()` function in `query.py` then parse the line, which splits `sources:` to separate the source list from the answer, and pass both to Gradio UI, which displays them in separate boxes. If the model omits the Sources line, the code would go back to lising source filenames from the top k retrieved chunks. 


**Example response with source attribution:**
```
Question: "Does Professor Duan allow cheat sheets on exams?"

Answer: "Yes, Professor Duan allows cheat sheets on exams. Multiple reviews confirm that a cheat sheet is permitted on both the midterm and the final."

Retrieved from: • prof_duan_yaqi.txt
```

**Example out-of-scope response:**
 
```
Question: "does jessy do curves"

Answer: "There is no direct information about Jessy curving grades in the provided context. However, some reviews mention that the grades for the class were 'really ambiguous' and that scores among the class are 'so close', but none of them explicitly state whether Jessy curves grades or not."

Retrieved from: • prof_hsieh_jessy.txt
```
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Does Professor Bowmaker curve grades generously? | Yes. gives ~42% As instead of required 35% | "Mixed information — one review mentions the curve can be tough, another does not provide specifics" | Partially relevant. Returned Bowmaker chunks but not the one containing the 42% stat | Inaccurate |
| 2 | Is Kyle Jung a good professor for someone with no accounting background? | No. Hard to follow, exam medians in 60s, students say avoid him | Correctly said no. Mentioned difficult lectures, condescending attitude, need to self-study, but noted one positive review | Relevant. All top chunks from prof_jung_kyle.txt | Accurate |
| 3 | Does Professor Duan allow cheat sheets on exams? | Yes. Multiple reviews explicitly confirms this | "Yes, Professor Duan allows cheat sheets on exams." | Relevant. Chunk 2 contained the exact phrase "Cheat sheets are allowed as well!" | Accurate |
| 4 | What do students say about Professor McIntyre's attitude toward questions in class? | Negative. Described as condescending, snappy, makes students feel stupid | Returned mixed response. Cited condescending reviews but also surfaced positive reviews about him remembering students' names | Partially relevant. Retrieved both critical and positive chunks | Partially accurate |
| 5 | Is Professor Husby's Nutrition class easy? | Yes. Consistently described as one of NYU's easiest, easy A, extra credit | Correctly said yes. Cited "almost unbelievably easy," straightforward MC exams, easy group project | Relevant. All top chunks from prof_husby_hannah.txt | Accurate |

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Does Bowmaker give 40% As?

**What the system returned:** Either a super vague response that cites "mixed information" about the Stern curve, or the refusal message: I don't have enough information in my sources to answer that.

**Root cause (tied to a specific pipeline stage):** I think it could be a chunking failure. The reviews that contain the specific answer of him using "his tensure to expand the Stern curve (gives ~42$ As instead of the required 35%)" and "Since he has tenure he actually breaks the Stern curve and gave around 40% of our class an A" were split across the chunk boundaries. The prof's name and course context landed in one chunk while the stat landed in the next. Apparently the overlap wasn't large enough to bridge the split as no single chunk contained both "Bowmaker" and "42% As" together. As such, the model couldn't find a high similarity match as the relevant signal was distributed across two chunks. 

**What you would change to fix it:**
Either I would increase the chunk size further so multi sentence reviews stay together or I split on the `---` separator between the reviews so that each chunk contains exactly one review.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
I mean, in a way, it kind of forced a concrete decision about chunk size and overlap that directly shaped the pipeline. When I bumped into the Bowmaker curve fail, I was able to trace the problem back to the initial 300 char chunks that caused the retrieval failures and update it to 500 char. Without the spec, I would've just changed a number. But with it, I had to articulate why my new size is better, which made the failure analysis in README much easier to write as well. 

**One way your implementation diverged from the spec, and why:**
The spec called for using LangChain `CharacterTextSplitter` for chunking. I ended up writing a custom character based chunking function instead because the customer function was simplier to debug and modify for this mid size chunk project. The function also tries to break at natural boundaries (newlines, sentence openings) before going back to word boundaries, which LangChain's fixed splitter doesn't do. 

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The documents and chunking strat sections of `planning.md` along with a sample `.txt` file showing the review formatting. I asked Claude to implement `ingest.py` based on my specified chunk size of 300 char and 50 char overlap.
- *What it produced:* ingestion script with document loading, sliding window chunking function, metadata attachment, validation, and JSON output
- *What I changed or overrode:* The script used `DATA_DIR = "data"` but my repo uses `documents/` so I corrected that. After testing the retrieval, I decided that 300 chunks was too small as key info were being split across boundaries so I increased `CHUNK_SIZE` to 500 and `OVERLAP` to 100. 

**Instance 2**

- *What I gave the AI:* My retrieval approach section from `planning.md` and asked Claude to implement the embedding pipeline and a grounded generation function paired with the system prompt, which forces answers from retrieved context only.
- *What it produced:* `embed.py` with batched ChromaDB storage, `query.py` with the `ask()` function and enhanced system prompt.
- *What I changed or overrode:* Reviewed the system prompt and kept the structure but specific wording of not being able to have enough info fallback was something I wanted to be explicit about, so I confirmed it matched my intent before keeping it. I also changed `TOP_K` from 5 to 8 after noticing that some queries weren't showing enough relevant chunks with only 5 results.
