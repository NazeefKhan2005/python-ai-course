# Phase 5 · Deep Learning & Generative AI

**Goal:** understand neural networks from first principles, train deep models with PyTorch, understand transformers and language models, and build evaluated, safe LLM applications (prompting, structured output, tools, RAG, agents).
**Modules:** M20–M23 · 28 lessons · ~53 h · **Portfolio project P5:** RAG assistant **or** image classifier app (`spec/09`) · **Phase exam `p5-exam`:** 25 questions + 2 NumPy implementation tasks, 90 minutes.

**Phase teaching notes**
* **Two kinds of work.** Concepts are implemented **from scratch with NumPy** (forward passes, backprop, attention, sampling: small sizes, fast, graded with pytest). Real frameworks (PyTorch, Hugging Face, real LLM APIs) run locally in scripts and **notebooks** (`site/notebooks/`); a laptop CPU is enough for graded work, and a hosted GPU notebook is optional for the big experiments. Each notebook lesson also has pytest-graded exercises (shape reasoning, from-scratch versions) so the learner gets precise feedback.
* **LLM exercises use `MockLLM` and `HashEmbedder`** from `course_mocks.py` (shipped in every pack, `spec/05` §5): no API key, no cost, deterministic tests. Lessons also show the real client code for the learner's own key. They are deterministic, need no network and no keys, and have the same interface ideas as real SDKs. Each lesson also shows the real-SDK version (Anthropic and OpenAI) as a static code block plus a local/notebook task. Keys always come from environment variables, never from page code.
* Training-based exercises keep runtime under about 15 s on a laptop CPU: small models, `load_digits`, few epochs.
* **Library generations** (pins in `requirements-deep-learning.txt`, details in `spec/06` §9): PyTorch 2.15 (`torch.load` defaults to `weights_only=True`), transformers 5 (PyTorch only; `dtype=` replaces `torch_dtype=`; turn progress bars off in verified examples with `transformers.utils.logging.disable_progress_bar()`), MCP Python SDK 2 (`MCPServer`, which older tutorials call `FastMCP`). Libraries that don't install on Python 3.15 yet (Chroma, LangGraph) are overview only (`spec/02` §5.1).
* LLM facts change quickly (model names, prices, context sizes). **Don't hard-code model names or prices in lessons.** Teach how to look them up and use placeholders such as `MODEL = "<current model id>"`.

---

## M20 · Neural Networks from Scratch
`m20-nn-from-scratch` · 6 lessons · ~11 h · Needs M07, M11, M14

**Why it matters at work:** interviewers ask you to explain backprop. When training goes wrong, people who understand the mechanics fix it faster than people who only call `.fit()`.

**Outcomes:** implement forward passes, activations and losses; derive and implement backprop for dense layers, with gradient checks; build a tiny autograd engine; train an MLP from scratch to over 90% on digits; implement optimisers and regularisation.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m20-l01** `l01-neurons-networks` From neurons to networks | Perceptron, weights and bias, activations (step, sigmoid, tanh, ReLU, GELU), layers, the forward pass as matrix multiplication, universal approximation intuition | ◆ activation functions, vectorised forward pass ▲ universal approximation (concept) | **E1** `relu(x)`, `sigmoid(x)` (stable). **E2** `dense_forward(X, W, b, activation) -> np.ndarray` with shape checks |
| **m20-l02** `l02-losses-softmax` Loss functions & softmax | MSE, binary cross-entropy, softmax + categorical cross-entropy, numerical stability, one-hot vs integer labels | ◆ stable softmax, cross-entropy ▲ label smoothing | **E1** `softmax(Z)` (row-wise). **E2** `cross_entropy(probs, labels) -> float`. **E3** `softmax_ce_grad(logits, labels) -> np.ndarray` (checked numerically) |
| **m20-l03** `l03-backpropagation` Backpropagation | Computational graphs, the chain rule, gradients of a dense layer, backprop through a 2-layer MLP, **gradient checking** | ◆ computational graphs, gradient checking ▲ vanishing and exploding gradients | **E1** `dense_backward(dout, X, W) -> tuple[dX, dW, db]`; tests compare with numerical gradients (relative error < 1e-6) |
| **m20-l04** `l04-tiny-autograd` Build a tiny autograd engine | A `Value` class: `+ * ** -`, `tanh`, `relu`, building the graph, topological sort, `backward()`. Inspired by Karpathy's micrograd (link and credit; the code is the course's own) | ◆ operator overloading for autograd ▲ topological order of the graph | **E1** implement `Value` operations and `backward`; tests compare gradients with finite differences on 5 expressions |
| **m20-l05** `l05-train-mlp` Train an MLP from scratch | Data (`load_digits`, scaled), He/Xavier initialisation, mini-batch SGD, loss and accuracy curves, overfitting one batch as a debugging step | ◆ mini-batches, initialisation ▲ learning-rate schedules | **E1** `train_mlp(X, y, hidden, epochs, lr, seed) -> dict` (weights + history); ≥ 0.90 held-out accuracy within the time limit |
| **m20-l06** `l06-optimizers-regularization` Optimisers & regularisation | SGD, momentum, RMSProp, **Adam** (implement), learning-rate schedules, weight decay, dropout (train vs eval), batch norm (concept), early stopping | ◆ momentum, Adam, dropout, weight decay ▲ batch normalisation | **E1** `adam_step(params, grads, state, lr, b1, b2, eps) -> state`. **E2** `dropout(x, p, rng, training) -> np.ndarray` (inverted dropout; expected value preserved) |

