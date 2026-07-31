---
title: Drikx-MT
emoji: 🗣️
colorFrom: indigo
colorTo: gray
sdk: streamlit
app_file: app.py
pinned: false
license: other
base_model: LiquidAI/LFM2-350M
pipeline_tag: translation
tags:
- translation
- constructed-language
- conlang
- drikx
- lfm2
- evidentiality
---

# Drikx: an evidential constructed language and a small-model translator certified by a rule-based oracle

**pseudoluc** — an LLM clone of Luc E. Brunet [Brunet 2025]

---

## Abstract

We present **Drikx**, a constructed language (conlang) whose grammar is designed to make
epistemic and agentive shortcuts *costly to utter*, and **Drikx-MT**, a French ↔ Drikx
neural translator obtained by low-rank fine-tuning of a 350M-parameter model. Drikx makes
three typologically attested features **obligatory and interacting**: verb-initial (VSO)
word order, a four-term **evidential** system marked on every finite assertion, and the
absence of any passive or impersonal construction (the agent is syntactically mandatory).
We formalise the language as an executable **rule-based oracle** that validates, glosses,
and generates Drikx, and we use that oracle to certify a synthetic parallel corpus: *no
training pair enters the set unless the oracle proves it well-formed.* Fine-tuning
`LiquidAI/LFM2-350M` [Liquid AI 2025] with LoRA [Hu et al. 2022] on this corpus yields a
translator that produces oracle-valid Drikx **95.8%** of the time and selects the correct
evidential **98.5%** of the time, learned entirely from an explicit evidential periphrasis
on the French side. We report two controlled ablations — prompt format and lexical
coverage — that isolate what the small model needs. The central design principle
throughout is: **the model proposes, the oracle disposes.**

---

## 1. Introduction

Constructed languages have a long history as instruments of thought rather than mere
communication, from Hildegard of Bingen's twelfth-century *Lingua Ignota* [Higley 2007]
to the modern engineered-language tradition [Okrent 2009]. Drikx belongs to this lineage
with an explicit cognitive brief: its grammar should *penalise* the linguistic moves that
let a speaker evade responsibility — asserting without a source, erasing the agent,
conflating routine with progress.

Drikx was specified not by a human linguist but by **pseudoluc**, a large-language-model
*clone* persona of Luc E. Brunet, produced and evaluated in a study of machine identity
[Brunet 2025]. The persona fixed the design constraints; the remainder of this work — the
rule engine, the oracle, a lexicon grown from 149 to 2 957 entries, a certified parallel
corpus, and the fine-tune documented here — operationalises that specification into a
working machine-translation system.

The contribution is threefold. **(i)** A compact but typologically grounded conlang whose
core features (§2) are individually attested in natural languages but here made jointly
obligatory. **(ii)** An *executable oracle* (§3) that turns grammaticality into a decidable
predicate, enabling a corpus with a hard correctness guarantee (§4). **(iii)** An empirical
study (§5–6) showing that a 350M model, fine-tuned locally at zero marginal cost, learns
this grammar — including nested evidential chains — to near-ceiling oracle validity, and a
diagnosis of where the remaining errors come from.

---

## 2. The Drikx language

### 2.1 Design principles

Three constraints are *firm* (non-negotiable) and mutually reinforcing:

1. **Obligatory evidentiality.** Every finite assertion carries a morpheme encoding the
   speaker's source of information. This generalises the obligatory evidentiality found in
   languages such as Tuyuca, where the verb must select among several evidential values
   [Barnes 1984; Aikhenvald 2004].
2. **No passive, no impersonal.** The agent of an agentive process is syntactically
   obligatory; responsibility cannot be grammatically erased.
3. **Grammaticalised aspect** distinguishing *repetitive* (routine, maintenance) from
   *sequential* (ordered steps toward a new state), in the sense of aspectual typology
   [Comrie 1976].

Word order is **verb–subject–object** (VSO), with the implicational correlates expected of
verb-initial languages — prepositions, noun-before-genitive [Greenberg 1963; Dryer &
Haspelmath 2013].

### 2.2 Phonology

The inventory is deliberately percussive: **12 consonants** — plain stops `p t k`, the
ejectives `pʼ tʼ kʼ`, nasals `m n`, fricatives `s x h`, and `r l` (no voiced stops, no
glides) — and **three vowels** `a i u`, never long or nasal. The maximal syllable is
`(C)(C)V(C)`; two-consonant codas occur word-finally.

Two *structural traits* make morphology audible without a dictionary:

- **Ejectives are grammatical.** `pʼ tʼ kʼ` never appear in lexical roots; they are
  reserved for epistemically *degraded* morphology — above all the CRU evidential (§2.3)
  and the privative prefix `kʼa-`. A root bearing an ejective is, by construction, a
  suspect word.
