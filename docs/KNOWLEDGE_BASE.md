# 📚 Prune — TCM Knowledge Base & Clinical Ontology

The Prune knowledge base is an organized, curated collection of Traditional Chinese Medicine (TCM) theoretical and diagnostic concepts. Each entry is stored as a `KnowledgeChunk` containing an immutable identifier, categorized collection, title, body content, and search tags.

---

## 🗂️ Knowledge Collections

| Collection | Description | Representative Source IDs |
| :--- | :--- | :--- |
| `symptom_pattern` | Symptom-to-syndrome differentiation mappings | `sp.headache.liver_yang`, `sp.insomnia.1to3am`, `sp.bloating.liver_spleen` |
| `treatment` | Self-care protocols, dietary adjustments & lifestyle | `tx.liver_yang.headache`, `tx.spleen.diet`, `tx.kidney_yang.lowback` |
| `acupressure` | Key acupoints with anatomical locations & techniques | `ap.GB20`, `ap.LI4`, `ap.HT7`, `ap.PC6`, `ap.ST36`, `ap.LV3` |
| `herb_food` | Food energetics, dietary therapy & kitchen teas | `hf.ginger`, `hf.chrysanthemum`, `hf.goji`, `hf.congee`, `hf.walnut_sesame` |
| `seasonal` | Five Element seasonal living guides | `se.spring`, `se.summer`, `se.late_summer`, `se.autumn`, `se.winter` |
| `organ_theory` | Zang-Fu organ systems & energetic clock theory | `ot.liver`, `ot.spleen`, `ot.kidney`, `ot.organ_clock`, `ot.qi_vs_yang` |
| `qigong` | Therapeutic movement sets & breathwork | `qg.baduanjin`, `qg.six_sounds`, `qg.zhanzhuang`, `qg.yijinjing` |
| `intake_question`| 12 standard constitutional diagnostic questions | `iq.energy`, `iq.sleep`, `iq.digestion`, `iq.tongue`, `iq.temperature` |

---

## 📍 Acupressure Points Catalog

| Point Name | Chinese Pinyin | Location Summary | Primary Indications |
| :--- | :--- | :--- | :--- |
| **GB20** | *Fengchi* (Wind Pool) | Hollow at skull base between neck muscles | Headache, neck stiffness, dizziness, colds |
| **LI4** | *Hegu* (Joining Valley) | Dorsum of hand between 1st and 2nd metacarpal | Head & facial pain, stress *(Contraindicated in pregnancy)* |
| **LV3** | *Taichong* (Great Surge) | Dorsum of foot between 1st and 2nd metatarsals | Irritability, Liver Qi stagnation, headache |
| **ST36** | *Zusanli* (Leg Three Miles) | 4 fingers below kneecap, lateral to shin bone | Fatigue, digestive tonification, general vitality |
| **SP6** | *Sanyinjiao* (3 Yin Crossing)| 4 fingers above medial malleolus | Digestion, pelvic health, sleep *(Contraindicated in pregnancy)* |
| **PC6** | *Neiguan* (Inner Pass) | 3 fingers above wrist crease between tendons | Nausea, anxiety, chest tightness, palpitations |
| **HT7** | *Shenmen* (Spirit Gate) | Wrist crease on ulnar (little finger) side | Insomnia, anxiety, palpitations, Shen calming |
| **BL23** | *Shenshu* (Kidney Shu) | Lower back, 2 fingers lateral to L2 vertebra | Low back weakness, fatigue, cold sensation |

---

## 🍵 Dietary Energetics Summary

- **Warming Foods**: Fresh Ginger (*Sheng Jiang*), Cinnamon (*Rou Gui*), Lamb, Walnuts, Black Sesame, Cooked Congee.
- **Cooling Foods**: Chrysanthemum (*Ju Hua*), Peppermint (*Bo He*), Cucumber, Mung Beans, Watermelon, Celery.
- **Moistening Foods**: Pears, White Fungus (*Yin Er*), Lily Bulbs (*Bai He*), Almonds, Goji Berries (*Gou Qi Zi*).