**Module project (`m20-project`):** *Digits from scratch*: a NumPy-only MLP with Adam, early stopping and a loss-curve plot; ≥ 0.95 accuracy on the held-out split. Graded, plus a 5-sentence reflection (rubric).
**Checkpoint (`m20-checkpoint`, 14 Q).**
**Interview corner:** explain backprop to an engineer · vanishing and exploding gradients · why ReLU · Adam vs SGD · what to try when the loss doesn't go down.
**Misconceptions:** more layers are always better; the training loss alone shows generalisation; dropout is active at inference.

---

## M21 · Deep Learning with PyTorch
`m21-pytorch` · 8 lessons · ~16 h · Needs M20

**Why it matters at work:** PyTorch is the dominant framework in industry and research. Fluency with tensors, `nn.Module` and the training loop is expected for ML-engineer roles.

**Outcomes:** work with tensors and autograd; build models with `nn.Module`; write a clean, reproducible training/evaluation loop; build CNNs with augmentation; fine-tune pretrained models; understand sequence models; debug and speed up training.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) | Notebook (self-checks) |
|---|---|---|---|---|
| **m21-l01** `l01-tensors-autograd` Tensors & autograd | Tensors vs ndarrays, dtype and device (CPU/CUDA/MPS), broadcasting, `requires_grad`, `backward`, `no_grad` | ◆ dtypes, devices, `requires_grad`, `no_grad` ▲ in-place operations and autograd | Predict-the-shape quiz (10 items); **E1** `broadcast_shape(a, b) -> tuple \| None` | tensor ops, an autograd check against manual gradients |
| **m21-l02** `l02-nn-module` Building models with `nn.Module` | `Linear`, `Conv2d`, `Embedding`, `forward`, `parameters()`, `Sequential`, initialisation, parameter counting | ◆ `nn.Sequential`, parameters, `state_dict` ▲ hooks | **E1** `count_params(layers: list[dict]) -> int` (Linear/Conv2d/Embedding specs) | build an MLP; parameter count matches |
| **m21-l03** `l03-training-loop` The training loop | `Dataset`/`DataLoader`, loss and optimiser, `train()`/`eval()`, metrics, checkpoints (`state_dict`), seeding, overfitting one batch first | ◆ `Dataset`, `DataLoader`, train/eval modes ▲ mixed precision | **E1** (Parsons) order the 8 steps of a training step correctly | FashionMNIST MLP ≥ 85% |
| **m21-l04** `l04-cnns` CNNs for computer vision | Convolution, padding and stride, pooling, receptive fields, CNN architectures, augmentation (`torchvision.transforms.v2`) | ◆ convolution and pooling layers, augmentation ▲ receptive fields | **E1** `conv2d(img, kernel, stride=1, padding=0)` in NumPy. **E2** `conv_output_size(n, k, s, p) -> int` | FashionMNIST CNN ≥ 90% |
| **m21-l05** `l05-transfer-learning` Transfer learning | Pretrained backbones (torchvision), feature extraction vs fine-tuning, freezing layers, small datasets, evaluation | ◆ freezing layers, fine-tuning ▲ domain shift | Quiz: when to freeze, learning rates for fine-tuning | fine-tune ResNet-18 on a small, permissively licensed image set (≥ target accuracy) |
| **m21-l06** `l06-sequence-models` Sequence models & embeddings | Embeddings, RNN/LSTM/GRU ideas, padding and masking, sequence classification; why transformers replaced RNNs | ◆ embeddings, RNN/LSTM/GRU ▲ packed sequences | **E1** `build_vocab(texts, min_freq) -> dict`. **E2** `pad_batch(seqs, pad_id, max_len) -> np.ndarray` | LSTM sentiment classifier on a small dataset |
| **m21-l07** `l07-practical-dl` Practical deep learning | GPU memory, mixed precision (`torch.autocast`), `torch.compile` (mention), gradient clipping, LR schedules, experiment logging, a debugging checklist; the framework landscape (Keras 3 multi-backend, JAX) | ◆ checkpoints, debugging training, reproducibility ▲ profiling | Quiz: diagnose 6 training curves | profile and speed up a training loop |
| **m21-l08** `l08-pytorch-reference` PyTorch reference | The tensor operations, layers, losses and optimisers used in 90% of code, grouped by task | ◆ every `Tensor` method and attribute, every layer and loss in `torch.nn`, every optimiser and scheduler in `torch.optim`, `torch.utils.data` ▲ `torch.compile`, custom autograd functions · **Ref:** `class:torch.Tensor` `module:torch.nn` `module:torch.optim` `module:torch.utils.data` | **Reference drills (CPU, seconds):** **E1** shape gymnastics (`view`, `permute`, `unsqueeze`). **E2** `masked_mean` with boolean masks. **E3** a custom `Dataset` + `DataLoader` with `collate_fn` | Notebook: tour of the reference with live outputs; self-check cells assert shapes |

