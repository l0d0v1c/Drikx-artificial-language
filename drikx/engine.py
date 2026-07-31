"""Drikx — moteur de règles + oracle (T1).

Encode la grammaire du sketch (`Dricks-spec/`) directement en Python : phonotactique,
morphologie verbale (STEM-ASPECT-ÉVIDENTIEL), syntaxe VSO, frontière lexical/grammatical.
Le lexique est chargé depuis le CSV de référence ; les règles ne sont PAS parsées depuis
les .md (elles sont réencodées ici, source de vérité de l'oracle).

API publique : validate(sentence) -> Report ; gloss(sentence) -> str ; generate(clause) -> str.
Le LLM propose, l'oracle dispose.
"""

from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

MODIFIER = "ʼ"  # ʼ éjective (U+02BC) — ne jamais confondre avec ' (U+0027)

# --------------------------------------------------------------------------- #
# Inventaire phonologique (01-phonologie.md)
# --------------------------------------------------------------------------- #

PLAIN_OCCL = {"p", "t", "k"}
EJECTIVES = {"p" + MODIFIER, "t" + MODIFIER, "k" + MODIFIER}
NASALS = {"m", "n"}
FRICATIVES = {"s", "x", "h"}
LIQUIDS = {"r", "l"}
CONSONANTS = PLAIN_OCCL | EJECTIVES | NASALS | FRICATIVES | LIQUIDS
VOWELS = {"a", "i", "u"}

# Attaques complexes licites (2 C). Occlusive+occlusive (distinctes), occlusive+liquide
# (jeu explicite du sketch, /tl/ exclu), /s/+occlusive.
_OCC_OCC = {a + b for a in PLAIN_OCCL for b in PLAIN_OCCL if a != b}
_OCC_LIQ = {"pr", "pl", "tr", "kr", "kl"}
_S_OCC = {"sp", "st", "sk"}
LICIT_ONSET_CLUSTERS = _OCC_OCC | _OCC_LIQ | _S_OCC

# Codas simples : une C parmi p t k s x r l n m — jamais éjective, jamais /h/.
LICIT_CODA_SINGLE = {"p", "t", "k", "s", "x", "r", "l", "n", "m"}

# Codas complexes (finale de mot uniquement). Le sketch ne documente que C+t / C+s,
# mais le lexique atteste largement sonante+obstruante (rk, lp, nt, rs...). Le modèle
# est calibré sur les racines attestées ; divergence consignée dans surprises.md.
_SON = {"r", "l", "n", "m"}
_OBSTR = {"p", "t", "k", "s", "x"}
LICIT_CODA_CLUSTERS = (
    {a + b for a in _SON for b in _OBSTR}          # sonante + obstruante : rk, lt, nk...
    | {a + b for a in {"r", "l"} for b in NASALS}   # sonante + nasale : rn, rm, ln, lm
    | {a + b for a in _OBSTR for b in {"t", "s"}}   # « parfum grec » : kt, pt, st, ks...
)


def to_phonemes(word: str) -> list[str]:
    """Segmente en phonèmes, une éjective = base + U+02BC comptée comme un phonème."""
    word = unicodedata.normalize("NFC", word)
    out: list[str] = []
    i = 0
    while i < len(word):
        ch = word[i]
        if i + 1 < len(word) and word[i + 1] == MODIFIER:
            out.append(ch + MODIFIER)
            i += 2
        else:
            out.append(ch)
            i += 1
    return out


def _is_vowel(ph: str) -> bool:
    return ph in VOWELS


def _licit_onset(cluster: list[str], word_initial: bool) -> bool:
    if not cluster:
        return True  # attaque nulle (seulement licite en tête de mot, géré par l'appelant)
    if any(_is_vowel(c) for c in cluster):
        return False
    if any(c == "h" for c in cluster) and not (word_initial and len(cluster) == 1):
        return False  # /h/ seulement en attaque simple initiale de mot
    if len(cluster) == 1:
        return cluster[0] in CONSONANTS
    if len(cluster) == 2:
        return (cluster[0] + cluster[1]) in LICIT_ONSET_CLUSTERS
    return False


