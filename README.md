# Drikx — an artificial language built for thinking

[![DOI](https://zenodo.org/badge/1318201232.svg)](https://doi.org/10.5281/zenodo.21721016)

> `sat-a-mu` · `sat-a-ri` · `sat-a-kʼara`
> EXIST-NEUT-DIR · EXIST-NEUT-REP · EXIST-NEUT-CRU
> *"It exists — I have seen it / I am told / I merely believe."*

**Drikx** (endonym *pratil*) is a [constructed language](https://en.wikipedia.org/wiki/Constructed_language) — an engineered artefact, not a natural or historical tongue, with no native speakers. It was designed by *pseudoLuc* in the lineage of Hildegard of Bingen's *Lingua Ignota*: a **philosophical / engineered language** whose grammar is meant to **make cognitive laziness expensive to say**.

Where a natural language lets a speaker blur the source of a claim, delete the agent of an act, or assert a belief as though it were a fact, Drikx makes each of those moves cost a morpheme, a stress shift, or an ejective consonant that — quite literally — must be *spat*. The surprising thing is structural, not decorative: the same three or four decisions that shape its phonology also shape its syntax, its writing system, and its silences.

This repository is the public home of the language: the **reference grammar**, a **parallel corpus**, a fine-tuned **translation model**, and a **Claude skill** that translates and glosses Drikx in both directions.

---

## What's in this repo

| Path | What it is |
|---|---|
| [`drikx-grammar.pdf`](drikx-grammar.pdf) | **The Drikx Language — A Reference Grammar of a Language Built for Thinking.** A full descriptive grammar in English (phonology, morphology, syntax, semantics, glossed texts, paradigms, and a bilingual lexicon), typeset in the style linguists use for a previously undescribed tongue. |
| [`Gilgamesh's reply to Ishtar — English · Drikx · taktil.pdf`](Gilgamesh's%20reply%20to%20Ishtar%20—%20English%20·%20Drikx%20·%20taktil.pdf) | A trilingual **specimen**: Gilgamesh's refusal of the goddess Ishtar (*Epic of Gilgamesh*, Tablet VI), set in English, Drikx (romanised, with gloss and commentary), and *taktil* — twelve incisions pressed into clay. |
| [`corpus/`](corpus/) | A French ⇄ Drikx parallel corpus with morpheme-level gloss and evidential/aspect labels, in JSONL. |
| [`drikx/`](drikx/) | The **oracle**: a pure-Python rule engine that validates, glosses, and generates Drikx, plus a deterministic French→Drikx rule translator. This is the arbiter that certifies the corpus — *the model proposes, the oracle disposes.* |
| [`dict/`](dict/) | Bilingual dictionaries (French⇄Drikx) as JSON and Markdown, used by the rule translator and for lookup. |
| [`adapters/lfm2-drikx-v6/`](adapters/lfm2-drikx-v6/) | A LoRA adapter that teaches [LiquidAI **LFM2-350M**](https://huggingface.co/LiquidAI/LFM2-350M) to translate into and out of Drikx. |
| [`drikx-traduction.skill`](drikx-traduction.skill) | A packaged **Claude skill** (Agent Skill) for translating, glossing, transliterating, and extending Drikx. Contains the phonology, grammar, writing-system tables, design constraints, and the full lexicon as CSV. |

---

## The language in one page

Drikx is small, internally consistent, and organised around a handful of design decisions that propagate through every corner of the system. Seven **hard constraints** define it:

1. **Obligatory evidentiality.** Every finite clause carries a source morpheme — a bare assertion is ungrammatical. Four degrees, ranked (the mind never substitutes for experience):
   - `-mu` **DIR** — perceived / verified by the speaker
   - `-ka` **INF** — deduced from traces or reasoning (and forced by the future and by the unknown-agent pronoun)
   - `-ri` **REP** — reported, from a citable source
   - `-kʼara` **CRU** — belief without a source; it exists, but as a *heavy, ejective* form connoted as an epistemic fault.
2. **No passive, no impersonal.** The agent of an agentive process is syntactically obligatory. Unknown agent → the explicit "someone-I-don't-know" pronoun `tʼu`, marked inferential. (Spontaneous events like *to rain*, *to fall* are exempt.)
3. **Repetitive vs. sequential aspect**, grammaticalised and non-interchangeable: `-si` **REP** (routine, cycle, maintenance) vs. `-tu` **SEQ** (ordered steps toward a new state). *stir-si* = patrol; *stir-tu* = conquest.
4. **Verb-initial (VSO).** The action before the agent — with the consistent knock-on effects: prepositions, noun before genitive.
5. **Percussive phonology.** Three vowels (a i u), a consonant inventory dominated by stops with one marked (ejective) series, obstruent onset clusters, a CVC core syllable, common words of 1–3 syllables.
6. **Neither politeness nor consensus.** No honorifics, no formal "you"; "everyone says so" is just the reportative — no valorising form.
7. **Dense lexicon.** Few roots, each a semantic cluster; fine sense comes from productive derivation (agentive `-ar`, resultative `-ut`, instrumental `-il`, abstract `-as`, desiderative `-us`, privative `kʼa-`).

The finite verb is a single template — **STEM-ASPECT-EVIDENTIAL** — and questions and imperatives are the only finite forms with *no* evidential (the empty source slot *is* the question).

```
pa  stir-a-mu       kint su   xu   purk ni   xast
PST marcher-NEUT-DIR enfant PROX vers maison DIST hier
"This child walked to that house yesterday (I saw it)."
```

### The name is an exonym

*Drikx* cannot be pronounced in Drikx itself: the language has no /d/ and the coda /kx/ is illicit. **"Drikx" is the shape the language takes when named from outside.** Its speakers — were there any — would call it simply *pratil*, "the tongue, the speech-tool," or, if forced to an endonym, adapt the foreign name by regular phonology to *tirks*.

### The written language: *taktil*

Drikx is written in the *taktil* script: consonants in Old Italic glyphs, vowels in Runic (`𐌔𐌊𐌉𐌌·ᛆ·𐌌𐌓·𐌕ᛆ·𐌓𐌉𐌊𐌕᛭`), with an optional separator `᛫` and a closing mark `᛭` on assertions — **never** on questions.

---

## A specimen: Gilgamesh's reply to Ishtar

[**Gilgamesh's reply to Ishtar — English · Drikx · taktil.pdf**](Gilgamesh's%20reply%20to%20Ishtar%20—%20English%20·%20Drikx%20·%20taktil.pdf) is the language shown at length: Gilgamesh refusing the goddess's hand (*Epic of Gilgamesh*, Tablet VI), the whole invective a single sustained judgment, "twelve incisions" pressed into clay.

It is also a demonstration of how the grammar *bites*:

- **Evidentiality as tone.** Every line but the first carries the inferential `-ka` — Gilgamesh is *reasoning* about what Ishtar is. Only the opening refusal, "No, I will not take you for a wife," takes the direct `-mu`: his own will, stated as fact.
- **No passive, no causative.** "You are the headband that smothers the one who wears it" cannot be said with a suppressed agent — Drikx recasts it as *"short of air is the man who dons it."* "You are the waterskin that spills over the one who carries it" becomes water that *flows* (`xuln`, a spontaneous process), because there is no middle voice to hide behind.
- **The two closing questions lose their evidential slot** and stay unclosed — the empty source *is* the question; the missing `᛭` on the page is the missing answer.

```
xa  kurt-a-mu       na  ta ti  xu milar
NEG take-NEUT-DIR    1SG ACC 2SG as wife
"No, I will not take you for a wife."
```

---

## The corpus

Line-delimited JSON (JSONL), one sentence pair per line, with morpheme gloss and the grammatical labels that make Drikx Drikx (evidential, aspect, clause type, negation).

| File | Lines | Contents |
|---|---:|---|
| `corpus/train.jsonl` | 92,600 | training split |
| `corpus/dev.jsonl` | 5,144 | validation split |
| `corpus/test.jsonl` | 5,144 | held-out test split |
| `corpus/volet_b_haiku.jsonl` | 8,540 | "Volet B" set — short, image-like sentences generated with Claude Haiku |

Each record looks like:

```json
{"fr": "Vous coupez cette eau-là peu à peu (je le crois sans preuve).",
 "drikx": "takt-atu-kʼara tiru ta turs ni",
 "gloss": "trancher-SEQ-CRU 2PL ACC eau DIST",
 "volet": "A", "type": "decl", "evid": "kʼara", "aspect": "tu", "neg": false}
```

- `fr` — French source, with the evidential rendered as a parenthetical
- `drikx` — Drikx target, morpheme boundaries hyphenated
- `gloss` — Leipzig-style interlinear gloss
- `evid` / `aspect` / `neg` / `type` / `volet` — the grammatical labels used to balance the corpus

The source language of the pairs is **French**; the grammar PDF is in **English**.

---

## The oracle

`drikx/` is the language written as executable rules — a rule-based **oracle** that decides, for any string, whether it is well-formed Drikx and, if not, exactly why. It is the project's arbiter of truth: every pair in the corpus was admitted only after the oracle proved it grammatical. *The model proposes, the oracle disposes.*

It is a dependency-free, pure-Python package (spaCy is needed only for the French rule translator, below).

| Function | What it does |
|---|---|
| `validate(sentence) -> Report` | decides grammaticality across four layers and returns a `Report` (`ok` + coded `Issue`s) |
| `gloss(sentence) -> str` | Leipzig-style interlinear gloss |
| `generate(clause) -> str` | rebuilds the surface string from a `Clause` AST |
| `validate_lexeme(ipa, pos, …)` | the oracle at the entry level, for growing the lexicon safely |
| `check_phonotactics(word)` | syllabifies and checks onsets, codas, and ejective placement |

Each rejection carries a specific diagnostic code, grouped in four layers:

- **Phonotactics** — syllabification, licit onset/coda clusters, ejectives barred from lexical roots, the two epenthesis rules (`/r/` breaks a hiatus, `/a/` breaks a cluster at a morpheme boundary).
- **Verbal morphology** — the obligatory `STEM-ASPECT-EVIDENTIAL` template, aspect allomorphy (`-si`/`-tu` → `-asi`/`-atu` after a complex coda), a single evidential slot.
- **Syntax** — VSO order, obligatory agent (no passive, no impersonal), `ta` before objects, future ⇒ `-ka`, unknown-agent `tʼu` ⇒ `-ka`, no evidential on questions or imperatives.
- **The lexical/grammatical boundary** — lexical words end in a consonant, grammatical words in a vowel.

```python
from drikx import validate, gloss

print(bool(validate("skim-a-mu na ta silp")))   # True
print(gloss("skim-a-mu na ta silp"))
# → voir-NEUT-DIR 1SG ACC chat

bad = validate("skim-a na ta silp")             # aspect present, evidential missing
print(bool(bad), bad.codes())
# → False ['MISSING_EVIDENTIAL']
```

By default the oracle loads its lexicon from `Dricks-spec/03-lexique.csv` (the reference lexicon). Point it at a larger one — e.g. the 2,957-entry `Dricks-spec/lexique_v2.csv`, or the Claude skill's `references/lexique.csv` (same columns: `ipa,pos,translation,grammar,derivation,notes`) — by passing a `Lexicon`:

```python
from drikx import validate, Lexicon

lex = Lexicon("Dricks-spec/lexique_v2.csv")
validate("skim-a-mu na ta silp", lex)
```

### The rule translator (French → Drikx)

`drikx/fr2drikx.py` is a deterministic, LLM-free French→Drikx translator — the "Volet B" pipeline that built part of the corpus. It parses French with spaCy, maps content words through `dict/fr-drikx.json`, reorders to VSO, places the particles, aspect, and default (direct) evidential, then **lets the oracle validate the result**. Its policy is high-precision, low-recall: any sentence with an uncovered word or an unhandled construction is *discarded, never approximated*. Scope is declarative clauses (subject + verb + direct object + simple obliques), present/past/future, affirmative/negative.

```python
from drikx.fr2drikx import Translator

tr = Translator()                       # needs spaCy + the fr_core_news_sm model
out = tr.translate("Je vois un chat.")
print(out.drikx if out else "(écartée)")
# → skim-a-mu na ta silp
```

```bash
pip install spacy && python -m spacy download fr_core_news_sm
```

---

## The translation model

`adapters/lfm2-drikx-v6/` is a **LoRA** adapter fine-tuned on the corpus above using [Apple **MLX**](https://github.com/ml-explore/mlx) (`mlx-lm`). It is a ~6 MB adapter, not a full model — you load it on top of the base model.

| | |
|---|---|
| Base model | `LiquidAI/LFM2-350M` |
| Method | LoRA (rank 8, scale 20, dropout 0) |
| Trained layers | 8 |
| Iterations | 10,000 · batch size 32 · lr 1e-4 · max seq 256 |

Full hyper-parameters are in [`adapters/lfm2-drikx-v6/adapter_config.json`](adapters/lfm2-drikx-v6/adapter_config.json).

### Try it

**From the command line:**

```bash
pip install mlx-lm

python -m mlx_lm generate \
  --model LiquidAI/LFM2-350M \
  --adapter-path adapters/lfm2-drikx-v6 \
  --prompt "Traduis en Drikx : Cet enfant a marché jusqu'à cette maison hier."
```

**From Python** — load the base model once, apply the LoRA adapter, and translate:

```python
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

# Base model + the Drikx LoRA adapter (this repo's adapters/lfm2-drikx-v6/)
model, tokenizer = load(
    "LiquidAI/LFM2-350M",
    adapter_path="adapters/lfm2-drikx-v6",
)

def to_drikx(french: str) -> str:
    # LFM2 is chat-tuned — wrap the request in its chat template
    messages = [{"role": "user", "content": f"Traduis en Drikx : {french}"}]
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True
    )
    return generate(
        model, tokenizer,
        prompt=prompt,
        max_tokens=128,
        sampler=make_sampler(temp=0.0),   # greedy — translation, not invention
        verbose=False,
    )

print(to_drikx("Cet enfant a marché jusqu'à cette maison hier."))
# → e.g.  pa stir-a-mu kint su xu purk ni xast
```

The corpus was built around French prompts, so phrase requests in French (`Traduis en Drikx : …` / `Traduis en français : …`) for best results.

> **Note.** A 350M-parameter model trained on a synthetic corpus is a *demonstration*, not an oracle. For rigorous or edge-case translation, prefer the reference grammar, the [`drikx/` oracle](#the-oracle) — which decides grammaticality programmatically — or the Claude skill, all of which enforce the evidential chain and the no-passive rule sentence by sentence.

---

## The Claude skill

`drikx-traduction.skill` is an [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) that translates **to and from Drikx**, glosses, checks a sentence for conformity, transliterates to/from *taktil*, and extends the lexicon by derivation. It bundles the phonology, morphosyntax, writing-system tables, the seven design constraints, worked examples, and the full ~2,900-entry lexicon as CSV.

It's a standard zip. To inspect it:

```bash
unzip -o drikx-traduction.skill -d drikx-skill
# drikx-traduction/SKILL.md, references/{01-phonologie,02-grammaire,05-ecriture,00-contraintes,04-traductions}.md, references/lexique.csv
```

To use it in **Claude Code**, unpack it into your skills directory (e.g. `~/.claude/skills/`) and it will trigger whenever you ask to translate, gloss, analyse, correct, or compose Drikx — in either direction.

---

## Credits & lineage

Designed by **pseudoLuc**, in the tradition of *engineered* / *philosophical* languages — from Hildegard of Bingen's *Lingua Ignota* onward — whose ambition is not to be spoken by a nation but to embody an idea.

*pseudoLuc* is the reflective LLM model of **Luc E. Brunet**, described in:

> Luc E. Brunet. *Le problème difficile de l'identité : évaluation d'un clone LLM.* **JITIPEE** 9(2), 2025. [doi:10.52497/jitipee.v9i2.381](https://doi.org/10.52497/jitipee.v9i2.381)

### Cite this repository

This repository — the grammar, corpus, oracle, model, and skill — is archived on Zenodo:

> Brunet, L. E. *Drikx — an artificial language built for thinking.* Zenodo. [doi:10.5281/zenodo.21721016](https://doi.org/10.5281/zenodo.21721016)

The DOI [`10.5281/zenodo.21721016`](https://doi.org/10.5281/zenodo.21721016) always resolves to the latest version.

> *— for those who would say whence they know.*

## License

No license file is present yet. Until one is added, all rights are reserved by the author; open an issue if you'd like to reuse the grammar, corpus, model, or skill.