**Module project (`m21-project`):** *Image classifier app*: transfer learning on a small dataset + a Gradio demo deployed to Hugging Face Spaces (it can become P5 option B).
**Checkpoint (`m21-checkpoint`, 15 Q).**
**Interview corner:** CNN intuition · batch norm · transfer learning strategy · "the training loss is NaN, what do you do?" · GPU out-of-memory fixes.
**Misconceptions:** `model.eval()` turns off gradients; bigger batches are always better; pretrained models need no normalisation matching.

---

## M22 · NLP & Transformers
`m22-nlp-transformers` · 6 lessons · ~12 h · Needs M20 (M05-L05 helps)

**Why it matters at work:** every LLM product rests on tokenization, embeddings, attention and decoding. Engineers who understand them debug cost, latency and quality problems that others can't.

**Outcomes:** implement BPE tokenization; use word embeddings for similarity and analogies; implement scaled dot-product and multi-head attention; explain and implement transformer blocks and positional encodings; use Hugging Face to fine-tune and evaluate models; implement decoding strategies and perplexity.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest) |
|---|---|---|---|
| **m22-l01** `l01-tokenization` Tokenization | Word vs character vs subword; the **BPE** algorithm; WordPiece, SentencePiece, byte-level BPE; tokens vs words; why token counts drive cost (tiktoken in the notebook) | ◆ BPE, WordPiece, special tokens ▲ tokenizer pitfalls (whitespace, numbers) | **E1** `bpe_learn(corpus: list[str], num_merges) -> list[tuple[str, str]]`. **E2** `bpe_encode(word, merges) -> list[str]` |
| **m22-l02** `l02-word-embeddings` Word embeddings | The distributional hypothesis, the word2vec idea, cosine similarity, analogies, PCA visualisation, bias in embeddings. Uses `data/glove-mini.json` (a small GloVe subset; **verify the licence and attribute it**) | ◆ word2vec intuition, cosine similarity ▲ bias in embeddings | **E1** `most_similar(word, vectors, k) -> list[str]`. **E2** `analogy(a, b, c, vectors) -> str` (excluding the inputs) |
| **m22-l03** `l03-attention` Attention from scratch | Queries, keys, values; scaled dot-product attention; softmax over scores; causal and padding masks; multi-head attention (split and merge heads) | ◆ scaled dot-product attention, masks ▲ multi-head attention shapes | **E1** `attention(Q, K, V, mask=None) -> tuple[out, weights]`. **E2** `causal_mask(n) -> np.ndarray`. **E3** `split_heads(X, h)` and `merge_heads(X)` |
| **m22-l04** `l04-transformer-architecture` The transformer architecture | Token embeddings + sinusoidal positional encoding (RoPE as a concept), the block (attention + MLP + residual + layer norm), encoder vs decoder vs encoder–decoder, BERT vs GPT vs T5, context windows, scaling intuition | ◆ positional encodings, residuals, layer norm ▲ the KV cache | **E1** `positional_encoding(seq_len, d_model) -> np.ndarray`. **E2** `layer_norm(x, eps=1e-5)`. **E3** `block_forward(x, params)` (a tiny pre-LN block; matches the reference) |
| **m22-l05** `l05-hugging-face` Hugging Face in practice | `pipeline`, `AutoTokenizer`/`AutoModel`, `datasets`, fine-tuning a classifier (`Trainer`), evaluation, model cards and licences on the Hub | ◆ pipelines, `AutoTokenizer`, `AutoModel` ▲ model cards and licences | Quiz (8 Q) + **notebook**: fine-tune a small encoder on sentiment ≥ target F1, with error analysis |
| **m22-l06** `l06-lm-decoding` Language modelling & decoding | Next-token prediction, a bigram LM from scratch, perplexity, greedy, temperature, top-k, top-p, repetition penalty | ◆ greedy, beam, temperature, top-k/top-p ▲ perplexity | **E1** `bigram_counts(tokens) -> dict`. **E2** `perplexity(token_probs) -> float`. **E3** `sample_next(logits, temperature, top_k, top_p, rng) -> int` (tests check distributions with fixed seeds) |