def _licit_coda(cluster: list[str], word_final: bool) -> bool:
    if not cluster:
        return True
    if any(_is_vowel(c) for c in cluster):
        return False
    if any(c in EJECTIVES or c == "h" for c in cluster):
        return False  # jamais d'éjective, jamais /h/ en coda
    if len(cluster) == 1:
        return cluster[0] in LICIT_CODA_SINGLE
    if len(cluster) == 2:
        return word_final and (cluster[0] + cluster[1]) in LICIT_CODA_CLUSTERS
    return False


@dataclass
class PhonoResult:
    ok: bool
    reason: str = ""      # sous-type : HIATUS, INVENTORY, SYLLABLE
    detail: str = ""


def check_phonotactics(word: str) -> PhonoResult:
    """Vrai si le mot admet une syllabation licite (C)(C)V(C)(C-final)."""
    phon = to_phonemes(word)
    if not phon:
        return PhonoResult(False, "EMPTY", "mot vide")
    unknown = [p for p in phon if p not in CONSONANTS and p not in VOWELS]
    if unknown:
        return PhonoResult(False, "INVENTORY", f"phonème(s) hors inventaire : {unknown}")
    for a, b in zip(phon, phon[1:]):
        if _is_vowel(a) and _is_vowel(b):
            return PhonoResult(False, "HIATUS", f"hiatus {a}{b} (deux voyelles se touchent)")

    n = len(phon)

    def parse(i: int, first: bool) -> bool:
        if i == n:
            return True
        for onset_len in (2, 1, 0):
            if onset_len == 0 and not first:
                continue  # attaque nulle interdite en milieu de mot (créerait un hiatus)
            j = i + onset_len
            if j > n:
                continue
            onset = phon[i:j]
            if not _licit_onset(onset, first):
                continue
            if j >= n or not _is_vowel(phon[j]):
                continue  # noyau obligatoire
            k = j + 1  # après le noyau
            for coda_len in (2, 1, 0):
                m = k + coda_len
                if m > n:
                    continue
                coda = phon[k:m]
                if not _licit_coda(coda, word_final=(m == n)):
                    continue
                if parse(m, False):
                    return True
        return False

    if parse(0, True):
        return PhonoResult(True)
    return PhonoResult(False, "SYLLABLE", "syllabation illicite (attaque/coda non conforme)")


def has_ejective(word: str) -> bool:
    return any(p in EJECTIVES for p in to_phonemes(word))


# --------------------------------------------------------------------------- #
# Tables grammaticales (02-grammaire.md) — réencodées, pas parsées
# --------------------------------------------------------------------------- #

ASPECTS = {"a": "NEUT", "si": "REP", "tu": "SEQ"}
# Allomorphes des aspects consonne-initiaux après coda complexe (épenthèse /a/,
# cf. surprises S5 / 02-grammaire §1.1) : -si→-asi, -tu→-atu.
ASPECT_FORMS = {"a": "NEUT", "si": "REP", "tu": "SEQ", "asi": "REP", "atu": "SEQ"}


def _complex_coda(word: str) -> bool:
    """Vrai si le mot finit par un amas de deux consonnes (coda complexe)."""
    ph = to_phonemes(word)
    return len(ph) >= 2 and not _is_vowel(ph[-1]) and not _is_vowel(ph[-2])


def aspect_surface(stem: str, code: str) -> str:
    """Forme de surface de l'aspect pour ce radical : -si/-tu deviennent -asi/-atu
    après une coda complexe (la voyelle-tampon /a/ évite l'amas radical↔aspect)."""
    if code == "NEUT":
        return "a"
    base = {"REP": "si", "SEQ": "tu"}.get(code, "")
    return ("a" + base) if _complex_coda(stem) else base
EVIDENTIALS = {"mu": "DIR", "ka": "INF", "ri": "REP.EV", "k" + MODIFIER + "ara": "CRU"}
DERIV_SUFFIX = {"ar": "AGT", "ut": "RES", "il": "INSTR", "as": "ABSTR", "us": "DESID"}
PRIVATIVE = "k" + MODIFIER + "a"  # préfixe privatif kʼa-

PRONOUNS = {"na": "1SG", "ti": "2SG", "ku": "3SG",
            "naru": "1PL", "tiru": "2PL", "kuru": "3PL"}