- **The lexical/grammatical boundary is a phonological signal.** Every lexical word (noun,
  verb, adjective) ends in a **consonant**; every purely grammatical word or affix ends in
  a **vowel**.

Two epenthesis rules repair illicit junctions: `/r/` breaks a hiatus, and `/a/` breaks a
consonant cluster at a morpheme boundary — so the consonant-initial aspects `-si`/`-tu`
surface as `-asi`/`-atu` after a complex coda. Glossing throughout follows the Leipzig
conventions [Comrie et al. 2008].

### 2.3 The evidential system

The finite verb template is **`STEM-ASPECT-EVIDENTIAL`**. Aspect (always realised) is `-a`
NEUT, `-si` REP, `-tu` SEQ; the evidential slot is obligatory on assertions:

| value | gloss | suffix | source |
|---|---|---|---|
| Direct | DIR | `-mu` | perceived / verified by the speaker |
| Inferential | INF | `-ka` | deduced from traces or reasoning |
| Reported | REP.EV | `-ri` | held from a citable other |
| Belief | CRU | `-kʼara` | believed without a source |

The belief value is **marked**: two syllables, an ejective, and it *attracts the stress* —
an epistemic fault the phonology forbids you to mutter. Questions and imperatives, being
non-assertive, take no evidential; the future takes the inferential (`-ka`) on the grounds
that tomorrow is deduced, not perceived.

```
skim-a-mu     na  ta silp
see-NEUT-DIR   1SG ACC cat
"I see the cat (with my own eyes)."
```

Because the agent is obligatory, an unknown agent is named explicitly by the pronoun
`tʼu` ("someone-I-don't-know"), which *forces* the inferential — the only licit substitute
for a passive:

```
takt-a-ka           tʼu          ta purk
break-NEUT-INF       AGT.UNKNOWN   ACC house
"Someone (I don't know who) demolished the house."   [never "the house was demolished"]
```

Evidentiality is **recursive through subordination**: a reported clause keeps *its own*
evidential, so the chain of who-knew-what-through-whom is encoded in the syntax rather than
left to good faith [cf. Aikhenvald 2004 on evidential scope]:

```
prat-a-ri      ku  ki    skim-a-mu     ku  ta silp
speak-NEUT-REP  3SG COMP  see-NEUT-DIR   3SG ACC cat
"He said (I'm told) that he had seen the cat (direct — for him)."
```

### 2.4 Morphosyntax and lexicon

Nouns have no gender and no case; number is an optional postposed particle `ru`. The
accusative is the preposed particle `ta`; there are three prepositions (`pi` in/at, `xu`
toward/for, `sa` from); the genitive is head-initial (`N i GEN`); negation is the preverbal
`xa`; coordination is `u`. Demonstratives are postposed (`su` proximal, `ni` distal),
numerals prenominal, and **adjectives are stative verbs**.

The lexicon is *dense by derivation* [in the spirit of morphological productivity,
Comrie 1989]: few roots, each a semantic cluster, with fine sense supplied by productive
suffixes — `-ar` agentive, `-ut` resultative, `-il` instrumental, `-as` abstract, `-us`
desiderative — and the ejective privative prefix `kʼa-`. The reference lexicon holds
**2 957 entries** and covers ≈ **80 %** of the most frequent French content lemmas, measured
against the Lexique database [New et al. 2004].

---

## 3. A rule-based oracle

The language is realised as an executable module (`drikx.validate`, `.gloss`, `.generate`)
that decides grammaticality across four layers: **phonotactics** (syllabification, licit
onsets/codas, ejective placement, the two epenthesis rules), **verbal morphology** (the
obligatory aspect buffer, the aspect allomorphy, a single evidential slot), **syntax**
(VSO order, obligatory agent, `ta` before objects, future ⇒ `-ka`, `tʼu` ⇒ `-ka`, no
evidential on questions), and the **lexical/grammatical boundary**. Each rejection carries
a specific diagnostic code.

This turns "is this Drikx?" into a decidable predicate. It is the project's arbiter of
truth: **every** datum that reaches the model is first proven well-formed by the oracle.
The principle — *the model proposes, the oracle disposes* — mirrors the use of formal
verifiers to filter model output in program synthesis and reasoning, and the use of
constraint checks to guarantee structured generation.

---

## 4. Corpus construction

We build a synthetic French ↔ Drikx parallel corpus (~17 000 pairs) whose every pair is
oracle-certified before inclusion. It combines three registers:

- **Volet A — systematic templates.** A deterministic generator crosses the four
  evidentials × three aspects × polarity × clause type (declarative, polar and partial
  questions, imperative, future, unknown-agent, evidential-chain subordination) over a
  controlled vocabulary. Crucially, the **French reference carries an explicit evidential
  periphrasis** ("I saw it", "I'm told", "I deduce", "I believe without proof"), giving the
  model a learnable signal for *choosing* the evidential.
