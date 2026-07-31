# Drikx — Écriture : le taktil

Contraintes actives (rappel) : phonologie percussive (13 C + 3 V, éjectives réservées au
dégradé épistémique, /h/ en attaque initiale seulement, pas de hiatus), frontière
lexical/grammatical audible (lexical = finale C, grammatical = finale V), accent initial
sauf CRU (l'accent dénonce), lexique dense (pas de racine neuve quand une dérivation
existe).

## 0. Nom et principe

Le système s'appelle **taktil** — mot déjà au lexique : « lame, outil-à-trancher »
(takt + -il instrumental). Écrire, c'est inciser ; la polysémie est gratuite (contrainte 7).

Principe directeur : **chaque trait audible du Drikx devient visible**. L'écriture est
alphabétique, bijective (un phonème = un glyphe, sans digraphe ni ligature), et puise ses
glyphes dans des écritures épigraphiques nées du couteau et du burin — angulaires, sans
courbe de plume, toutes LTR en Unicode :

1. **Vieil italique** (bloc U+10300) pour les consonnes — la charpente, monumentale.
2. **Runique** (bloc U+16A0) pour les voyelles — hampes fines : le liant est
   graphiquement léger.
3. Les **éjectives** prennent la série marquée du vieil italique (les « supplémentaires »
   grecques Θ Φ Ψ) : trois glyphes ronds dans une page d'angles — corps étrangers.
   La faute épistémique se voit comme elle s'entend.

## 1. Inventaire (16 glyphes)

### Consonnes (vieil italique)

| Phonème | Glyphe | Codepoint | Nom source | Note |
|---|---|---|---|---|
| p | 𐌐 | U+10310 | PE | |
| t | 𐌕 | U+10315 | TE | |
| k | 𐌊 | U+1030A | KA | |
| pʼ | 𐌘 | U+10318 | PHE | la lance dans le cercle |
| tʼ | 𐌈 | U+10308 | THE | la cible |
| kʼ | 𐌙 | U+10319 | KHE | le trident — porteur du CRU |
| m | 𐌌 | U+1030C | ME | |
| n | 𐌍 | U+1030D | NE | |
| s | 𐌔 | U+10314 | SE | |
| x | 𐌗 | U+10317 | EKS | |
| h | 𐌇 | U+10307 | HE | initiale de mot uniquement, comme /h/ |
| r | 𐌓 | U+10313 | RE | |
| l | 𐌋 | U+1030B | EL | |

### Voyelles (runique)

| Phonème | Glyphe | Codepoint | Nom source | Note |
|---|---|---|---|---|
| a | ᛆ | U+16C6 | short-twig a | |
| i | ᛁ | U+16C1 | isa | la hampe nue — voyelle minimale |
| u | ᚢ | U+16A2 | uruz | |

### Ponctuation

| Signe | Codepoint | Emploi |
|---|---|---|
| ᛫ | U+16EB | séparateur de mots, optionnel (style lapidaire) |
| ᛭ | U+16ED | clôture d'assertion — jamais après une question |

## 2. Règles orthographiques

1. **Bijection stricte.** Un phonème = un glyphe, dans l'ordre de prononciation.
   Le hiatus étant interdit en Drikx, aucune séquence vocalique n'est jamais à segmenter.
2. **L'accent ne s'écrit pas.** Il est prévisible : initial partout, attiré par le
   morphème CRU quand il est présent — et celui-ci s'annonce déjà par le trident 𐌙.
   Ce qui est calculable ne se paie pas.
3. **L'épenthèse s'écrit comme elle se prononce.** Le /r/ des hiatus et le /a/ des
   frontières morphologiques (-asi/-atu) apparaissent en toutes lettres : takt-asi-mu
   s'écrit 𐌕ᛆ𐌊𐌕ᛆ𐌔ᛁ𐌌ᚢ. L'orthographe est de surface, pas morphophonémique.
4. **Pas de casse, pas de variantes contextuelles.** L'écriture est lapidaire ;
   un seul œil par glyphe.
5. **Les questions ne se clôturent pas.** ᛭ marque une assertion ; l'interrogative,
   qui n'asserte rien (grammaire §2.6), reste ouverte — le blanc final est la place
   de la réponse.

## 3. Les trois isomorphismes (traits structurels)

1. **La frontière lexical/grammatical est lisible au dernier glyphe.** Mot lexical →
   finale consonantique → finit lourd, sur du vieil italique. Mot grammatical → finale
   vocalique → finit fin, sur une rune. La charpente et le liant se distinguent d'un
   coup d'œil, sans dictionnaire (miroir exact du trait structurel n°2 de la phonologie).