AGT_INC = "t" + MODIFIER + "u"       # tʼu — agent inconnu, force -ka
TAM = {"pa": "PST", "nu": "FUT"}
NEG = "xa"
ACC = "ta"
PLURAL = "ru"
GEN = "i"
COORD = "u"
Q_POLAR = "ha"
COMP = "ki"
PREPS = {"pi": "in", "xu": "to", "sa": "from"}
DEMOS = {"su": "PROX", "ni": "DIST"}
INTERJ = {"p" + MODIFIER + "a": "BS"}
APPROX = {"k" + MODIFIER + "u": "APPROX"}

FUTURE_EVID = "ka"  # le futur exige l'inférentiel


# --------------------------------------------------------------------------- #
# Lexique (03-lexique.csv)
# --------------------------------------------------------------------------- #

DEFAULT_LEXICON = Path(__file__).resolve().parents[1] / "Dricks-spec" / "03-lexique.csv"


@dataclass
class LexEntry:
    ipa: str
    pos: str
    translation: str
    grammar: str
    derivation: str
    notes: str

    @property
    def gloss(self) -> str:
        t = self.translation.split("/")[0].strip().split()
        return (t[0] if t else self.ipa).lower()


class Lexicon:
    """Charge le CSV et classe chaque forme (racine, dérivé, mot grammatical)."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_LEXICON
        self.entries: dict[str, LexEntry] = {}
        self._load()

    def _load(self) -> None:
        text = self.path.read_text(encoding="utf-8")
        text = unicodedata.normalize("NFC", text)
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            ipa = row["ipa"].strip()
            entry = LexEntry(
                ipa=ipa,
                pos=row["pos"].strip(),
                translation=(row.get("translation") or "").strip(),
                grammar=(row.get("grammar") or "").strip(),
                derivation=(row.get("derivation") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )
            key = ipa.strip("-")  # suffixes stockés sans le tiret
            self.entries[key] = entry

    # -- classification d'une forme nue (sans tiret) ------------------------- #

    def category(self, form: str) -> str:
        """Renvoie une catégorie fonctionnelle pour la forme donnée."""
        if form in PRONOUNS:
            return "pronoun"
        if form == AGT_INC:
            return "agt_inc"
        if form in TAM:
            return "tam"
        if form == NEG:
            return "neg"
        if form == ACC:
            return "acc"
        if form == PLURAL:
            return "plural"
        if form == GEN:
            return "gen"
        if form == COORD:
            return "coord"
        if form == Q_POLAR:
            return "qpolar"
        if form == COMP:
            return "comp"
        if form in PREPS:
            return "prep"
        if form in DEMOS:
            return "demo"
        if form in INTERJ:
            return "interj"
        if form in APPROX:
            return "approx"
        entry = self.entries.get(form)
        if entry is None:
            return "unknown"
        pos = entry.pos
        if pos == "n":
            return "noun"
        if pos == "v":
            return "verb"
        if pos == "v.stat":
            return "stative"
        if pos == "num":
            return "num"
        if pos == "pro.int":
            return "interro"
        if pos == "adv":
            return "adverb"
        if pos in ("pro",):
            return "pronoun"
        return pos  # part / prep / conj / intj tombent ici si non capturés

    def is_verbal_stem(self, stem: str) -> bool:
        e = self.entries.get(stem)
        return e is not None and e.pos in ("v", "v.stat")

    def is_stative(self, form: str) -> bool:
        e = self.entries.get(form)
        return e is not None and e.pos == "v.stat"

    def is_root(self, form: str) -> bool:
        e = self.entries.get(form)
        return e is not None and e.derivation == "racine"

    def gloss_of(self, form: str) -> str:
        e = self.entries.get(form)
        return e.gloss if e else form


_DEFAULT_LEX: Lexicon | None = None


def get_lexicon() -> Lexicon:
    global _DEFAULT_LEX
    if _DEFAULT_LEX is None:
        _DEFAULT_LEX = Lexicon()
    return _DEFAULT_LEX


# --------------------------------------------------------------------------- #
# Rapport de validation
# --------------------------------------------------------------------------- #

@dataclass
class Issue:
    code: str
    message: str
    span: str = ""

    def __str__(self) -> str:
        loc = f" [{self.span}]" if self.span else ""
        return f"{self.code}: {self.message}{loc}"


@dataclass
class Report:
    ok: bool
    issues: list[Issue] = field(default_factory=list)
    clause: "Clause | None" = None

    def __bool__(self) -> bool:
        return self.ok

    def codes(self) -> list[str]:
        return [i.code for i in self.issues]

    def has(self, code: str) -> bool:
        return any(i.code == code for i in self.issues)

    def has_family(self, prefix: str) -> bool:
        return any(i.code.startswith(prefix) for i in self.issues)

    def __str__(self) -> str:
        head = "OK" if self.ok else "REJET"
        return head + "".join("\n  - " + str(i) for i in self.issues)


# --------------------------------------------------------------------------- #
# AST
# --------------------------------------------------------------------------- #

@dataclass
class Verb:
    surface: str
    root: str
    deriv: list[str]
    stem: str
    aspect: str | None       # code NEUT/REP/SEQ
    evid: str | None         # code DIR/INF/REP.EV/CRU
    imperative: bool = False
    morphs: list[str] = field(default_factory=list)
    evid_count: int = 0
    aspect_form: str | None = None   # forme de surface écrite (a/si/asi/tu/atu)


@dataclass
class NP:
    head: str
    head_cat: str
    num: str | None = None
    mods: list[str] = field(default_factory=list)     # statifs attributifs
    demo: str | None = None                            # su / ni (surface)
    plural: bool = False
    gen: "NP | None" = None
    coord: list["NP"] = field(default_factory=list)


@dataclass
class Arg:
    role: str            # NOM / ACC / OBL
    np: NP
    prep: str | None = None


@dataclass
class Clause:
    verb: Verb | None = None
    neg: bool = False
    tam: str | None = None            # PST / FUT
    qtype: str | None = None          # polar / partial
    qword: str | None = None
    subject: Arg | None = None
    args: list[Arg] = field(default_factory=list)
    adverbs: list[str] = field(default_factory=list)
    subordinate: "Clause | None" = None
    subordinator: str | None = None   # 'ki'


# --------------------------------------------------------------------------- #
# Parseur
# --------------------------------------------------------------------------- #

class _Parser:
    def __init__(self, lex: Lexicon):
        self.lex = lex
        self.issues: list[Issue] = []

    def add(self, code: str, message: str, span: str = "") -> None:
        self.issues.append(Issue(code, message, span))

    # -- verbe ------------------------------------------------------------- #

    def parse_verb(self, tok: str) -> Verb:
        morphs = tok.split("-")
        evid = None
        evid_count = sum(1 for m in morphs if m in EVIDENTIALS)
        if evid_count > 1:
            self.add("DOUBLE_EVIDENTIAL",
                     "plus d'un évidentiel dans le verbe (un seul slot final)", tok)
        body = morphs
        if morphs[-1] in EVIDENTIALS:
            evid = EVIDENTIALS[morphs[-1]]
            body = morphs[:-1]
        aspect = None
        aspect_form = None
        stem_morphs = body
        if body and body[-1] in ASPECT_FORMS:
            aspect_form = body[-1]
            aspect = ASPECT_FORMS[body[-1]]
            stem_morphs = body[:-1]
        if not stem_morphs:
            stem_morphs = [morphs[0]]
        root = stem_morphs[0]
        deriv = stem_morphs[1:]
        stem = "".join(stem_morphs)
        return Verb(surface=tok, root=root, deriv=deriv, stem=stem,
                    aspect=aspect, evid=evid, morphs=morphs, evid_count=evid_count,
                    aspect_form=aspect_form)

    def validate_verb_form(self, v: Verb) -> None:
        # phonotactique du mot verbal entier (voyelles-tampon incluses)
        joined = "".join(v.morphs)
        pr = check_phonotactics(joined)
        if not pr.ok:
            self.add(f"PHONO_{pr.reason}", f"phonotactique : {pr.detail}", v.surface)
        # aspect obligatoire (voyelle-tampon du template)
        if v.aspect is None:
            self.add("MISSING_ASPECT",
                     "slot aspect absent ou invalide (template STEM-ASPECT-ÉVID)", v.surface)
        # allomorphie d'aspect : -si/-tu deviennent -asi/-atu après coda complexe
        elif v.aspect in ("REP", "SEQ"):
            exp = aspect_surface(v.stem, v.aspect)
            if v.aspect_form != exp:
                self.add("ASPECT_EPENTHESIS",
                         f"aspect {v.aspect} : forme attendue -{exp} après « {v.stem} » "
                         f"(épenthèse /a/), reçu -{v.aspect_form}", v.surface)
        # dérivations valides
        for d in v.deriv:
            if d not in DERIV_SUFFIX:
                self.add("BAD_DERIVATION", f"suffixe dérivationnel inconnu : -{d}", v.surface)
        # racine / radical connus
        if not self.lex.is_verbal_stem(v.stem):
            root_known = self.lex.is_verbal_stem(v.root)
            privative = v.stem.startswith(PRIVATIVE) and self.lex.is_root(v.stem[len(PRIVATIVE):])
            if not root_known and not privative:
                if has_ejective(v.root):
                    self.add("EJECTIVE_IN_ROOT",
                             f"éjective dans une racine lexicale : {v.root}", v.surface)
                else:
                    self.add("UNKNOWN_ROOT", f"racine verbale inconnue : {v.root}", v.surface)
        # frontière : la racine lexicale doit finir par une consonne
        rp = to_phonemes(v.root)
        if rp and _is_vowel(rp[-1]) and not v.root.startswith(PRIVATIVE):
            self.add("BOUNDARY", f"racine lexicale à finale vocalique : {v.root}", v.surface)

    # -- syntagme nominal --------------------------------------------------- #

    def parse_np(self, toks: list[str], i: int):
        n = len(toks)
        if i >= n:
            return None, i
        num = None
        cat = self.lex.category(toks[i])
        if cat == "num":
            num = toks[i]
            i += 1
            if i >= n:
                self.add("NUMERAL_NO_NOUN", f"numéral sans nom : {num}", num)
                return None, i
            cat = self.lex.category(toks[i])
        if cat not in ("noun", "pronoun", "agt_inc", "interro"):
            return None, i
        head = toks[i]
        head_cat = cat
        i += 1
        np = NP(head=head, head_cat=head_cat, num=num)
        while i < n:
            t = toks[i]
            tcat = self.lex.category(t)
            if tcat == "stative":
                np.mods.append(t)
                i += 1
            elif tcat == "demo" and np.demo is None:
                np.demo = t
                i += 1
            elif t == PLURAL:
                if num is not None:
                    self.add("NUMERAL_WITH_PLURAL",
                             "numéral et pluriel ru sur le même nom (le nombre ne se paie "
                             "pas deux fois)", f"{num} {head} ru")
                np.plural = True
                i += 1
            elif t == GEN:
                gnp, ni = self.parse_np(toks, i + 1)
                if gnp is None:
                    self.add("BAD_GENITIF", "lien génitif i sans complément nominal", t)
                    i += 1
                else:
                    np.gen = gnp
                    i = ni
            else:
                break
        return np, i

    # -- clause ------------------------------------------------------------- #

    def parse_clause(self, toks: list[str], subordinate: bool = False) -> Clause:
        cl = Clause()
        n = len(toks)
        i = 0
        # zone préverbale
        while i < n:
            t = toks[i]
            cat = self.lex.category(t)
            if t == NEG:
                cl.neg = True
                i += 1
            elif cat == "tam":
                cl.tam = TAM[t]
                i += 1
            elif t == Q_POLAR:
                cl.qtype = "polar"
                i += 1
            elif cat == "interro":
                cl.qtype = "partial"
                cl.qword = t
                i += 1
            elif t == ACC:
                self.add("MISPLACED_ACC",
                         "marqueur d'objet ta en position préverbale", t)
                i += 1
            else:
                break

        if i >= n:
            self.add("NO_VERB", "aucun verbe dans la proposition")
            return cl

        vtok = toks[i]
        if "-" in vtok:
            v = self.parse_verb(vtok)
            self.validate_verb_form(v)
            cl.verb = v
            i += 1
        else:
            vcat = self.lex.category(vtok)
            if vcat in ("verb", "stative"):
                # radical nu = impératif (seule forme finie à finale consonantique)
                v = Verb(surface=vtok, root=vtok, deriv=[], stem=vtok,
                         aspect=None, evid=None, imperative=True, morphs=[vtok])
                pr = check_phonotactics(vtok)
                if not pr.ok:
                    self.add(f"PHONO_{pr.reason}", f"phonotactique : {pr.detail}", vtok)
                cl.verb = v
                i += 1
            else:
                self.add("VSO_ORDER",
                         f"le verbe n'est pas en tête (trouvé « {vtok} », {vcat})", vtok)
                return cl

        # zone post-verbale : sujet puis objets/obliques/adverbes
        last_np: NP | None = None
        object_before_subject = False
        while i < n:
            t = toks[i]
            tcat = self.lex.category(t)
            if t == COMP:
                cl.subordinator = t
                cl.subordinate = self.parse_clause(toks[i + 1:], subordinate=True)
                break
            if t == ACC:
                np, ni = self.parse_np(toks, i + 1)
                if np is None:
                    self.add("BAD_ACC", "marqueur ta sans objet nominal", t)
                    i += 1
                    continue
                if cl.subject is None and not cl.verb.imperative:
                    object_before_subject = True
                cl.args.append(Arg("ACC", np))
                last_np = np
                i = ni
            elif tcat == "prep":
                np, ni = self.parse_np(toks, i + 1)
                if np is None:
                    self.add("DANGLING_PREP", f"préposition {t} sans complément", t)
                    i += 1
                    continue
                cl.args.append(Arg("OBL", np, prep=t))
                last_np = np
                i = ni
            elif t == COORD:
                np, ni = self.parse_np(toks, i + 1)
                if np is None:
                    self.add("BAD_COORD", "coordination u sans second membre", t)
                    i += 1
                    continue
                if last_np is not None:
                    last_np.coord.append(np)
                else:
                    self.add("BAD_COORD", "coordination u sans premier membre", t)
                i = ni
            elif tcat == "adverb":
                cl.adverbs.append(t)
                i += 1
            else:
                np, ni = self.parse_np(toks, i)
                if np is None:
                    self.add("STRAY_TOKEN", f"jeton inattendu : {t}", t)
                    i += 1
                    continue
                if cl.subject is None:
                    cl.subject = Arg("NOM", np)
                else:
                    self.add("MISSING_ACC",
                             f"nom non marqué en position d'objet (ta manquant) : {np.head}",
                             np.head)
                    cl.args.append(Arg("ACC", np))
                last_np = np
                i = ni

        # OSV réel : un objet a précédé un sujet qui existe bel et bien
        if object_before_subject and cl.subject is not None:
            self.add("VSO_ORDER", "objet avant le sujet (VSO : S précède O)",
                     cl.verb.surface if cl.verb else "")

        self._check_semantics(cl, subordinate)
        return cl

    # -- règles sémantico-syntaxiques -------------------------------------- #

    def _check_semantics(self, cl: Clause, subordinate: bool) -> None:
        v = cl.verb
        if v is None:
            return

        is_question = cl.qtype is not None and not subordinate
        is_imperative = v.imperative

        if is_imperative:
            # radical nu : pas d'évidentiel, pas d'aspect, sujet implicite 2SG
            if v.evid is not None or v.aspect is not None:
                self.add("IMPERATIVE_INFLECTED",
                         "impératif fléchi (le radical nu est la seule forme sans liant)",
                         v.surface)
            return

        # évidentiel : slot final
        if is_question:
            if v.evid is not None:
                self.add("QUESTION_HAS_EVIDENTIAL",
                         "évidentiel sur une interrogative (la question EST la requête de "
                         "source ; slot vide)", v.surface)
        else:
            if v.evid is None:
                self.add("MISSING_EVIDENTIAL",
                         "assertion sans évidentiel (toute proposition finie porte sa source)",
                         v.surface)

        # futur ⇒ inférentiel -ka
        if cl.tam == "FUT" and v.evid is not None and v.morphs and v.morphs[-1] != FUTURE_EVID:
            self.add("FUTURE_REQUIRES_INF",
                     "le futur exige l'inférentiel -ka (on ne perçoit pas demain)", v.surface)

        # tʼu ⇒ inférentiel -ka
        subj_heads = []
        if cl.subject:
            subj_heads = [cl.subject.np.head] + [c.head for c in cl.subject.np.coord]
        if AGT_INC in subj_heads and (not v.morphs or v.morphs[-1] != FUTURE_EVID):
            self.add("TU_REQUIRES_INF",
                     "l'agent inconnu tʼu force l'évidentiel -ka (on infère l'agent)",
                     v.surface)

        # agent syntaxiquement obligatoire (pas de passif ni d'impersonnel)
        if not is_question and cl.subject is None:
            self.add("MISSING_AGENT",
                     "agent absent (VSO : sujet obligatoire ; tʼu comble l'ignorance, "
                     "jamais de passif)", v.surface)


# --------------------------------------------------------------------------- #
# API publique
# --------------------------------------------------------------------------- #

def _tokenize(sentence: str) -> list[str]:
    s = unicodedata.normalize("NFC", sentence).strip()
    s = s.rstrip("?!").strip()
    return [t for t in s.split() if t]


def parse(sentence: str, lex: Lexicon | None = None) -> tuple[Clause, list[Issue]]:
    lex = lex or get_lexicon()
    p = _Parser(lex)
    toks = _tokenize(sentence)
    if not toks:
        p.add("EMPTY", "phrase vide")
        return Clause(), p.issues
    cl = p.parse_clause(toks)
    return cl, p.issues


def validate(sentence: str, lex: Lexicon | None = None) -> Report:
    """Oracle : renvoie un Report (ok + diagnostics) pour la phrase donnée."""
    cl, issues = parse(sentence, lex)
    return Report(ok=(len(issues) == 0), issues=issues, clause=cl)


# Catégories lexicales à finale consonantique (mots lexicaux).
LEXICAL_POS = {"n", "v", "v.stat", "num", "pro.int", "adv"}
# Suffixes dérivationnels licites (mêmes que DERIV_SUFFIX) + préfixe privatif.
_VALID_SUFFIXES = set(DERIV_SUFFIX) | {"ar", "ut", "il", "as", "us"}


def validate_lexeme(ipa: str, pos: str, derivation: str = "racine",
                    lex: Lexicon | None = None,
                    seen: set[str] | None = None) -> Report:
    """Oracle au niveau de l'entrée lexicale (pour l'expansion T2).

    Vérifie : phonotactique, absence de doublon (lexique + `seen`), finale
    consonantique des mots lexicaux, éjectives interdites en racine (le préfixe
    privatif kʼa- reste licite). Renvoie un Report.
    """
    lex = lex or get_lexicon()
    issues: list[Issue] = []
    form = unicodedata.normalize("NFC", ipa).strip()

    if not form:
        issues.append(Issue("EMPTY", "ipa vide", ipa))
        return Report(ok=False, issues=issues)

    # phonotactique
    pr = check_phonotactics(form)
    if not pr.ok:
        issues.append(Issue(f"PHONO_{pr.reason}", f"phonotactique : {pr.detail}", form))

    # doublon (lexique de référence ou déjà retenu dans cette passe)
    if form.strip("-") in lex.entries:
        issues.append(Issue("DUPLICATE", f"déjà au lexique : {form}", form))
    elif seen is not None and form in seen:
        issues.append(Issue("DUPLICATE", f"doublon dans la génération : {form}", form))

    # frontière lexical/grammatical : mot lexical ⇒ finale consonantique
    if pos in LEXICAL_POS:
        phon = to_phonemes(form)
        if phon and _is_vowel(phon[-1]):
            issues.append(Issue("BOUNDARY",
                                f"mot lexical à finale vocalique : {form}", form))

    # éjectives interdites en racine (privatif kʼa- excepté)
    is_privative = form.startswith(PRIVATIVE) or "privatif" in derivation.lower()
    if derivation.strip().lower() == "racine" and has_ejective(form) and not is_privative:
        issues.append(Issue("EJECTIVE_IN_ROOT",
                            f"éjective dans une racine lexicale : {form}", form))

    return Report(ok=(len(issues) == 0), issues=issues)


# --------------------------------------------------------------------------- #
# Glose (Leipzig)
# --------------------------------------------------------------------------- #

def _gloss_np(np: NP, lex: Lexicon) -> list[str]:
    out: list[str] = []
    if np.num:
        out.append(lex.gloss_of(np.num))
    out.append(lex.gloss_of(np.head) if np.head_cat in ("noun", "interro")
               else _gram_gloss(np.head, lex))
    for m in np.mods:
        out.append(lex.gloss_of(m))
    if np.plural:
        out.append("PL")
    if np.demo:
        out.append(DEMOS[np.demo])
    if np.gen:
        out.append("GEN")
        out.extend(_gloss_np(np.gen, lex))
    for c in np.coord:
        out.append("and")
        out.extend(_gloss_np(c, lex))
    return out


def _gram_gloss(form: str, lex: Lexicon) -> str:
    if form in PRONOUNS:
        return PRONOUNS[form]
    if form == AGT_INC:
        return "AGT.INC"
    return lex.gloss_of(form)


def _gloss_verb(v: Verb, lex: Lexicon) -> str:
    if v.imperative:
        return lex.gloss_of(v.root) + ".IMP"
    parts = [lex.gloss_of(v.root)]
    for d in v.deriv:
        parts.append(DERIV_SUFFIX.get(d, d))
    if v.aspect:
        parts.append(v.aspect)
    if v.evid:
        parts.append(v.evid)
    return "-".join(parts)


def _gloss_clause(cl: Clause, lex: Lexicon) -> list[str]:
    out: list[str] = []
    if cl.qtype == "partial" and cl.qword:
        out.append(lex.gloss_of(cl.qword))
    if cl.qtype == "polar":
        out.append("Q")
    if cl.neg:
        out.append("NEG")
    if cl.tam:
        out.append(cl.tam)
    if cl.verb:
        out.append(_gloss_verb(cl.verb, lex))
    if cl.subject:
        out.extend(_gloss_np(cl.subject.np, lex))
    for a in cl.args:
        if a.role == "ACC":
            out.append("ACC")
        elif a.role == "OBL" and a.prep:
            out.append(PREPS.get(a.prep, a.prep))
        out.extend(_gloss_np(a.np, lex))
    for adv in cl.adverbs:
        out.append(lex.gloss_of(adv))
    if cl.subordinate:
        out.append("COMP")
        out.extend(_gloss_clause(cl.subordinate, lex))
    return out


def gloss(sentence: str, lex: Lexicon | None = None) -> str:
    """Glose Leipzig d'une phrase (ligne de gloses alignée sur les mots)."""
    lex = lex or get_lexicon()
    cl, _ = parse(sentence, lex)
    return " ".join(_gloss_clause(cl, lex))


