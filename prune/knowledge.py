"""Curated TCM knowledge base for Prune.

Every entry here is a `KnowledgeChunk` that represents a vector in the retrieval index.
In production, this can be synced to Pinecone or Weaviate; for self-contained
operation, it is embedded and cached locally with cosine similarity retrieval.

Each chunk carries:
- `id`        : Stable identifier (used for transparent citation: e.g. sp.headache.liver_yang)
- `collection`: Category (symptom_pattern, treatment, acupressure, herb_food, seasonal, organ_theory, qigong, intake_question)
- `title`     : Descriptive heading
- `text`      : Core clinical / theoretical knowledge content
- `tags`      : Keywords included in embedding vector
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KnowledgeChunk:
    id: str
    collection: str
    title: str
    text: str
    tags: List[str] = field(default_factory=list)

    def embedding_text(self) -> str:
        tag_str = " | ".join(self.tags)
        return f"[{self.collection}] {self.title}\n{self.text}\nTags: {tag_str}"


# ---------------------------------------------------------------------------
# Symptom -> Pattern mappings
# ---------------------------------------------------------------------------
_SYMPTOM_PATTERN: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="sp.headache.liver_yang",
        collection="symptom_pattern",
        title="Headache with pressure behind the eyes — Liver Yang rising",
        text=(
            "Frontal or temporal headache with pressure behind the eyes, often "
            "worse with stress, anger or red wine, frequently accompanied by "
            "irritability, red eyes, dry mouth, and a wiry pulse, points to "
            "Liver Yang rising. If the head feels heavy and 'wrapped in a wet "
            "towel' with nausea, suspect Dampness obstructing the head instead."
        ),
        tags=["headache", "behind eyes", "pressure", "Liver Yang", "Dampness"],
    ),
    KnowledgeChunk(
        id="sp.insomnia.1to3am",
        collection="symptom_pattern",
        title="Waking between 1–3 AM — Liver Qi stagnation",
        text=(
            "The TCM organ clock assigns 1–3 AM to the Liver. Repeatedly waking "
            "in this window, especially with vivid dreams, jaw tension or "
            "frustration, indicates Liver Qi stagnation, often with underlying "
            "Liver Blood deficiency. Waking 3–5 AM points instead to the Lung."
        ),
        tags=["insomnia", "wake at night", "organ clock", "Liver"],
    ),
    KnowledgeChunk(
        id="sp.loose_stools.am",
        collection="symptom_pattern",
        title="Loose stools every morning — Spleen Qi (and Kidney Yang) deficiency",
        text=(
            "Daybreak diarrhoea — loose, urgent stools shortly after waking, "
            "often with abdominal coldness, fatigue and pale tongue — is the "
            "classic 'cock-crow diarrhoea' pattern: Spleen Qi deficiency, "
            "frequently with Kidney Yang deficiency when chronic."
        ),
        tags=["digestion", "loose stools", "morning diarrhoea", "Spleen", "Kidney Yang"],
    ),
    KnowledgeChunk(
        id="sp.menstrual.dark_clots",
        collection="symptom_pattern",
        title="Severe period pain with dark clots — Blood stagnation",
        text=(
            "Cramping menstrual pain that is sharp, fixed, worse before/at the "
            "start of bleeding and accompanied by dark, clotted blood reflects "
            "Blood stagnation in the Lower Jiao. Warmth and movement relieve "
            "it; cold and stillness aggravate it."
        ),
        tags=["menstruation", "dysmenorrhoea", "clots", "Blood stagnation"],
    ),
    KnowledgeChunk(
        id="sp.cold.wind_cold",
        collection="symptom_pattern",
        title="Acute cold with chills and clear runny nose — Wind-Cold invasion",
        text=(
            "Sudden onset of chills greater than fever, stiff neck, clear nasal "
            "discharge, no thirst and a tight pulse is Wind-Cold attacking the "
            "Lung Wei (defensive) layer. The strategy is to release the "
            "exterior with warming, pungent therapy."
        ),
        tags=["cold", "chills", "runny nose", "Wind-Cold", "Wei Qi"],
    ),
    KnowledgeChunk(
        id="sp.fatigue.chronic",
        collection="symptom_pattern",
        title="Months of exhaustion despite sleep — Qi deficiency differentiation",
        text=(
            "Persistent fatigue with adequate sleep typically reflects Qi "
            "deficiency. Cold limbs, low back weakness, low libido and "
            "frequent pale urination point to Kidney; bloating, loose stools "
            "and poor appetite point to Spleen. The two often coexist."
        ),
        tags=["fatigue", "exhaustion", "Qi deficiency", "Kidney", "Spleen"],
    ),
    KnowledgeChunk(
        id="sp.bloating.liver_spleen",
        collection="symptom_pattern",
        title="Recurring post-meal bloating — Liver invading Spleen",
        text=(
            "Bloating and stomach discomfort triggered or worsened by stress, "
            "with alternating loose stools and constipation, is Liver Qi "
            "stagnation invading the Spleen (Middle Jiao disharmony). Eating "
            "while rushed or upset is a key aggravator."
        ),
        tags=["bloating", "digestion", "stress", "Liver", "Spleen", "Middle Jiao"],
    ),
    KnowledgeChunk(
        id="sp.lowback.kidney_yang",
        collection="symptom_pattern",
        title="Chronic low back pain, worse with cold — Kidney Yang deficiency + Bi syndrome",
        text=(
            "Long-standing dull lower back pain that worsens in cold or damp "
            "weather and improves with warmth indicates Kidney Yang deficiency "
            "with a Cold-Damp Bi (obstruction) component. The lumbar region is "
            "the 'mansion of the Kidneys' in TCM."
        ),
        tags=["low back pain", "lumbar", "Kidney Yang", "Bi syndrome", "cold"],
    ),
    KnowledgeChunk(
        id="sp.palpitations.shen",
        collection="symptom_pattern",
        title="Anxiety with palpitations, normal cardiology — Shen disturbance",
        text=(
            "Palpitations with anxiety, poor sleep and vivid dreams in the "
            "absence of cardiac pathology is a Shen (spirit) disturbance. "
            "Pale complexion and dizziness suggest Heart Blood deficiency; "
            "night sweats and tinnitus suggest Heart-Kidney disconnection "
            "(failure of Water and Fire to communicate)."
        ),
        tags=["anxiety", "palpitations", "Shen", "Heart Blood", "Heart Kidney"],
    ),
    KnowledgeChunk(
        id="sp.recurrent_colds.lung_wei",
        collection="symptom_pattern",
        title="Catches every cold — Lung & Wei Qi deficiency",
        text=(
            "Frequent seasonal respiratory infections, spontaneous sweating, "
            "weak voice and shortness of breath on exertion reflect Lung Qi "
            "and Wei (defensive) Qi deficiency. The Lungs control the skin "
            "and the exterior in TCM."
        ),
        tags=["recurrent infection", "Lung Qi", "Wei Qi", "immune"],
    ),
    KnowledgeChunk(
        id="sp.emotion.liver_qi",
        collection="symptom_pattern",
        title="Feeling stuck, frustrated, irritable — Liver Qi stagnation (emotional)",
        text=(
            "A sense of being stuck, easily frustrated, sighing, chest or "
            "rib-side tightness and PMS irritability is the emotional face of "
            "Liver Qi stagnation. The Liver governs the smooth flow of Qi and "
            "of emotions."
        ),
        tags=["frustration", "stuck", "Liver Qi stagnation", "emotion"],
    ),
    KnowledgeChunk(
        id="sp.emotion.autumn_grief",
        collection="symptom_pattern",
        title="Sad and unmotivated since autumn — Lung & grief connection",
        text=(
            "Autumn corresponds to the Metal element and the Lung organ, whose "
            "associated emotion is grief. Sadness and low motivation that "
            "appear or worsen in autumn reflect a seasonal Lung pattern, often "
            "Lung Qi deficiency."
        ),
        tags=["sadness", "grief", "autumn", "Lung", "Metal"],
    ),
    KnowledgeChunk(
        id="sp.emotion.overthinking",
        collection="symptom_pattern",
        title="Overthinking, mind never stops — Spleen-Heart axis (pensiveness)",
        text=(
            "Excessive worry and rumination injure the Spleen (the emotion "
            "'pensiveness' belongs to Earth), which then fails to nourish the "
            "Heart and Shen. Symptoms include poor digestion, fatigue, and a "
            "racing mind at night."
        ),
        tags=["overthinking", "worry", "pensiveness", "Spleen", "Heart"],
    ),
]

# ---------------------------------------------------------------------------
# Pattern -> Treatment protocols
# ---------------------------------------------------------------------------
_TREATMENT: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="tx.liver_yang.headache",
        collection="treatment",
        title="Self-care for Liver Yang rising headache",
        text=(
            "Strategy: subdue Liver Yang, soothe Liver Qi. Reduce alcohol, "
            "coffee, fried foods and late-night screen exposure. Favour "
            "chrysanthemum tea, celery, mint and leafy greens. Gentle "
            "downward-directing breathing (slow exhale longer than inhale). "
            "Acupressure on GB20 and LI4 (see acupressure entries)."
        ),
        tags=["Liver Yang", "headache", "treatment"],
    ),
    KnowledgeChunk(
        id="tx.liver_qi.evening",
        collection="treatment",
        title="Evening routine for Liver Qi stagnation insomnia",
        text=(
            "Finish eating by 19:00. Take a 20-minute walk after dinner to "
            "move Liver Qi. Keep screens dim after sunset. A warm foot soak "
            "with a pinch of salt before bed grounds Yang. Consider a small "
            "cup of chamomile or rose-bud tea. Journaling 'what is on my "
            "chest' can release stuck emotions."
        ),
        tags=["Liver Qi", "insomnia", "evening routine"],
    ),
    KnowledgeChunk(
        id="tx.spleen.diet",
        collection="treatment",
        title="Spleen-tonifying food therapy",
        text=(
            "Strategy: warm, cooked, simple meals. Favour congee, well-cooked "
            "oats, pumpkin, sweet potato, carrots, ginger and small amounts "
            "of meat broth. Avoid raw salads, iced drinks, dairy and excess "
            "sugar, all of which generate Damp and weaken the Spleen."
        ),
        tags=["Spleen Qi", "diet", "Damp", "food therapy"],
    ),
    KnowledgeChunk(
        id="tx.blood_stagnation.menses",
        collection="treatment",
        title="Warming protocol for menstrual Blood stagnation",
        text=(
            "Apply warmth to the lower abdomen (hot water bottle or moxa over "
            "Ren-4 / Ren-6) from a few days before menses until flow eases. "
            "Drink ginger and brown-sugar decoction. Avoid cold drinks and "
            "raw foods around the period. Gentle hip-circling movement helps "
            "move stagnant Blood."
        ),
        tags=["menstruation", "Blood stagnation", "warming", "moxa"],
    ),
    KnowledgeChunk(
        id="tx.wind_cold.protocol",
        collection="treatment",
        title="Wind-Cold release protocol",
        text=(
            "Drink hot ginger-and-spring-onion (cong bai) decoction, dress "
            "warmly and induce gentle sweating under blankets. Rest. A hot "
            "foot soak with ginger and a pinch of salt supports release of "
            "the exterior. Avoid raw, cold or greasy foods until symptoms "
            "clear."
        ),
        tags=["Wind-Cold", "ginger", "sweating therapy"],
    ),
    KnowledgeChunk(
        id="tx.kidney_yang.lowback",
        collection="treatment",
        title="Kidney Yang & Bi syndrome low-back self-care",
        text=(
            "Keep the lumbar region warm at all times — a haramaki / lumbar "
            "wrap, especially in cold weather. Daily gentle moxibustion over "
            "BL23 (Shenshu) and Du4 (Mingmen) where appropriate. Walnuts, "
            "black sesame, lamb and bone broth tonify Kidney Yang. Avoid "
            "prolonged cold sitting and overexertion."
        ),
        tags=["Kidney Yang", "low back pain", "moxibustion", "Bi syndrome"],
    ),
    KnowledgeChunk(
        id="tx.shen.calming",
        collection="treatment",
        title="Calming the Shen — anxiety and palpitations",
        text=(
            "Daily 10-minute seated breathing focused on the lower dantian "
            "anchors the Shen. Avoid stimulants after midday. A warm cup of "
            "longan-and-jujube decoction in the evening nourishes Heart "
            "Blood. Acupressure on HT7 (Shenmen) and PC6 (Neiguan) before "
            "sleep settles the spirit."
        ),
        tags=["Shen", "anxiety", "palpitations", "Heart"],
    ),
    KnowledgeChunk(
        id="tx.lung_wei.tonify",
        collection="treatment",
        title="Seasonal tonification for Lung & Wei Qi deficiency",
        text=(
            "Strategy: tonify Lung and consolidate the exterior. Daily "
            "diaphragmatic breathing or the Six Healing Sounds 'sss' for the "
            "Lung. Foods: white radish, pear, almonds, lily bulb, congee. "
            "Begin protective practices in late summer to prepare for autumn."
        ),
        tags=["Lung Qi", "Wei Qi", "immune", "tonification"],
    ),
    KnowledgeChunk(
        id="tx.liver_qi.movement",
        collection="treatment",
        title="Movement therapy for Liver Qi stagnation",
        text=(
            "Brisk walking, swimming, dance and Qigong forms that stretch the "
            "lateral ribcage (sides of the body, where the Liver and "
            "Gallbladder channels run) move stuck Qi. Sour foods in small "
            "quantity (lemon, vinegar) gently regulate the Liver."
        ),
        tags=["Liver Qi stagnation", "movement", "Qigong"],
    ),
    KnowledgeChunk(
        id="tx.lung.autumn",
        collection="treatment",
        title="Autumn adjustment protocol for Lung-related sadness",
        text=(
            "Earlier bedtimes, more time in natural light, and breathing "
            "practices that emphasise a slow, complete exhale. White, "
            "moistening foods (pear, white fungus, almond) support the "
            "Lung. Allow grief to be felt rather than suppressed; the Metal "
            "element values clear letting-go."
        ),
        tags=["autumn", "Lung", "grief", "seasonal"],
    ),
    KnowledgeChunk(
        id="tx.earth.grounding",
        collection="treatment",
        title="Grounding practices for overthinking",
        text=(
            "Eat warm cooked breakfasts at a consistent time. Walk barefoot "
            "on natural ground when possible. A 5-minute 'feet on the floor, "
            "hands on the belly' breathing pause before each meal supports "
            "the Earth element and helps the Spleen anchor thought."
        ),
        tags=["overthinking", "Spleen", "Earth", "grounding"],
    ),
]

# ---------------------------------------------------------------------------
# Acupressure point database (location, technique, contraindications)
# ---------------------------------------------------------------------------
_ACUPRESSURE: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="ap.GB20",
        collection="acupressure",
        title="GB20 — Fengchi (Wind Pool)",
        text=(
            "Location: in the hollow between the two large neck muscles at "
            "the base of the skull. Technique: press inward and slightly "
            "upward with the thumbs for 1–2 minutes while breathing slowly. "
            "Indications: headache, neck tension, dizziness, common cold. "
            "Caution: avoid heavy pressure if you have severe cervical spine "
            "issues."
        ),
        tags=["GB20", "Fengchi", "headache", "neck"],
    ),
    KnowledgeChunk(
        id="ap.LI4",
        collection="acupressure",
        title="LI4 — Hegu (Joining Valley)",
        text=(
            "Location: on the back of the hand, at the highest point of the "
            "muscle when thumb and index finger are pressed together. "
            "Technique: firm thumb pressure for 1 minute each side. "
            "Indications: headache, facial pain, common cold, constipation. "
            "Contraindication: do NOT use during pregnancy — strong moving "
            "point."
        ),
        tags=["LI4", "Hegu", "headache", "pregnancy contraindication"],
    ),
    KnowledgeChunk(
        id="ap.HT7",
        collection="acupressure",
        title="HT7 — Shenmen (Spirit Gate)",
        text=(
            "Location: on the wrist crease on the little-finger side, in the "
            "depression just inside the wrist tendon. Technique: gentle "
            "circular pressure for 1–2 minutes. Indications: anxiety, "
            "palpitations, insomnia, calming the Shen."
        ),
        tags=["HT7", "Shenmen", "anxiety", "insomnia", "Shen"],
    ),
    KnowledgeChunk(
        id="ap.PC6",
        collection="acupressure",
        title="PC6 — Neiguan (Inner Pass)",
        text=(
            "Location: three finger-widths up from the wrist crease on the "
            "inner forearm, between the two tendons. Technique: thumb "
            "pressure 1 minute each side. Indications: nausea, palpitations, "
            "anxiety, chest tightness."
        ),
        tags=["PC6", "Neiguan", "palpitations", "nausea"],
    ),
    KnowledgeChunk(
        id="ap.LU7",
        collection="acupressure",
        title="LU7 — Lieque (Broken Sequence)",
        text=(
            "Location: above the wrist on the thumb-side of the radial bone, "
            "about 1.5 finger-widths above the wrist crease. Technique: firm "
            "circular pressure for 1 minute. Indications: common cold, "
            "cough, neck stiffness — opens the Lung and releases the "
            "exterior."
        ),
        tags=["LU7", "Lieque", "cold", "Lung"],
    ),
    KnowledgeChunk(
        id="ap.BL23",
        collection="acupressure",
        title="BL23 — Shenshu (Kidney Shu)",
        text=(
            "Location: on the lower back, two finger-widths lateral to the "
            "spine at the level of the second lumbar vertebra (waist). "
            "Technique: warm hands and rub up-and-down briskly until warm, "
            "morning and evening. Indications: low back pain, fatigue, cold "
            "limbs, Kidney tonification."
        ),
        tags=["BL23", "Shenshu", "low back", "Kidney Yang"],
    ),
    KnowledgeChunk(
        id="ap.SP6",
        collection="acupressure",
        title="SP6 — Sanyinjiao (Three Yin Crossing)",
        text=(
            "Location: four finger-widths above the inner ankle bone, just "
            "behind the tibia. Technique: thumb pressure 1–2 minutes each "
            "side. Indications: digestive issues, menstrual irregularity, "
            "insomnia. Contraindication: do NOT use during pregnancy."
        ),
        tags=["SP6", "Sanyinjiao", "digestion", "menstruation", "pregnancy contraindication"],
    ),
    KnowledgeChunk(
        id="ap.ST36",
        collection="acupressure",
        title="ST36 — Zusanli (Leg Three Miles)",
        text=(
            "Location: four finger-widths below the kneecap, one finger-width "
            "lateral to the shin bone. Technique: firm thumb pressure or tap "
            "for 2 minutes daily. Indications: fatigue, digestive weakness, "
            "general tonification — the great Qi-building point."
        ),
        tags=["ST36", "Zusanli", "fatigue", "Spleen", "Stomach"],
    ),
    KnowledgeChunk(
        id="ap.LV3",
        collection="acupressure",
        title="LV3 — Taichong (Great Surge)",
        text=(
            "Location: top of the foot in the depression between the first "
            "and second metatarsal bones. Technique: firm thumb pressure 1 "
            "minute each side. Indications: irritability, headache, PMS, "
            "Liver Qi stagnation — the key Liver-soothing point."
        ),
        tags=["LV3", "Taichong", "Liver Qi stagnation", "irritability"],
    ),
]

# ---------------------------------------------------------------------------
# Herbal & food therapy
# ---------------------------------------------------------------------------
_HERB_FOOD: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="hf.ginger",
        collection="herb_food",
        title="Ginger (sheng jiang) — warming, exterior-releasing",
        text=(
            "Pungent and warm. Disperses Cold, releases the exterior, warms "
            "the Middle Jiao and stops nausea. Useful in early Wind-Cold "
            "colds, cold-type digestion, and menstrual cramps with cold. "
            "Caution in Heat patterns or pronounced Yin deficiency."
        ),
        tags=["ginger", "Wind-Cold", "warming", "nausea"],
    ),
    KnowledgeChunk(
        id="hf.chrysanthemum",
        collection="herb_food",
        title="Chrysanthemum tea (ju hua) — cooling for Liver Yang",
        text=(
            "Cool, sweet and slightly bitter. Clears Liver heat, brightens "
            "the eyes and calms Liver Yang rising. Helpful for tension "
            "headaches behind the eyes, red eyes and stress-related "
            "irritability."
        ),
        tags=["chrysanthemum", "Liver Yang", "headache", "cooling"],
    ),
    KnowledgeChunk(
        id="hf.goji",
        collection="herb_food",
        title="Goji berries (gou qi zi) — Liver/Kidney Yin tonic",
        text=(
            "Sweet, neutral. Nourishes Liver and Kidney Yin and Blood, "
            "moistens the Lung. Good for tired eyes, low-grade fatigue, "
            "ageing and dryness. Steep 1 tablespoon in hot water or add to "
            "porridge."
        ),
        tags=["goji", "Liver Yin", "Kidney Yin", "tonic"],
    ),
    KnowledgeChunk(
        id="hf.congee",
        collection="herb_food",
        title="Congee — universal Spleen tonic",
        text=(
            "Slow-cooked rice porridge nourishes Spleen and Stomach, "
            "supports recovery from illness, and is suitable for almost any "
            "deficiency pattern. Adapt with ginger for cold patterns, lily "
            "bulb for dryness, or jujube for fatigue."
        ),
        tags=["congee", "Spleen", "tonic", "convalescence"],
    ),
    KnowledgeChunk(
        id="hf.longan_jujube",
        collection="herb_food",
        title="Longan & jujube decoction — Heart Blood",
        text=(
            "Simmer 10 jujubes (red dates) and a small handful of dried "
            "longan in 1 L water for 30 minutes. Sweet and warm; nourishes "
            "Heart Blood and calms the Shen. Useful for anxiety and "
            "palpitations from Blood deficiency."
        ),
        tags=["longan", "jujube", "Heart Blood", "Shen"],
    ),
    KnowledgeChunk(
        id="hf.walnut_sesame",
        collection="herb_food",
        title="Walnuts & black sesame — Kidney tonics",
        text=(
            "Walnuts (he tao ren) tonify Kidney Yang, lubricate the "
            "intestines and benefit the Lung. Black sesame (hei zhi ma) "
            "nourishes Kidney and Liver Yin and the Blood, darkens hair. A "
            "daily small handful of either supports long-term Kidney "
            "essence."
        ),
        tags=["walnut", "black sesame", "Kidney", "longevity"],
    ),
    KnowledgeChunk(
        id="hf.pear_white",
        collection="herb_food",
        title="Pear and white foods — Lung moistening",
        text=(
            "Pear, white fungus (yin er), lily bulb (bai he) and almond "
            "moisten the Lung and clear dryness. Especially appropriate in "
            "autumn or when there is dry cough, dry skin and dry throat."
        ),
        tags=["pear", "white fungus", "Lung", "autumn", "dryness"],
    ),
]

# ---------------------------------------------------------------------------
# Seasonal & constitutional wellness protocols
# ---------------------------------------------------------------------------
_SEASONAL: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="se.spring",
        collection="seasonal",
        title="Spring protocol — Liver & Gallbladder season",
        text=(
            "Spring belongs to the Wood element and the Liver-Gallbladder "
            "pair. Rise earlier with the sun, walk outdoors, stretch the "
            "sides of the body, and add young green vegetables and small "
            "amounts of sour foods (lemon, vinegar, sauerkraut). Avoid "
            "excessive anger and overwork; aim for smooth, flexible energy."
        ),
        tags=["spring", "Liver", "Gallbladder", "Wood"],
    ),
    KnowledgeChunk(
        id="se.summer",
        collection="seasonal",
        title="Summer protocol — Heart season",
        text=(
            "Summer is Fire / Heart. Go to bed a little later, rise early, "
            "stay joyful and socially engaged. Eat lighter, cooling foods "
            "(watermelon, mung bean, cucumber). Protect the Heart from "
            "overheating and emotional excess."
        ),
        tags=["summer", "Heart", "Fire"],
    ),
    KnowledgeChunk(
        id="se.late_summer",
        collection="seasonal",
        title="Late summer — Spleen / Earth",
        text=(
            "The damp transition between summer and autumn taxes the Spleen. "
            "Favour warm cooked foods, yellow/orange root vegetables, and "
            "minimise raw and cold foods. A short midday rest supports the "
            "Earth element."
        ),
        tags=["late summer", "Spleen", "Earth"],
    ),
    KnowledgeChunk(
        id="se.autumn",
        collection="seasonal",
        title="Autumn protocol — Lung season",
        text=(
            "Autumn is Metal / Lung. Begin Lung tonification (breathing "
            "practices, white moistening foods). Earlier bedtimes, gentler "
            "exercise. Allow grief to be processed. Protect the neck and "
            "upper back from wind."
        ),
        tags=["autumn", "Lung", "Metal", "grief"],
    ),
    KnowledgeChunk(
        id="se.winter",
        collection="seasonal",
        title="Winter protocol — Kidney season",
        text=(
            "Winter is Water / Kidney. Sleep earlier, rise later, conserve "
            "energy. Warming, slow-cooked foods (bone broth, black beans, "
            "walnuts). Protect the lower back and feet from cold. Quiet "
            "introspective practices store Jing for the coming year."
        ),
        tags=["winter", "Kidney", "Water", "Jing"],
    ),
    KnowledgeChunk(
        id="se.longevity_jing",
        collection="seasonal",
        title="Long-term vitality — Jing & Kidney essence",
        text=(
            "Jing (essence) is the deepest reserve, stored in the Kidneys. "
            "Practices that protect Jing: regular sleep before 23:00, "
            "moderation in sex and stimulants, slow Qigong, walking in "
            "nature, and tonifying foods (walnut, black sesame, goji, "
            "Cordyceps, He Shou Wu under practitioner guidance)."
        ),
        tags=["Jing", "Kidney essence", "longevity", "vitality"],
    ),
    KnowledgeChunk(
        id="se.age_40s_women",
        collection="seasonal",
        title="Diet in the 40s — women, Kidney Yin decline",
        text=(
            "The 40s mark a natural decline of Kidney Yin in women, often "
            "felt as heat, dryness, sleep changes and irregular menses. "
            "Favour Yin-nourishing foods (black sesame, goji, mulberry, "
            "tofu, pear, white fungus). Reduce hot, spicy, drying foods. "
            "Protect sleep and rest."
        ),
        tags=["women", "40s", "Kidney Yin", "perimenopause"],
    ),
    KnowledgeChunk(
        id="se.age_40s_men",
        collection="seasonal",
        title="Diet in the 40s — men, Kidney Yang support",
        text=(
            "In men the 40s often bring early signs of Kidney Yang decline: "
            "lower libido, cold limbs, low-back weakness. Favour warming "
            "tonifying foods (walnut, lamb in winter, bone broth, black "
            "beans), reduce raw and iced foods, keep the lower back warm "
            "and exercise without exhausting."
        ),
        tags=["men", "40s", "Kidney Yang"],
    ),
]

# ---------------------------------------------------------------------------
# Organ theory (education mode)
# ---------------------------------------------------------------------------
_ORGAN_THEORY: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="ot.liver",
        collection="organ_theory",
        title="The Liver in TCM",
        text=(
            "In TCM the Liver governs the smooth flow of Qi (and therefore "
            "of emotions), stores the Blood, controls the tendons, opens to "
            "the eyes and is paired with the Gallbladder. It is also linked "
            "with the menstrual cycle. This is a *functional* Liver in "
            "Chinese medicine and is NOT the same as the biomedical liver "
            "organ — though the two overlap in some functions."
        ),
        tags=["Liver", "organ theory", "education"],
    ),
    KnowledgeChunk(
        id="ot.spleen",
        collection="organ_theory",
        title="The Spleen in TCM",
        text=(
            "The Spleen transforms food and fluids into Qi and Blood, "
            "ascends pure Qi, holds Blood inside the vessels, governs the "
            "muscles, and opens to the mouth. Its emotion is pensiveness. "
            "This is a functional concept that differs from the biomedical "
            "spleen."
        ),
        tags=["Spleen", "organ theory", "education"],
    ),
    KnowledgeChunk(
        id="ot.kidney",
        collection="organ_theory",
        title="The Kidney in TCM",
        text=(
            "The Kidneys store Jing (essence), govern birth, growth, "
            "reproduction and ageing, control Water, anchor the Qi for the "
            "Lung, and open to the ears and the lower orifices. The lumbar "
            "region is the 'mansion of the Kidneys'. Emotion: fear."
        ),
        tags=["Kidney", "organ theory", "Jing"],
    ),
    KnowledgeChunk(
        id="ot.heart",
        collection="organ_theory",
        title="The Heart in TCM",
        text=(
            "The Heart governs Blood and houses the Shen (spirit / "
            "consciousness). It opens to the tongue and shows on the "
            "complexion. Its emotion is joy (in excess: mania). A calm, "
            "well-housed Shen produces clear thought and restful sleep."
        ),
        tags=["Heart", "Shen", "organ theory"],
    ),
    KnowledgeChunk(
        id="ot.lung",
        collection="organ_theory",
        title="The Lung in TCM",
        text=(
            "The Lung governs Qi and respiration, controls the skin and "
            "Wei (defensive) Qi, opens to the nose, and is linked to the "
            "emotion of grief. Weak Lungs are reflected in shortness of "
            "breath, recurrent colds and weak voice."
        ),
        tags=["Lung", "Wei Qi", "grief"],
    ),
    KnowledgeChunk(
        id="ot.qi_vs_yang",
        collection="organ_theory",
        title="Qi deficiency vs Yang deficiency",
        text=(
            "Qi deficiency: tiredness, shortness of breath, weak voice, "
            "spontaneous sweat, pale tongue. Yang deficiency includes ALL "
            "of those plus marked COLD signs — cold limbs, aversion to "
            "cold, copious clear urine, loose stools, low libido. Yang "
            "deficiency is, in effect, Qi deficiency that has progressed to "
            "involve a lack of warmth."
        ),
        tags=["Qi deficiency", "Yang deficiency", "education"],
    ),
    KnowledgeChunk(
        id="ot.organ_clock",
        collection="organ_theory",
        title="The TCM organ clock",
        text=(
            "Each two-hour window of the day corresponds to peak activity "
            "in one organ system. Key windows for sleep disturbance: "
            "23:00–01:00 Gallbladder, 01:00–03:00 Liver, 03:00–05:00 Lung, "
            "05:00–07:00 Large Intestine. Repeated waking in the same "
            "window points to that organ."
        ),
        tags=["organ clock", "insomnia", "education"],
    ),
]

# ---------------------------------------------------------------------------
# Qigong style database (personalisation)
# ---------------------------------------------------------------------------
_QIGONG: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="qg.baduanjin",
        collection="qigong",
        title="Ba Duan Jin (Eight Pieces of Brocade) — general balance",
        text=(
            "An eight-movement set suitable for almost every constitution. "
            "Especially good for Qi deficiency, mild Liver Qi stagnation "
            "and general daily tonification. 15–20 minutes, beginner "
            "friendly."
        ),
        tags=["Ba Duan Jin", "Qigong", "beginner", "balance"],
    ),
    KnowledgeChunk(
        id="qg.yijinjing",
        collection="qigong",
        title="Yi Jin Jing (Muscle-Tendon Change) — for stagnation",
        text=(
            "Stronger, more stretching set that moves Liver Qi and "
            "tonifies tendons. Good for Liver Qi stagnation constitutions "
            "with frustration and tightness."
        ),
        tags=["Yi Jin Jing", "Liver Qi stagnation"],
    ),
    KnowledgeChunk(
        id="qg.six_sounds",
        collection="qigong",
        title="Liu Zi Jue (Six Healing Sounds) — organ-specific",
        text=(
            "Six vocalised exhalations, each tied to an organ system "
            "(Liver 'xu', Heart 'he', Spleen 'hu', Lung 'sss', Kidney "
            "'chui', Triple Burner 'xi'). Excellent for emotional "
            "patterns and pre-sleep practice."
        ),
        tags=["Six Healing Sounds", "Liu Zi Jue", "emotion"],
    ),
    KnowledgeChunk(
        id="qg.zhanzhuang",
        collection="qigong",
        title="Zhan Zhuang (Standing Pole) — for Qi/Yang building",
        text=(
            "Quiet standing meditation that builds Qi and Yang over time. "
            "Best for Kidney Yang deficiency and grounding for "
            "overthinking. Start with 5 minutes daily."
        ),
        tags=["Zhan Zhuang", "Kidney Yang", "standing"],
    ),
]

# ---------------------------------------------------------------------------
# Structured premium intake questions (12 standard constitutional dimensions)
# ---------------------------------------------------------------------------
_INTAKE_QUESTIONS: List[KnowledgeChunk] = [
    KnowledgeChunk(
        id="iq.energy",
        collection="intake_question",
        title="Energy levels",
        text="How is your overall energy from morning to evening? When do you feel most tired?",
        tags=["intake", "energy"],
    ),
    KnowledgeChunk(
        id="iq.sleep",
        collection="intake_question",
        title="Sleep quality",
        text="How easily do you fall asleep? Do you wake during the night, and if so, around what time?",
        tags=["intake", "sleep"],
    ),
    KnowledgeChunk(
        id="iq.digestion",
        collection="intake_question",
        title="Digestion",
        text="How is your appetite, bloating after meals, and stool quality (formed, loose, dry)?",
        tags=["intake", "digestion"],
    ),
    KnowledgeChunk(
        id="iq.temperature",
        collection="intake_question",
        title="Temperature preference",
        text="Do you tend to feel cold or hot? Are your hands and feet usually warm or cool?",
        tags=["intake", "temperature"],
    ),
    KnowledgeChunk(
        id="iq.thirst",
        collection="intake_question",
        title="Thirst & drinking",
        text="Are you usually thirsty, and do you prefer warm or cold drinks?",
        tags=["intake", "thirst"],
    ),
    KnowledgeChunk(
        id="iq.emotion",
        collection="intake_question",
        title="Predominant emotion",
        text="Which emotion shows up most often: irritability, worry, sadness, fear, or joy?",
        tags=["intake", "emotion"],
    ),
    KnowledgeChunk(
        id="iq.tongue",
        collection="intake_question",
        title="Tongue self-report",
        text=(
            "Look at your tongue in the mirror. Is the body pale, normal, or red? "
            "Is the coating thin/white, thick/white, or yellow? Any teeth marks on the sides?"
        ),
        tags=["intake", "tongue"],
    ),
    KnowledgeChunk(
        id="iq.menstruation",
        collection="intake_question",
        title="Menstruation (if applicable)",
        text="If you menstruate: cycle length, flow, colour, clots, and pain pattern?",
        tags=["intake", "menstruation"],
    ),
    KnowledgeChunk(
        id="iq.sweat",
        collection="intake_question",
        title="Sweating",
        text="Do you sweat easily without exertion, or have night sweats?",
        tags=["intake", "sweat"],
    ),
    KnowledgeChunk(
        id="iq.lowback",
        collection="intake_question",
        title="Lower back & knees",
        text="Any weakness, ache or coldness in the lower back or knees?",
        tags=["intake", "low back"],
    ),
    KnowledgeChunk(
        id="iq.stress",
        collection="intake_question",
        title="Stress and tension",
        text="Where in the body do you carry stress (jaw, shoulders, ribs, gut)?",
        tags=["intake", "stress"],
    ),
    KnowledgeChunk(
        id="iq.diet_lifestyle",
        collection="intake_question",
        title="Diet & lifestyle",
        text="Briefly describe your typical diet, exercise frequency, and screen time before bed.",
        tags=["intake", "lifestyle"],
    ),
]


def all_chunks() -> List[KnowledgeChunk]:
    """Return all knowledge chunks across all categories."""
    return (
        _SYMPTOM_PATTERN
        + _TREATMENT
        + _ACUPRESSURE
        + _HERB_FOOD
        + _SEASONAL
        + _ORGAN_THEORY
        + _QIGONG
        + _INTAKE_QUESTIONS
    )


def intake_questions() -> List[KnowledgeChunk]:
    """Return only the intake questionnaire items."""
    return list(_INTAKE_QUESTIONS)


def get_chunk_by_id(chunk_id: str) -> Optional[KnowledgeChunk]:
    """Look up a single knowledge chunk by its unique ID."""
    for chunk in all_chunks():
        if chunk.id == chunk_id:
            return chunk
    return None
