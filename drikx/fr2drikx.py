"""Traducteur à règles français → Drikx (Volet B du corpus T3).

Déterministe, sans LLM. Analyse le français avec spaCy, mappe le vocabulaire via
le dictionnaire canonique (`dict/fr-drikx.json`), réordonne en VSO, pose les
particules (ta, xa, i…), l'aspect (NEUT par défaut) et l'évidentiel (DIR par
défaut — politique (a)), puis laisse l'oracle valider. Haute précision : toute
phrase dont un mot n'est pas couvert ou dont la structure n'est pas gérée est
**écartée, pas approximée** (spec T3).

Portée v1 : propositions DÉCLARATIVES simples (sujet + verbe + objet direct +
obliques simples), présent/passé/futur, affirmatif/négatif. Le reste est écarté.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .engine import Lexicon, aspect_surface, validate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DICT = ROOT / "dict" / "fr-drikx.json"
DEFAULT_LEXICON = ROOT / "Dricks-spec" / "lexique_v2.csv"

SUBJ_PRON = {"je": ("na", "sg"), "tu": ("ti", "sg"), "il": ("ku", "sg"),
             "elle": ("ku", "sg"), "on": ("ku", "sg"), "nous": ("naru", "pl"),
             "vous": ("tiru", "pl"), "ils": ("kuru", "pl"), "elles": ("kuru", "pl")}
OBJ_PRON = {"me": "na", "te": "ti", "le": "ku", "la": "ku", "l'": "ku",
            "les": "kuru", "nous": "naru", "vous": "tiru", "lui": "ku", "leur": "kuru"}
POSS = {"mon": "na", "ma": "na", "mes": "na", "ton": "ti", "ta": "ti", "tes": "ti",
        "son": "ku", "sa": "ku", "ses": "ku", "notre": "naru", "nos": "naru",
        "votre": "tiru", "vos": "tiru", "leur": "kuru", "leurs": "kuru"}
FR_NUM = {"un": "nat", "une": "nat", "deux": "tis", "trois": "kur",
          "quatre": "pilt", "cinq": "xam"}
DEMO_DET = {"ce", "cet", "cette", "ces"}
PREP = {"dans": "pi", "à": "pi", "au": "pi", "aux": "pi", "vers": "xu",
        "pour": "xu", "de": "sa", "depuis": "sa", "du": "sa", "des": "sa"}

EVID_PERIPHRASE = "je l'ai vu"  # politique (a) : DIR par défaut
# verbes-outils / modaux mal représentés lexicalement : on écarte (pas d'approximation)
BLOCK_VERBS = {"avoir", "falloir", "pouvoir", "devoir", "vouloir", "valoir"}


class Skip(Exception):
    """Structure non gérée → phrase écartée."""


@dataclass
class Translation:
    fr: str
    drikx: str
    features: dict


class Translator:
    def __init__(self, dict_path: Path | str = DEFAULT_DICT, model: str = "fr_core_news_sm",
                 lexicon: Path | str = DEFAULT_LEXICON):
        import spacy
        self._nlp = spacy.load(model, disable=["ner"])
        self.fr2dk: dict[str, str] = json.loads(Path(dict_path).read_text(encoding="utf-8"))
        self.lex = Lexicon(lexicon)  # l'oracle valide contre le lexique étendu v2

    def lookup(self, lemma: str, upos: str) -> str | None:
        return self.fr2dk.get(f"{lemma.lower()}|{upos}")

    def lookup_verb(self, tok) -> str | None:
        """Cherche le verbe ; rattrape les lemmatisations -er ratées (donne→donner)."""
        v = self.lookup(tok.lemma_, "VERB")
        if v is None and not tok.lemma_.endswith("r"):
            v = self.lookup(tok.lemma_ + "r", "VERB")
        return v

    # -- syntagme nominal ------------------------------------------------- #

    def build_np(self, tok, consumed: set | None = None) -> tuple[list[str], str]:
        """Renvoie (jetons Drikx, nombre). Lève Skip si non traduisible.
        Marque dans `consumed` les indices de jetons de contenu utilisés."""
        if consumed is not None:
            consumed.add(tok.i)
        if tok.pos_ == "PRON":
            key = tok.text.lower().rstrip("'")
            if key in OBJ_PRON:
                return [OBJ_PRON[key]], "sg"
            raise Skip(f"pronom non géré : {tok.text}")
        if tok.pos_ not in ("NOUN", "PROPN"):
            raise Skip(f"tête de SN non nominale : {tok.pos_}")
        noun = self.lookup(tok.lemma_, "NOUN")
        if noun is None:
            raise Skip(f"nom hors lexique : {tok.lemma_}")

        toks: list[str] = []
        numeral = None
        demo = False
        plural = "Plur" in tok.morph.get("Number")
        poss = None
        statives: list[str] = []

        for ch in tok.children:
            if ch.dep_ == "amod" and ch.pos_ == "ADJ":
                st = self.lookup(ch.lemma_, "ADJ")
                if st is None:
                    raise Skip(f"adjectif hors lexique : {ch.lemma_}")
                statives.append(st)
                if consumed is not None:
                    consumed.add(ch.i)
            elif ch.dep_ == "nummod" or ch.pos_ == "NUM":
                w = ch.lemma_.lower()
                if w not in FR_NUM:
                    raise Skip(f"numéral non géré : {ch.text}")
                numeral = FR_NUM[w]
                if consumed is not None:
                    consumed.add(ch.i)
            elif ch.dep_ == "det":
                d = ch.lemma_.lower()
                if d in POSS:
                    poss = POSS[d]
                elif d in DEMO_DET:
                    demo = True
                # articles définis/indéfinis : ignorés (pas d'article en Drikx)
            elif ch.dep_ in ("nmod", "obl:arg") and ch.pos_ in ("NOUN", "PROPN"):
                raise Skip("génitif nominal complexe non géré")

        if numeral:
            toks.append(numeral)
        toks.append(noun)
        toks += statives
        if demo:
            toks.append("su")
        if plural and not numeral:
            toks.append("ru")
        if poss:
            toks += ["i", poss]
        return toks, ("pl" if (plural or numeral not in (None, "nat")) else "sg")

    # -- traduction ------------------------------------------------------- #

    def _subject_tokens(self, head, consumed: set, extra=None) -> list[str] | None:
        srcs = list(head.children) + (list(extra.children) if extra else [])
        if any(c.dep_ == "nsubj:pass" for c in srcs):
            return None  # pas de passif en Drikx
        subs = [c for c in srcs if c.dep_ in ("nsubj", "expl:subj")]
        if not subs:
            return None
        s = subs[0]
        key = s.text.lower().rstrip("'")  # lemme peu fiable (Elle→lui) : on prend le texte
        if s.pos_ == "PRON" and key in SUBJ_PRON:
            consumed.add(s.i)
            return [SUBJ_PRON[key][0]]
        if s.pos_ in ("NOUN", "PROPN"):
            toks, _ = self.build_np(s, consumed)
            return toks
        return None

    def translate(self, text: str) -> Translation | None:
        text = text.strip()
        if not text or text[-1] in "?!" or len(text) > 120:
            return None  # v1 : déclaratives uniquement
        doc = self._nlp(text)

        roots = [t for t in doc if t.dep_ == "ROOT"]
        if len(roots) != 1:
            return None
        head = roots[0]

        # proposition unique : pas de verbe secondaire subordonné/coordonné
        if any(t.pos_ in ("VERB", "AUX") and t is not head and t.dep_ in
               ("conj", "advcl", "ccomp", "xcomp", "acl", "acl:relcl") for t in doc):
            return None

        neg = any(t.lemma_ in ("ne", "pas") or "Neg" in t.morph.get("Polarity")
                  for t in doc)
        consumed: set[int] = {head.i}

        # écarte les verbes-outils/modaux et les tournures réflexives ou idiomatiques
        if head.lemma_ in BLOCK_VERBS:
            return None
        if any(c.dep_ in ("expl:comp", "expl:pass") for c in head.children):
            return None
        if any(c.pos_ == "PRON" and c.text.lower().rstrip("'") == "se"
               for c in head.children):
            return None

        try:
            # ---- prédicat : verbe, ou copule + adjectif (statif) ----
            stative = None
            vroot = None
            cop_head = None  # nœud portant le sujet en cas de copule
            if any(c.dep_ == "cop" for c in head.children):
                # copule : le prédicat est la tête (adjectif attribut → verbe statif)
                stative = self.lookup(head.lemma_, "ADJ")
                if stative is None:
                    return None
                for c in head.children:
                    if c.dep_ == "cop":
                        consumed.add(c.i)
            else:
                vroot = self.lookup_verb(head)
                if vroot is None:
                    if head.lemma_ == "être":
                        adjs = [c for c in head.children if c.pos_ == "ADJ"]
                        if not adjs:
                            return None
                        stative = self.lookup(adjs[0].lemma_, "ADJ")
                        cop_head = head
                        consumed.add(adjs[0].i)
                        if stative is None:
                            return None
                    else:
                        return None

            fut = "Fut" in head.morph.get("Tense")
            evid = "ka" if fut else "mu"

            # ---- sujet (agent obligatoire) ----
            subj_toks = self._subject_tokens(head, consumed, extra=cop_head)
            if subj_toks is None:
                return None

            # ---- assemblage ----
            dk: list[str] = []
            if fut:
                dk.append("nu")
            if neg:
                dk.append("xa")

            if stative is not None:
                dk.append(f"{stative}-{aspect_surface(stative, 'NEUT')}-{evid}")
                dk += subj_toks
            else:
                dk.append(f"{vroot}-{aspect_surface(vroot, 'NEUT')}-{evid}")
                dk += subj_toks
                for c in head.children:
                    if c.dep_ in ("obj", "dobj"):
                        np, _ = self.build_np(c, consumed)
                        dk += ["ta"] + np
                    elif c.dep_ in ("obl", "obl:arg", "iobj"):
                        prep = [g for g in c.children if g.dep_ == "case"]
                        if not prep or prep[0].lemma_.lower() not in PREP:
                            raise Skip("oblique sans préposition mappable")
                        np, _ = self.build_np(c, consumed)
                        dk += [PREP[prep[0].lemma_.lower()]] + np
            drikx = " ".join(dk)

            # ---- garde-fou : aucun mot de contenu français laissé de côté ----
            leftover = [tt for tt in doc if tt.pos_ in ("NOUN", "VERB", "ADJ", "PROPN", "NUM")
                        and tt.i not in consumed]
            if leftover:
                raise Skip(f"contenu non traduit : {[t.text for t in leftover]}")
        except Skip:
            return None

        if not validate(drikx, self.lex).ok:
            return None
        fr_ref = text.rstrip(".") + f" ({EVID_PERIPHRASE})."
        return Translation(fr=fr_ref, drikx=drikx,
                           features={"type": "stat" if stative else "decl",
                                     "evid": evid, "neg": neg, "fut": fut})