# --------------------------------------------------------------------------- #
# Génération (AST -> surface)
# --------------------------------------------------------------------------- #

def _gen_np(np: NP) -> list[str]:
    out: list[str] = []
    if np.num:
        out.append(np.num)
    out.append(np.head)
    out.extend(np.mods)
    if np.plural:
        out.append(PLURAL)
    if np.demo:
        out.append(np.demo)
    if np.gen:
        out.append(GEN)
        out.extend(_gen_np(np.gen))
    for c in np.coord:
        out.append(COORD)
        out.extend(_gen_np(c))
    return out


def _gen_clause(cl: Clause) -> list[str]:
    out: list[str] = []
    if cl.qtype == "partial" and cl.qword:
        out.append(cl.qword)
    if cl.qtype == "polar":
        out.append(Q_POLAR)
    if cl.neg:
        out.append(NEG)
    if cl.tam:
        out.append({"PST": "pa", "FUT": "nu"}[cl.tam])
    if cl.verb:
        out.append(cl.verb.surface)
    if cl.subject:
        out.extend(_gen_np(cl.subject.np))
    for a in cl.args:
        if a.role == "ACC":
            out.append(ACC)
        elif a.role == "OBL" and a.prep:
            out.append(a.prep)
        out.extend(_gen_np(a.np))
    out.extend(cl.adverbs)
    if cl.subordinate:
        out.append(cl.subordinator or COMP)
        out.extend(_gen_clause(cl.subordinate))
    return out


def generate(clause: Clause) -> str:
    """Reconstruit la chaîne de surface depuis un AST Clause."""
    return " ".join(_gen_clause(clause))