- **Volet B — natural sentences.** French sentences from the **Tatoeba** corpus (CC-BY)
  [Tatoeba] are parsed with spaCy [Honnibal & Montani 2017], mapped through a canonical
  bilingual dictionary, reordered to VSO, and translated by the deterministic rule engine.
  Anything outside the covered vocabulary or unhandled syntax is **discarded, never
  approximated** — a high-precision, low-recall policy.
- **Volet C — lexical coverage.** Every lexicon entry is exposed in several simple,
  grammatically correct French frames (articles and conjugations drawn from Lexique
  [New et al. 2004]), so that rare roots are seen by the model.

This is the classic use of *synthetic and rule-generated data* for low-resource MT
[Sennrich et al. 2016a], with the difference that here correctness is not merely plausible
but *proven*.

---

## 5. Fine-tuning

**Model.** `LiquidAI/LFM2-350M` [Liquid AI 2025], a compact hybrid-architecture language
model in the Liquid Foundation Model line whose lineage traces to liquid time-constant
networks [Hasani et al. 2021]. We adapt it with **LoRA** [Hu et al. 2022] (≈1.5M trainable
parameters, 0.4% of the model) using **MLX** [Hannun et al. 2023] on Apple Silicon; a full
run costs minutes and no cloud budget.

**Tokenisation.** A recurring concern for orthographies with unusual symbols is subword
tokenisation, which motivates byte-level models such as ByT5 [Xue et al. 2022] or the
subword machinery of standard NMT [Sennrich et al. 2016b]. We verified that LFM2's
tokenizer **round-trips Drikx losslessly**, including the ejective modifier letter `ʼ`
(U+02BC); no byte-level workaround is required, and the byte-level rationale for ByT5 does
not apply here.

**Format and objective.** The corpus is cast as instruction/response pairs in *both*
directions and presented through the model's **chat template**; the loss is masked to the
response. Training uses AdamW-style optimisation with a fixed learning rate of 2e-4 and a
fixed seed for reproducibility. The full recipe — data preparation, training command, and
evaluation — is scripted end-to-end.

---

## 6. Evaluation

**Metric.** The master metric is **oracle validity**: the fraction of generated Drikx that
passes `validate`. We complement it with **evidential accuracy** (does the generated
evidential match the reference?), exact match, and **chrF** [Popović 2015] (BLEU [Papineni
et al. 2002] is reported in the repository). The oracle-as-judge protocol makes
grammaticality directly measurable, independently of surface overlap.

**Main result (fr → Drikx, held-out test).**

| metric | value |
|---|---|
| **oracle validity** | **95.8 %** |
| **evidential correct** | **98.5 %** |
| exact match | 66.0 % |
| chrF | 89.2 |
| oracle validity — systematic grammar (Volet A) | **99.5 %** |
| oracle validity — natural sentences (Volet B) | **96.3 %** |
| oracle validity — vocabulary frames (Volet C) | 92.3 % |

(fr → Drikx, held-out test of 500 sentences; `LiquidAI/LFM2-350M` + LoRA, 1 800 steps.)

Evidentiality — the hard, interesting part of the language — is learned almost perfectly
from the French periphrasis, *including* the recursive evidential chains of §2.3, which the
model reproduces verbatim.

**Ablation 1 — prompt format.** Training the instruction-tuned base with a raw
completion format (no chat template) collapses to **35.7 %** oracle validity: the model
degenerates on unfamiliar inputs. Routing the same data through the chat template raises
this to **95.9 %** (on the grammar+natural test), the single most important lever.

**Ablation 2 — lexical coverage.** The remaining errors are *lexical, not grammatical*.
Adding Volet C lifts the share of lexicon entries exercised by the corpus from ≈ 26 % to
**67 %**, and oracle validity on **natural** sentences rises from **80.8 %** to **96.3 %**
(and on the vocabulary frames themselves from 80.6 % to 92.3 %). Grammar (Volet A) stays at
≈ 100 %; the frontier is vocabulary breadth — a data problem, not an architecture problem.

---

## 7. Discussion and limitations

The experiments support a clean separation of concerns. A 350M model, given an
oracle-clean and grammar-systematic corpus, acquires a non-trivial morphosyntax —
obligatory evidentiality, VSO, agent obligatoriness, aspect allomorphy, evidential
chaining — to ceiling. What it does *not* fully acquire is the long tail of the lexicon:
roots seen only a few times are sometimes paraphrased with a commoner word (valid Drikx,
but not exact). This is expected and addressable with more per-word exposure.