**Module project (`m22-project`):** *Fine-tune and audit*: fine-tune a sentiment model (notebook), then write an error-analysis report (slices, failure examples, bias probes) using the rubric.
**Checkpoint (`m22-checkpoint`, 15 Q).**
**Interview corner:** explain attention · BERT vs GPT · how tokenization affects cost and multilingual quality · temperature vs top-p · what positional encodings do.
**Misconceptions:** tokens are words; temperature 0 is always best; attention weights are explanations.

---

## M23 · Building LLM Applications
`m23-llm-apps` · 8 lessons · ~14 h · Needs M22 (L01–L04 need only M12 + M15)

**Why it matters at work:** "AI engineer" roles centre on building reliable LLM features: prompts, structured outputs, tool use, retrieval, evaluation and guardrails, with attention to cost and safety.

**Outcomes:** call LLM APIs safely (keys, cost, streaming); engineer and version prompts; get validated structured outputs; implement the tool-calling loop; build vector search and RAG with citations; evaluate LLM apps (retrieval and answer metrics, regression tests); defend against prompt injection; decide when agents are (and aren't) appropriate.

| Lesson | Essential (must cover) | Extra & advanced · reference | Graded exercises (pytest, MockLLM) |
|---|---|---|---|
| **m23-l01** `l01-llm-apis` Working with LLM APIs | Messages and roles, system prompts, parameters, tokens, cost and latency, streaming; Anthropic and OpenAI SDK equivalents (static code); **API keys only in environment variables**; local setup task | ◆ message roles, tokens and cost, streaming ▲ retries with backoff | **E1** `build_messages(system, history, user) -> list[dict]`. **E2** `estimate_cost(tokens_in, tokens_out, price_in_per_m, price_out_per_m) -> float` |
| **m23-l02** `l02-prompt-engineering` Prompt engineering | Clear instructions and context, examples (few-shot), delimiters/XML tags, roles, asking for reasoning, templates, versioning prompts, testing prompts with cases | ◆ few-shot, system prompts, output constraints ▲ prompt-injection basics | **E1** `render_prompt(template, **values) -> str` (error naming any missing variable). **E2** `few_shot_prompt(examples, query) -> str` (exact format) |
| **m23-l03** `l03-structured-outputs` Structured outputs | JSON outputs, schema-constrained generation, pydantic models, validation, **retrying with the error fed back**, defensive parsing | ◆ JSON schemas, pydantic validation, retries ▲ constrained decoding (concept) | **E1** `parse_with_retry(llm, messages, Model, max_retries) -> Model`; `MockLLM` returns invalid JSON first, and tests check the retry message contains the validation error |
| **m23-l04** `l04-tool-use` Tool use / function calling | Tool schemas (JSON Schema), the call → execute → return loop, multi-step tools, step budgets, safe tool execution; **MCP** (Model Context Protocol): what servers expose (tools, resources, prompts) and a minimal local server with the MCP SDK 2 (`MCPServer`, run by the learner) | ◆ tool schemas, the tool loop ▲ parallel tool calls | **E1** `run_tool_loop(llm, tools, user_msg, max_steps) -> str`. **E2** `tool_schema(fn) -> dict` from type hints and the docstring |
| **m23-l05** `l05-embeddings-vector-search` Embeddings & vector search | Text embeddings, similarity, chunking (fixed, overlap, structure-aware), brute-force vs ANN indexes, a FAISS index (`faiss-cpu`; it has no Windows wheels, so a platform note sends Windows learners to WSL 2 for that section), Chroma and pgvector as overview (`spec/02` §5.1), metadata filters. A real embedding model with sentence-transformers runs locally (one-time model download); in tests: `HashEmbedder` (lexical and deterministic: say so) | ◆ similarity search, chunking ▲ approximate nearest-neighbour indexes | **E1** `chunk_text(text, size, overlap) -> list[str]`. **E2** `top_k(query_vec, matrix, k) -> list[int]` (cosine; vectorised) |
| **m23-l06** `l06-rag` Retrieval-augmented generation | Ingest → chunk → embed → index → retrieve → assemble the prompt → generate → cite; hybrid search (BM25, from scratch in E1 and then with `bm25s`, combined with vectors), reranking, "I don't know" behaviour, failure modes | ◆ retrieval + generation, citations ▲ reranking, hybrid search | **E1** `bm25_scores(query, docs, k1=1.5, b=0.75) -> list[float]`. **E2** `build_rag_prompt(question, chunks) -> str` (numbered sources). **E3** `answer(question, index, llm) -> dict` with citations |
| **m23-l07** `l07-llm-evaluation-safety` Evaluating LLM apps & safety | Evaluation sets, exact match and token F1, retrieval metrics (recall@k, MRR), LLM-as-judge (with caveats), prompt regression tests, guardrails, **prompt injection** (direct and indirect) and mitigations, data leakage, hallucination handling | ◆ evaluation sets, LLM-as-judge ▲ red-teaming | **E1** `recall_at_k(retrieved, relevant, k)`. **E2** `mrr(results)`. **E3** `token_f1(pred, gold)`. **E4** `quarantine_instructions(doc_text) -> str` (a defence-in-depth exercise; the lesson says plainly that no filter is complete) |
| **m23-l08** `l08-agents` Agents & orchestration | The agent loop (plan → act → observe), memory, step and cost budgets, human-in-the-loop, frameworks as overview (LangGraph, LlamaIndex, Claude Agent SDK, OpenAI Agents SDK, MCP servers; `spec/02` §5.1), when **not** to use agents, reliability and evaluation | ◆ planning loops, budgets, traces ▲ multi-agent patterns | **E1** `Agent` class with tools, a step budget and a trace log; tests run scripted `MockLLM` scenarios (success, a tool error, a loop that must stop) |

**Phase 5 portfolio project (`p5-project`):** RAG assistant **or** image classifier app (`spec/09`). **Checkpoint (`m23-checkpoint`, 16 Q)** and **phase exam `p5-exam`**.
**Interview corner:** design a RAG system for company docs · how to reduce hallucinations · how to evaluate an LLM feature · prompt injection risks · when to use prompting vs RAG vs fine-tuning.
**Misconceptions:** a bigger context window removes the need for retrieval; LLM-as-judge is objective; a system prompt alone prevents injection.
