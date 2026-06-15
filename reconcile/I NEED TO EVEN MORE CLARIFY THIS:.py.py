I NEED TO EVEN MORE CLARIFY THIS:




this is the config file:

{
  "source": {
    "qid": "Q799",
    "label": "Milken Archive"
  },

  "row": {
    "context": "expression",

    "label": {
      "field": "Title"
    },

    "identity": {
      "scope": "expression",
      "fields": ["Title", "Composer"],
      "separator": " | ",
      "strategy": "always_new"
    }
  },

  "contexts": [
    {
      "name": "work",

      "label": {
        "field": "Title"
      },

      "identity": {
        "scope": "work",
        "fields": ["Title"],
        "strategy": "canonicalize"
      }
    }
  ],
  "fields": {

    "Composer": {
      "type": "entity",
      "predicate": "P9",
      "split": true,
      "delimiter": ";",
      "scope": "person",
      "graph": [
        {
          "subject": { "source": "column" },
          "predicate": "P9",
          "object": { "source": "context", "context": "work" }
        }
      ]
    },

    "Spotify Album": {
      "type": "entity",
      "split": true,
      "delimiter": ";",
      "scope": "manifestation",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P10",
          "object": {
            "source": "column",
            "entity_type": "album"
          }
        }
      ]
    },

    "Duration (minutes)": {
      "type": "literal",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P4",
          "object": { "source": "column" }
        }
      ]
    },

    "Year (Known)": {
      "type": "literal",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P5",
          "object": { "source": "column" },
          "certainty": "certain"
        }
      ]
    },

    "Year (Estimated)": {
      "type": "literal",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P5",
          "object": { "source": "column" },
          "certainty": "uncertain"
        }
      ]
    },

    "Commissioning Institution (Name)": {
      "type": "entity",
      "scope": "institution",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P12",
          "object": { "source": "column" }
        }
      ]
    },

    "Primary Genre": {
      "type": "entity",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P13",
          "object": { "source": "column" }
        }
      ]
    },

    "Instrumentation": {
      "type": "entity",
      "split": true,
      "delimiter": ";",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P14",
          "object": { "source": "column" }
        }
      ]
    },

    "Form-General": {
      "type": "entity",
      "split": true,
      "delimiter": "/",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P15",
          "object": { "source": "column" }
        }
      ]
    },

    "Form-Specific (was Tertiary Genre)": {
      "type": "entity",
      "split": true,
      "delimiter": "/",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P15",
          "object": { "source": "column" }
        }
      ]
    },

    "Other": {
      "type": "entity",
      "split": true,
      "delimiter": "/",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P15",
          "object": { "source": "column" }
        }
      ]
    },

    "Sacred": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P13",
          "object": { "source": "constant", "value": "Sacred" }
        }
      ]
    },

    "Secular": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P13",
          "object": { "source": "constant", "value": "Secular" }
        }
      ]
    },

    "Ashkenazi": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P16",
          "object": { "source": "constant", "value": "Ashkenazi" }
        }
      ]
    },

    "Sephardi": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P16",
          "object": { "source": "constant", "value": "Sephardi" }
        }
      ]
    },

    "Israeli": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P16",
          "object": { "source": "constant", "value": "Israeli" }
        }
      ]
    },

    "Mizrahi": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P16",
          "object": { "source": "constant", "value": "Mizrahi" }
        }
      ]
    },

    "Musical": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Musical" }
        }
      ]
    },

    "Conceptual": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Conceptual" }
        }
      ]
    },

    "Textual": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Textual" }
        }
      ]
    },

    "Functional": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Functional" }
        }
      ]
    },

    "Sonic": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "expression" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Sonic" }
        }
      ]
    },

    "Social": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Social" }
        }
      ]
    },

    "Classical": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P18",
          "object": { "source": "constant", "value": "Classical" }
        }
      ]
    },

    "Klezmer": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P18",
          "object": { "source": "constant", "value": "Klezmer" }
        }
      ]
    },

    "Cantorial": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P18",
          "object": { "source": "constant", "value": "Cantorial" }
        }
      ]
    },

    "Folk": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P18",
          "object": { "source": "constant", "value": "Folk" }
        }
      ]
    },

    "Jazz": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P18",
          "object": { "source": "constant", "value": "Jazz" }
        }
      ]
    },

    "Devotional-Solemn": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Devotional-Solemn" }
        }
      ]
    },

    "Popular": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Popular" }
        }
      ]
    },

    "Theatrical": {
      "type": "entity",
      "match": "x",
      "scope": "musical marker",
      "graph": [
        {
          "subject": { "source": "context", "context": "work" },
          "predicate": "P17",
          "object": { "source": "constant", "value": "Theatrical" }
        }
      ]
    }
  }
}


THIS IS A SAMPLE ROW OF THE OPEN REFINE OUTPUT:

id	query	bucket	entity_type	candidate_id	candidate_label	candidate_description	candidate_score	candidate_source	candidate_url	wiki_match
QW1001	Adon olam	expression	entity	Q203	adon olam		1.0	wikibase	https://husky.oarc.ucla.edu/wiki/Item:Q203	y