2. **L'impératif est de la pierre pure.** Seule forme finie à finale consonantique,
   takt ! s'écrit 𐌕ᛆ𐌊𐌕 — l'ordre se termine sur du monumental, sans liant. Propriété
   émergente de la règle 1, pas un décor.
3. **Le CRU se dénonce graphiquement.** Le morphème -kʼara commence par le trident 𐌙 :
   impossible de le glisser discrètement dans une ligne d'angles. L'accent qu'il attire
   n'a pas besoin d'être écrit — le glyphe fait le travail prosodique à l'œil.

## 4. Spécimens

skim-a-mu na ta silp — « J'ai vu le chat (de mes yeux). »

> 𐌔𐌊ᛁ𐌌ᛆ𐌌ᚢ ᛫ 𐌍ᛆ ᛫ 𐌕ᛆ ᛫ 𐌔ᛁ𐌋𐌐 ᛭

stir-si-mu nark — « L'homme marche (routine) — constaté. »

> 𐌔𐌕ᛁ𐌓𐌔ᛁ𐌌ᚢ ᛫ 𐌍ᛆ𐌓𐌊 ᛭

takt-a-kʼara nark ta purk — « L'homme a (je le crois sans preuve) démoli la maison. »

> 𐌕ᛆ𐌊𐌕ᛆ𐌙ᛆ𐌓ᛆ ᛫ 𐌍ᛆ𐌓𐌊 ᛫ 𐌕ᛆ ᛫ 𐌐ᚢ𐌓𐌊 ᛭

takt-a-ka tʼu ta purk — « Quelqu'un (j'ignore qui) a démoli la maison. »

> 𐌕ᛆ𐌊𐌕ᛆ𐌊ᛆ ᛫ 𐌈ᚢ ᛫ 𐌕ᛆ ᛫ 𐌐ᚢ𐌓𐌊 ᛭

ha skim-a ti ta silp ? — « As-tu vu le chat ? »

> 𐌇ᛆ ᛫ 𐌔𐌊ᛁ𐌌ᛆ ᛫ 𐌕ᛁ ᛫ 𐌕ᛆ ᛫ 𐌔ᛁ𐌋𐌐

takt ! — « Tranche ! »

> 𐌕ᛆ𐌊𐌕

prat-a-ri ku ki skim-a-mu ku ta silp — « Il a dit (rapporté) qu'il avait vu le chat (direct pour lui). »

> 𐌐𐌓ᛆ𐌕ᛆ𐌓ᛁ ᛫ 𐌊ᚢ ᛫ 𐌊ᛁ ᛫ 𐌔𐌊ᛁ𐌌ᛆ𐌌ᚢ ᛫ 𐌊ᚢ ᛫ 𐌕ᛆ ᛫ 𐌔ᛁ𐌋𐌐 ᛭

## 5. Affichage

Tous les blocs choisis sont LTR en Unicode — pas de piège bidirectionnel (le vieux-turc,
envisagé pour les éjectives à cause de ses formes barbelées, a été écarté précisément
parce qu'il est RTL et casserait le rendu en contexte mixte). Le runique s'affiche
presque partout ; le vieil italique demande une police dédiée (Noto Sans Old Italic,
Segoe UI Historic sous Windows).

## 6. Extensions ouvertes (non intégrées)

- **Sceaux évidentiels** (+4 signes) : un signe de clôture dédié par source (DIR / INF /
  RAPPORTÉ / CRU) en fin de proposition, redondant avec le morphème mais permettant de
  balayer la traçabilité d'une inscription d'un coup d'œil. Candidat le plus conforme
  au programme de la langue.
- **Chiffres** : aucun système numéral écrit dans le sketch ; un comptage incisé
  (barres et croix) resterait dans le geste.
- **Logogrammes** pour les racines denses (takt, stark, prat…) : modèle mixte plus
  riche, écarté par défaut — il affaiblit la lisibilité mécanique de l'alphabet.

## QA (résumé)

Score 9/10. Vérifié : bijection phonème ↔ glyphe sans ambiguïté de segmentation
(hiatus interdit en amont) ; éjectives jamais en coda → 𐌈 𐌘 𐌙 jamais en finale de
mot ; 𐌇 restreint à l'initiale comme /h/ ; spécimens conformes glyphe à glyphe à la
grammaire et à la phonologie ; blocs Unicode tous LTR. Ambiguïtés assumées : la rondeur
de 𐌈 𐌘 𐌙 contredit localement l'esthétique angulaire — c'est le trait (la série
marquée doit détonner) ; la coordination u et la voyelle isolée ᚢ restent homographes
comme elles sont homophones (grammaire, QA issue 4). Coquille amont signalée :
01-phonologie.md annonce « 12 consonnes », le tableau en contient 13 — l'écriture
suit le tableau.
