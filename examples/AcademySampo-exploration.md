# Data Schema Exploration: AcademySampo

This is a example of using the Data Shape Server (DSS) showing information
about the available knowledge graph schemas and exploring the AcademySampo
academic-prosopography knowledge graph in detail.

This conversation took place in the Claude Desktop application using 
the Opus 4.8 model.

A full transcript of this conversation is available online:
- https://claude.ai/share/dd13bf64-83aa-412a-a7f1-3b353386abd9

---

## What data schemas are available?

The DSS system exposes a large collection of knowledge-graph schemas,
each backed by a SPARQL endpoint. They span many domains:

- **Large general knowledge graphs:** DBpedia (~483k classes), Wikidata (~85k classes)
- **Government / public data:** DataEuropaEU, data.gov.cz, Camera dei Deputati, INSEE,
  UK Land Registry, Swiss LINDAS, German GND/DNB, The Gazette (UK), Linked Saeima
- **Life sciences / biomedicine:** UniProt, Bio2RDF, RIKEN MetaDB, RDF Portal (NCBI,
  ProteinAtlas), MeSH/NLM, Rhea-DB, MetaNetX, Cellosaurus, OMA, WikiPathways,
  Glycoinfo/GlyGen, IMGT, BacDive, BRENDA, nextProt, DisGeNET, TaxRef
- **Cultural heritage / libraries (GLAM):** Europeana, Muziekweb, DOREMUS, JPSearch,
  Cervantes Virtual, BnF, BNE, Libris, the Sampo projects, Getty TGN, SilkNow
- **Finance / economics:** ISO 20022 (~3,782 classes), ESCO, CSSZ
- **Niche / thematic:** Nobel Prizes, Mondial, Star Wars, DBLP, WordNet, AGROVOC, OpenEI
- **Vocabularies / thesauri:** LOV (~2,461), MMISW, UNESCO, NERC

### Exact count

**399** schema entries are loaded in total. Note that many are duplicates or variants
of the same underlying endpoint (e.g. `s26_`, `http_`, and `https_` prefixed versions
point to the same SPARQL URLs).

---

## AcademySampo

### What it is

AcademySampo (`yoma` / *ylioppilasmatrikkeli*, "student register") is part of the Finnish
"Sampo" family of cultural-heritage knowledge graphs published by the Semantic Computing
Research Group (SeCo) at `ldf.fi`. It models Finnish university students and academics
through history, built largely from the *Ylioppilasmatrikkeli* student registers
(the registry entries `D1640` and `D1853` refer to the 1640 and 1853 editions).

- **Schema namespace:** `http://ldf.fi/schema/yoma/`
- **SPARQL endpoint:** `http://ldf.fi/yoma/sparql`
- **Class count:** ~268
- **Registry tag:** `che25`

> Note: the registry entry named `AcademySampoX` currently returns "unknown ontology"
> from the live introspection endpoint, so data here was pulled from an equivalent
> variant (`http_ldf_fi_yoma_sparql`) pointing at the same endpoint.

### Top classes

| Rank | Class | Instances | Represents |
|------|-------|-----------|------------|
| 1 | rdf:Statement | 187,324 | Reified RDF statements (provenance/annotation) |
| 2 | :Distance | 123,197 | Computed distances (e.g. between places) |
| 3 | :Label | 93,050 | Name/label objects |
| 4 | :Timespan | 62,575 | Time periods for events |
| 5 | :ReferencedPerson | 47,246 | Persons mentioned/cited in sources |
| 6 | :Death | 42,815 | Death events |
| 7 | :Study | 42,052 | Study/education events |
| 8 | :Career | 41,760 | Career events |
| 9 | y-rel:Wife (f11) | 34,606 | Wife relationship |
| 10 | y-rel:Husband (f12) | 31,276 | Husband relationship |
| 11 | :Coordinate | 27,978 | Geographic coordinates |
| 12 | :Person | 27,978 | **The central entity — academic persons** |
| 13 | y-rel:Son (f6) | 25,076 | Son relationship |
| 14 | :Birth | 24,944 | Birth events |
| 15 | y-rel:Daughter-in-law (f73) | 20,497 | In-law relationship |

The largest classes are infrastructural (statements, distances, labels, timespans)
rather than biographical. `Person` sits at ~28k instances but is referenced over
600k times across the graph. Family-relationship classes (`y-rel:*`) collectively
form a large share of the data.

### Top properties