cache.json looks something like this:

"_counter": 4099,
  "levels": {
    "expression": {
      "Adon olam | Gustave Cohen::4359419072": "QW1001",
      "As the Hart Panteth | Thou Art Enthroned Above | A.J. Davis::4581763584": "QW1010",
      "Barukh Habba (Psalm 118: 26-29) | Amsterdam|Western Sephardi Tradition::4581884480": "QW1016",
      "3 | Amsterdam|Western Sephardi Tradition::4581886272": "QW1023",
      "Ein keloheinu | Amsterdam|Western Sephardi Tradition::4581888064": "QW1028",
      "Empor zu Gott, mein Lobgesang! | Alois Kaiser::4581890048": "QW1031",
      "Liturgical Settings | Edward Stark::4581891904": "QW1036",
      "Liturgical Settings I | Sigmund Schlesinger::4581893824": "QW1042",
      "Liturgical Settings II | Sigmund Schlesinger::4581895872": "QW1047",
      "Mizmor shir l'yom hashabbat | Frederick Kitziger::4581897920": "QW1050",
      "Oh, What is Man | Frederick Kitziger::4581899648": "QW1054",
      "Our Guardian Slumbers Not | C. Weber::4581918144": "QW1059",
      "Selections from the Spicker-Sparger Anthology | Various::4581920064": "QW1064",
      "Shabbat | Amsterdam|Western Sephardi Tradition::4581921856": "QW1068",
      "Shira ḥadasha (Morning Liturgy) | Amsterdam|Western Sephardi Tradition::4581923648": "QW1071",
      "Torah Reading | Amsterdam|Western Sephardi Tradition::4581925440": "QW1074",
      "Union Hymnal Selections | Amsterdam|Western Sephardi Tradition::4581927488": "QW1078",
      "Vay'khullu | Max Graumann::4581929984": "QW1081",
      "A Garden Eastward | Hugo Weisgall::4581931776": "QW1086",
      "American Choral Settings | Traditional::4581950272": "QW1096",
      "Arvit Morocco | Aaron Bensoussan::4581951936": "QW1101",
      "At Grandfather's Knee | Simon Sargon::4581954240": "QW1107",
      "Canto de los Marranos | Marvin Levy::4581956416": "QW1115",
      "Eight Choral Songs for a capella Chorus | Leo Kraft::4581958720": "QW1121",
      "Fantasy On a Sephardi Melody | Robert Starer::4581960576": "QW1127",
      "Five Sephardic Choruses | Samuel Adler::4581962304": "QW1134",
      "Kantigas Ulvidadas | Ofer Ben-Amots::4581964608": "QW1140",
      "L'kha dodi | Aaron Bensoussan::4582016000": "QW1145",
      "L'kha dodi | Samuel Adler::4582018176": "QW1149",
      "Ladino Songs of Love and Suffering | Bruce Adolphe::4582020160": "QW1152",
      "Love's Wounded | Hugo Weisgall::4582022144": "QW1158",
      "Morena | Sid Robinovitch::4582024320": "QW1163",
      "Mystical Procession | Ofer Ben-Amots::4582026176": "QW1168",
      "O Bless the Lord, My Soul | Abraham Binder::4582028352": "QW1172",
      "Prayers My Grandfather Wrote | Mario Castelnuovo-Tedesco::4582030464": "QW1178",
      "Psalm of the Distant Dove | Hugo Weisgall::4582064960": "QW1186",
      "Sacred Service for Sabbath Eve | Mario Castelnuovo-Tedesco::4582066944": "QW1190",
      "Sephardi Kiddush | Traditional::4582068928": "QW1195",
      "Shabbat Nusaḥ S'fard | Emanuel Rosen
.....
 },
    "person": {
      "Gustave Cohen": "QW1003",
      "A.J. Davis": "QW1012",
      "Amsterdam|Western Sephardi Tradition": "QW1018",
      "Alois Kaiser": "QW1033",
      "Edward Stark": "QW1038",
      "Sigmund Schlesinger": "QW1044",
      "Frederick Kitziger": "QW1052",
      "C. Weber": "QW1061",
      "Various": "QW1066",
      "Max Graumann": "QW1083",
      "Hugo Weisgall": "QW1088",
      "Traditional": "QW1098",
      "Aaron Bensoussan": "QW1103",
      "Simon Sargon": "QW1109",
      "Marvin Levy": "QW1117",
      "Leo Kraft": "QW1123",
      "Robert Starer": "QW1129",
      "Samuel Adler": "QW1136",
      "Ofer Ben-Amots": "QW1142",
      "Bruce Adolphe": "QW1154",
      "Sid Robinovitch": "QW1165",
      "Abraham Binder": "QW1174",
      "Mario Castelnuovo-Tedesco": "QW1180",
      "Emanuel Rosenberg": "QW1200",
      "Bruce Roter": "QW1210",
      "Ben Steinberg": "QW1225",
      "Ernest Bloch": "QW1229",

ETC.

plan.json looks something like this:




  {
    "subject": "Adon olam | Gustave Cohen::4359419072",
    "subject_label": "Adon olam",
    "predicate": "LABEL",
    "predicate_label": "LABEL",
    "object": null,
    "object_label": null,
    "object_type": "literal",
    "source": {
      "qid": "Q799",
      "label": "Milken Archive"
    },
    "references": [],
    "qualifiers": []
  },
  {
    "subject": "QW1003",
    "subject_label": "Gustave Cohen",
    "predicate": "P9",
    "predicate_label": "Composer",
    "object": "QW1002",
    "object_label": "Adon olam",
    "object_type": "entity",
    "source": {
      "qid": "Q799",
      "label": "Milken Archive"
    },
    "references": [],
    "qualifiers": []
  },
  {
    "subject": "QW1001",
    "subject_label": "Adon olam",
    "predicate": "P10",
    "predicate_label": "Spotify Album",
    "object": "QW1004",
    "object_label": "Milken Archive Digital Volume 1, Digital Album 1",
    "object_type": "entity",
    "source": {
      "qid": "Q799",
      "label": "Milken Archive"
    },
    "references": [],
    "qualifiers": []
  },
  {
    "subject": "QW1001",

.....

THIS IS THE PIPELINE

Got it. No interpretation beyond what you just stated.

I’ll restate the pipeline **with your exact semantics and no drift**.

---

# 🧠 CORRECT PIPELINE (STRICT OPENREFINE SEMANTICS)

---

# 0. INPUT

OpenRefine export CSV where:

Each row is:

* `id` = local entity (`QW####`)
* `query`
* `candidate_id`
* `wiki_match`
* `candidate_label`, etc.

---

# 1. OPENREFINE DECISION MODEL (IMPORTANT CORRECTION)

Each row contains **explicit user selection state**.

## TWO POSSIBLE VALUES ONLY:

### A. MATCH SELECTED

```text id="a1"
wiki_match = "y"
candidate_id = Q###
```

Meaning:

> user selected an existing Wikibase entity

---

### B. CREATE SELECTED (EXPLICIT TOKEN)

```text id="a2"
candidate_id = "__create__"
```

Meaning:

> user explicitly chose to create a new entity in Wikibase

---

### 🚫 IMPORTANT

There is NO implicit creation.

There is ONLY:

* `"y"` = accept candidate
* `"__create__"` = create new entity

---

# 2. RECONCILIATION PHASE (SYNCHRONOUS EXECUTION)

This phase consumes the OpenRefine CSV and IMMEDIATELY interacts with Wikibase.

For each row:

---

## CASE 1 — ACCEPT EXISTING ENTITY

Condition:

```text id="b1"
wiki_match == "y"
AND candidate_id starts with "Q"
```

Action:

```text id="b2"
QW#### → candidate_id (existing QID)
```

No API creation.

---

## CASE 2 — CREATE NEW ENTITY (EXPLICIT)

Condition:

```text id="c1"
candidate_id == "__create__"
```

Action:

### Step 1: create entity in Wikibase

```text id="c2"
POST wbeditentity → returns QNEW
```

### Step 2: immediately bind result

```text id="c3"
QW#### → QNEW
```

---

# 3. OUTPUT OF RECONCILIATION PHASE (AUTHORITATIVE MAP)

This is generated immediately after processing ALL rows:

```json id="d1"
{
  "QW1001": {
    "qid": "Q203",
    "created": false
  },
  "QW1002": {
    "qid": "Q987",
    "created": true
  }
}
```

---

# 4. CRITICAL PROPERTY (NO AMBIGUITY)

This mapping:

> is the ONLY authoritative identity resolution artifact

It is:

* fully materialized
* fully synchronous
* derived AFTER OpenRefine decisions
* includes all creations

---

# 5. DOWNSTREAM PIPELINE

## 5.1 PLAN REWRITE

Replace:

```text id="e1"
QW#### → QID
```

---

## 5.2 GLOBAL DEDUP

Remove duplicates:

```text id="e2"
(subject, predicate, object)
```

---

## 5.3 WRITEBACK

Pure sink:

* no reconciliation
* no creation
* no mapping

---

# 🧱 FINAL SYSTEM INVARIANTS (NOW CORRECTED TO YOUR SPEC)

## 1. OpenRefine is a decision layer only

It produces exactly:

* `"y"` → accept candidate
* `"__create__"` → create entity

---

## 2. ENTITY CREATION IS EXPLICIT AND SYNCHRONOUS

Triggered ONLY by:

```text id="f1"
candidate_id == "__create__"
```

---

## 3. MAPPING IS PRODUCED AFTER FULL RESOLUTION

Not speculative. Not partial.

---

## 4. QW IS NEVER CREATED IN PIPELINE

QW is:

> pre-existing local identity

---

## 5. WIKIBASE IS THE ONLY SOURCE OF QIDS

* existing QIDs come from search
* new QIDs come from creation step

---
WE NEED FROM # 2. RECONCILIATION PHASE (SYNCHRONOUS EXECUTION) ON!