Limitations: (i) **quality is bounded by the corpus, not the architecture**; (ii) the
natural-sentence register inherits the rule translator's high-precision / low-recall bias,
under-representing idioms and unusual French constructions; (iii) Drikx is a research
artefact, expressive over everyday content but not a general-purpose natural language;
(iv) reported figures are on synthetic test splits drawn from the same generator families
as training — oracle validity is a strong *grammaticality* signal but not a substitute for
human adequacy judgement.

---

## 8. Conclusion

Drikx pairs a linguistically motivated conlang with an executable oracle, and shows that
the pair enables a tiny, locally trained translator to learn an evidential, agent-strict,
verb-initial grammar with near-perfect well-formedness. The recurring lesson — *the model
proposes, the oracle disposes* — is a general recipe wherever a formal checker for the
target exists: let generation be cheap and fallible, and let a verifier make the guarantee.

---

## Usage

```python
from mlx_lm import load, generate

model, tok = load("LiquidAI/LFM2-350M", adapter_path="path/to/this/adapter")

def to_drikx(fr: str) -> str:
    msgs = [{"role": "user",
             "content": f"Traduis cette phrase française en drikx : {fr}"}]
    prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
    return generate(model, tok, prompt=prompt, max_tokens=48).split("\n")[0].strip()

print(to_drikx("Je vois un oiseau rouge."))   # → skim-a-mu na ta tirk rukt
```

The reverse direction uses `"Traduis cette phrase drikx en français : …"`. A Streamlit demo
that shows, side by side, the neural output, the deterministic rule translator, and the
oracle diagnostic is provided in the project repository.

---

## Citation

```bibtex
@article{brunet2025identite,
  author  = {Brunet, Luc E.},
  title   = {Le probl{\`e}me difficile de l'identit{\'e} : {\'e}valuation d'un clone LLM},
  journal = {JITIPEE},
  volume  = {9},
  number  = {2},
  year    = {2025},
  doi     = {10.52497/jitipee.v9i2.381}
}
```

---

## References

- Aikhenvald, A. Y. (2004). *Evidentiality.* Oxford University Press.
- Barnes, J. (1984). Evidentials in the Tuyuca verb. *International Journal of American Linguistics*, 50(3), 255–271.
- Brunet, L. E. (2025). Le problème difficile de l'identité : évaluation d'un clone LLM. *JITIPEE*, 9(2). doi:10.52497/jitipee.v9i2.381.
- Comrie, B. (1976). *Aspect.* Cambridge University Press.
- Comrie, B. (1989). *Language Universals and Linguistic Typology* (2nd ed.). Blackwell.
- Comrie, B., Haspelmath, M., & Bickel, B. (2008). *The Leipzig Glossing Rules.* Max Planck Institute for Evolutionary Anthropology.
- Dryer, M. S., & Haspelmath, M. (eds.) (2013). *The World Atlas of Language Structures Online.* Max Planck Institute for Evolutionary Anthropology.
- Greenberg, J. H. (1963). Some universals of grammar with particular reference to the order of meaningful elements. In *Universals of Language.* MIT Press.
- Hannun, A., et al. (2023). *MLX: An array framework for Apple silicon.* Apple. https://github.com/ml-explore/mlx
- Hasani, R., Lechner, M., Amini, A., Rus, D., & Grosu, R. (2021). Liquid time-constant networks. *AAAI 2021.*
- Higley, S. L. (2007). *Hildegard of Bingen's Unknown Language.* Palgrave Macmillan.
- Honnibal, M., & Montani, I. (2017). *spaCy: Natural language understanding with Bloom embeddings, CNNs and incremental parsing.*
- Hu, E. J., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR 2022.*
- Liquid AI (2025). *LFM2.* https://huggingface.co/LiquidAI/LFM2-350M
- New, B., Pallier, C., Brysbaert, M., & Ferrand, L. (2004). Lexique 2: A new French lexical database. *Behavior Research Methods, Instruments, & Computers*, 36(3), 516–524.
- Okrent, A. (2009). *In the Land of Invented Languages.* Spiegel & Grau.
- Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). BLEU: a method for automatic evaluation of machine translation. *ACL 2002.*
- Popović, M. (2015). chrF: character n-gram F-score for automatic MT evaluation. *WMT 2015.*
- Sennrich, R., Haddow, B., & Birch, A. (2016a). Improving neural machine translation models with monolingual data. *ACL 2016.*
- Sennrich, R., Haddow, B., & Birch, A. (2016b). Neural machine translation of rare words with subword units. *ACL 2016.*
- Tatoeba Project. *Tatoeba: a collection of sentences and translations.* https://tatoeba.org (CC-BY).
- Xue, L., et al. (2022). ByT5: Towards a token-free future with pre-trained byte-to-byte models. *TACL*, 10.

---

*Base model © Liquid AI (`LiquidAI/LFM2-350M`); this fine-tune inherits its license.
Tatoeba data is CC-BY; French lexical statistics are from Lexique.org.*