| Rank | Property | Count | Role |
|------|----------|-------|------|
| 1 | rdf:type | 1,137,110 | Class membership (structural) |
| 2 | skos:prefLabel | 735,576 | Preferred label / name (data) |
| 3 | :link_by | 395,958 | Generic provenance/linking |
| 4 | biocrm:has_family_relation | 324,736 | Family relationship (bio-CRM core) |
| 5 | biocrm:inheres_in | 275,610 | Role/relation attaches to a person |
| 6 | y-rel:relates_to | 246,394 | Relation → person link |
| 7 | schema:date | 221,540 | Event date → Timespan |
| 8 | rdf:object / subject / predicate | 187,324 each | Reified statement parts |
| 9 | :has_event | 171,402 | Person → life event |
| 10 | :event_no | 157,630 | Event ordering index (data) |
| 11 | schema:place | 138,090 | Event → place |
| 12 | :inferred | 123,333 | Flags inferred/derived triples |
| 13 | :value | 123,197 | Literal value (mainly on Distance) |
| 14 | :has_title | 111,261 | Person → title/occupation |
| 15 | :has_reference | 104,718 | Link to source material |

The content-bearing properties are the biographical ones: `biocrm:has_family_relation`,
`biocrm:inheres_in`, and `y-rel:relates_to` encode the genealogical network; `:has_event`,
`schema:date`, `schema:place`, and `:has_title` build the event-based life histories.
The `biocrm:` namespace points to **BioCRM**, a CIDOC-CRM extension SeCo uses for
prosopography (modelling people, roles, and relationships in history).

### The :Timespan class

**Incoming properties** (ways other entities point to a Timespan):

| Property | Count | Meaning |
|----------|-------|---------|
| schema:date | 221,535 | Links an entity/event to its date Timespan |
| skos:broader | 61,354 | Timespans nested within larger Timespans |
| :date_of_end | 41,914 | End date of something |
| :date_of_origin | 23,742 | Start/origin date |
| :link_by | 18,902 | Generic linking relation |
| void:exampleResource | 1 | VoID dataset-description example pointer |

**Outgoing properties** (attached to a Timespan instance):

| Property | Count | Holds |
|----------|-------|-------|
| gvp:estStart | 62,421 | Estimated start of the interval (Getty GVP) |
| gvp:estEnd | 62,352 | Estimated end of the interval |

A Timespan is a thin "interval" object: reached via `schema:date` / `:date_of_end` /
`:date_of_origin`, and internally carrying just `gvp:estStart` and `gvp:estEnd`.
This Getty `estStart`/`estEnd` pattern is SeCo's standard way of modelling fuzzy
historical dates, where exact days are unknown so a span is bracketed by estimated bounds.

### The biocrm:has_family_relation property

This property always connects a `y-rel:` **relation class** (subject) to a person class
(object), following the BioCRM reification pattern:

> **`y-rel:[relation]` → has_family_relation → `:Person` / `:ReferencedPerson`**

A relationship isn't a direct person-to-person edge but is itself an instance
(e.g. a "Wife" relation node) that then points to the related person.

Most-used connections:

| Relation class (subject) | Target | Count |
|--------------------------|--------|-------|
| y-rel:Son (f6) | ReferencedPerson | 40,852 |
| y-rel:Husband (f12) | ReferencedPerson | 34,886 |
| y-rel:Mother (f3) | Person | 25,509 |
| y-rel:Father (f4) | Person | 25,492 |
| y-rel:Wife (f11) | Person | 22,142 |
| y-rel:Brother (f22) | Person | 13,571 |
| y-rel:Mother-in-law (f55) | ReferencedPerson | 13,269 |
| y-rel:Wife (f11) | ReferencedPerson | 13,060 |
| y-rel:Daughter-in-law (f73) | ReferencedPerson | 12,868 |
| y-rel:Father-in-law (f56) | ReferencedPerson | 11,446 |

**Person vs ReferencedPerson:** `:Person` is a fully-modelled individual with their own
biography; `:ReferencedPerson` is someone merely mentioned in a source as a relative,
without a full record. The same relation often appears with both targets (e.g. Wife →
Person 22,142×, Wife → ReferencedPerson 13,060×) depending on whether the relative is
independently documented.

The long tail extends into very fine-grained, often Finnish-labelled kin types:
great-great-great-grandfather (f102), *pikkuserkun tytär* (second-cousin's daughter,
f115), foster and step relations, *appipuoli* (f124) — some with only a single instance.
This gives the dataset an unusually deep genealogical vocabulary.
