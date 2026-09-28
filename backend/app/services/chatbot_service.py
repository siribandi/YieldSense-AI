import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.prediction_service import PredictionService
from backend.app.services.analytics_service import AnalyticsService
from backend.app.db.models import User, Farm, Crop, Prediction


class ChatbotService:
    """
    AgriSense AI Conversational Intelligence Engine for YieldSense AI.
    Provides comprehensive, realistic, and domain-grounded agronomic assistance
    across crops, soils, fertilizers, irrigation, weather, crop diseases,
    sowing/harvesting, agricultural practices, ML yield forecasts, and personalized farm data.
    """

    def __init__(self):
        self.prediction_service = PredictionService()
        self.analytics_service = AnalyticsService()
        self._init_knowledge_base()

    def _init_knowledge_base(self):
        """Initializes structured agronomic knowledge."""
        # 1. Comprehensive Crop Profiles (12 Supported Crops)
        self.crops = {
            "soybean": {
                "name": "Soybean (Glycine max)",
                "season": "Kharif (June - October)",
                "soil": "Well-drained Loamy and Black soils",
                "ph": "6.0 - 7.0 (Slightly acidic to neutral)",
                "rainfall": "100 - 180 mm",
                "temp": "25 C - 32 C",
                "seed_rate": "25 - 30 kg/acre with 45 cm row spacing",
                "npk": "N: 20-30 kg/ha, P: 60-80 kg/ha, K: 40-60 kg/ha",
                "fertilizer": "DAP or NPK basal + Rhizobium japonicum seed inoculation",
                "irrigation": "Critical at Flowering (R1-R2) and Pod-filling (R3-R4) stages. Sensitive to waterlogging.",
                "diseases": "Yellow Mosaic Virus (spread by whiteflies), Charcoal Rot, Rust. Use resistant varieties (JS 335, JS 95-60) and spray Imidacloprid for vectors.",
                "harvest": "Harvest when 95% of pods turn golden brown and moisture is 13-14%."
            },
            "wheat": {
                "name": "Wheat (Triticum aestivum)",
                "season": "Rabi (November - April)",
                "soil": "Well-drained Loamy, Clay Loam, and Alluvial soils",
                "ph": "6.0 - 7.5 (Neutral)",
                "rainfall": "150 - 250 mm (Requires 4 to 6 scheduled irrigations)",
                "temp": "15 C - 25 C for growth, 28 C - 30 C at grain fill",
                "seed_rate": "40 - 50 kg/acre (100-125 kg/ha) with 20-22.5 cm row spacing",
                "npk": "N: 100-120 kg/ha, P: 50-60 kg/ha, K: 40-50 kg/ha",
                "fertilizer": "Urea in 3 split doses (50% basal, 25% at CRI, 25% at tillering) + DAP (basal)",
                "irrigation": "Critical at Crown Root Initiation (21 days after sowing), Tillering, Booting, Flowering, and Milking.",
                "diseases": "Yellow/Brown Rust, Loose Smut, Karnal Bunt, Terminal Heat Stress. Treat seeds with Carbendazim (2g/kg) and spray Propiconazole 25 EC (0.1%) for rust.",
                "harvest": "Harvest when straw turns yellow and grains are hard with < 12% moisture."
            },
            "rice": {
                "name": "Rice / Paddy (Oryza sativa)",
                "season": "Kharif and Rabi (where irrigated)",
                "soil": "Heavy Clay, Clay Loam, and Alluvial soils with high water retention",
                "ph": "5.5 - 7.0",
                "rainfall": "200 - 300+ mm (Standing water of 2-5 cm during tillering/panicle)",
                "temp": "24 C - 35 C",
                "seed_rate": "15 - 20 kg/acre for transplanting; 25-30 kg/acre for direct seeding",
                "npk": "N: 100-150 kg/ha, P: 50-60 kg/ha, K: 50-60 kg/ha + Zinc (25 kg/ha)",
                "fertilizer": "Urea (split into 3 doses) + DAP + Zinc Sulphate (basal)",
                "irrigation": "Maintain saturated soil to shallow standing water until 10 days before harvest.",
                "diseases": "Blast (Pyricularia oryzae), Bacterial Leaf Blight, Brown Spot, Stem Borer, Brown Planthopper. Treat with Tricyclazole 75 WP for blast and Cartap Hydrochloride for borers.",
                "harvest": "Harvest when 80-85% of panicles turn golden yellow."
            },
            "cotton": {
                "name": "Cotton (Gossypium hirsutum / arboreum)",
                "season": "Kharif (May - October)",
                "soil": "Deep Black Regur soil and fertile Sandy Loam",
                "ph": "6.5 - 8.0",
                "rainfall": "120 - 250 mm",
                "temp": "28 C - 37 C (Sensitive to frost and excessive moisture)",
                "seed_rate": "1.5 - 2.0 kg/acre for Bt hybrids with 90x60 cm spacing",
                "npk": "N: 90-120 kg/ha, P: 45-60 kg/ha, K: 45-60 kg/ha",
                "fertilizer": "NPK complexes + Foliar sprays of 2% DAP or Potassium Nitrate at flowering/boll setting",
                "irrigation": "Critical at Square formation, Flowering, and Boll development. Avoid waterlogging.",
                "diseases": "Pink Bollworm, Cotton Leaf Curl Virus, Bacterial Blight, Fusarium Wilt. Install pheromone traps and use IPM techniques.",
                "harvest": "Pick mature, fully opened bolls in dry morning hours."
            },
            "maize": {
                "name": "Maize / Corn (Zea mays)",
                "season": "Kharif, Rabi, and Spring",
                "soil": "Well-drained deep Loamy soil rich in organic matter",
                "ph": "5.8 - 7.2",
                "rainfall": "120 - 220 mm",
                "temp": "20 C - 32 C",
                "seed_rate": "8 - 10 kg/acre with 60x20 cm spacing",
                "npk": "N: 100-120 kg/ha, P: 60 kg/ha, K: 40 kg/ha",
                "fertilizer": "DAP (basal) + Urea top-dress at knee-high (V6) and tasseling (VT) stages",
                "irrigation": "Critical at Knee-high, Tasseling, Silking, and Grain-filling stages.",
                "diseases": "Fall Armyworm (FAW), Turcicum Leaf Blight, Stalk Rot. Spray Emamectin Benzoate 5 SG for FAW.",
                "harvest": "Harvest when husk leaves turn brown and black layer forms at grain base."
            },
            "groundnut": {
                "name": "Groundnut / Peanut (Arachis hypogaea)",
                "season": "Kharif and Summer",
                "soil": "Light Sandy Loam and Red Sandy soil with good aeration",
                "ph": "6.0 - 6.8",
                "rainfall": "100 - 180 mm",
                "temp": "25 C - 32 C",
                "seed_rate": "40 - 50 kg/acre kernel with 30x10 cm spacing",
                "npk": "N: 20-30 kg/ha, P: 40-50 kg/ha, K: 40-60 kg/ha + Gypsum (200-400 kg/ha)",
                "fertilizer": "DAP + Gypsum at flowering/pegging (supplies Calcium for pod filling and kernel weight)",
                "irrigation": "Critical at Flowering, Peg penetration, and Pod development.",
                "diseases": "Tikka disease (Cercospora leaf spot), Rust, Collar Rot. Spray Mancozeb 75 WP or Chlorothalonil.",
                "harvest": "Harvest when inner pod shell turns dark brownish-black."
            },
            "sugarcane": {
                "name": "Sugarcane (Saccharum officinarum)",
                "season": "Perennial / Annual (Spring or Autumn planting)",
                "soil": "Deep Loamy, Clay Loam, and Alluvial soils",
                "ph": "6.5 - 7.5",
                "rainfall": "200 - 300 mm (Requires regular irrigation cycles)",
                "temp": "26 C - 35 C",
                "seed_rate": "35,000 - 40,000 three-budded setts/ha",
                "npk": "N: 150-250 kg/ha, P: 60-80 kg/ha, K: 60-80 kg/ha",
                "fertilizer": "NPK basal + Urea split into 3-4 top dressings + Trash mulching",
                "irrigation": "Irrigate every 10-14 days during summer formative phase.",
                "diseases": "Red Rot (Colletotrichum falcatum), Smut, Top Borer, Pyrilla. Use healthy disease-free setts.",
                "harvest": "Harvest at peak sucrose maturity (10-12 months) when Brix reading reaches 18-20%."
            },
            "barley": {
                "name": "Barley (Hordeum vulgare)",
                "season": "Rabi",
                "soil": "Sandy Loam to Loamy soil (Drought and salinity tolerant)",
                "ph": "6.5 - 8.0",
                "rainfall": "100 - 180 mm",
                "temp": "15 C - 28 C",
                "seed_rate": "35 - 40 kg/acre with 22.5 cm spacing",
                "npk": "N: 60-80 kg/ha, P: 30-40 kg/ha, K: 30-40 kg/ha",
                "fertilizer": "DAP + Urea (Apply 2/3 N at sowing, 1/3 at first irrigation)",
                "irrigation": "Requires 2 to 3 irrigations at Tillering and Flag leaf emergence.",
                "diseases": "Covered Smut, Stripe Disease, Aphids. Seed treatment with Thiram (2.5 g/kg).",
                "harvest": "Harvest when spikes turn golden yellow and grains are hard."
            },
            "pulses": {
                "name": "Pulses (Chickpea, Pigeonpea, Green gram, Black gram)",
                "season": "Kharif and Rabi",
                "soil": "Well-drained Loamy and Black soils",
                "ph": "6.2 - 7.5",
                "rainfall": "80 - 160 mm",
                "temp": "20 C - 30 C",
                "seed_rate": "Chickpea: 30-35 kg/acre; Moong/Urad: 8-10 kg/acre",
                "npk": "N: 20-25 kg/ha, P: 40-50 kg/ha, K: 20-30 kg/ha",
                "fertilizer": "DAP or Single Super Phosphate (SSP) + Rhizobium + PSB culture",
                "irrigation": "1-2 light irrigations at Branching and Pod-fill. Avoid excess watering.",
                "diseases": "Wilt (Fusarium), Pod Borer (Helicoverpa armigera), Ascochyta Blight. Install pheromone traps and spray NPV or Chlorantraniliprole.",
                "harvest": "Harvest when plants dry up and pods rattle upon shaking."
            },
            "tea": {
                "name": "Tea (Camellia sinensis)",
                "season": "Perennial Plantation",
                "soil": "Deep, well-drained Acidic Red Loam rich in organic matter",
                "ph": "4.5 - 5.5 (Acidic)",
                "rainfall": "200 - 300+ mm well-distributed",
                "temp": "18 C - 30 C with shade canopy",
                "seed_rate": "Clonal cuttings / nursery seedlings at 105x75 cm spacing",
                "npk": "N: 100-140 kg/ha, P: 30-40 kg/ha, K: 80-100 kg/ha",
                "fertilizer": "Ammonium Sulphate + NPK blends + Organic compost",
                "irrigation": "Sprinkler irrigation during dry winter/spring months.",
                "diseases": "Blister Blight, Red Spider Mites, Tea Mosquito Bug. Spray Wettable Sulphur or Hexaconazole.",
                "harvest": "Pluck two tender leaves and a terminal bud on 7-10 day rounds."
            },
            "coffee": {
                "name": "Coffee (Coffea arabica / canephora)",
                "season": "Perennial Shade Plantation",
                "soil": "Deep, porous, fertile Red Loam",
                "ph": "5.5 - 6.5",
                "rainfall": "150 - 250 mm with blossom showers (25-40mm in March-April)",
                "temp": "18 C - 28 C (Frost-sensitive)",
                "seed_rate": "Nursery seedlings at 2x2 m (Arabica) or 3x3 m (Robusta)",
                "npk": "N: 100-120 kg/ha, P: 60-80 kg/ha, K: 100-120 kg/ha",
                "fertilizer": "NPK + Farmyard Manure split into pre-monsoon and post-monsoon doses",
                "irrigation": "Overhead sprinkler irrigation for blossom and backing showers.",
                "diseases": "Coffee Leaf Rust (Hemileia vastatrix), White Stem Borer, Berry Borer. Spray 0.5% Bordeaux mixture.",
                "harvest": "Hand-pick fully ripe red berries (cherries) in selective rounds."
            },
            "jute": {
                "name": "Jute (Corchorus olitorius / capsularis)",
                "season": "Kharif (Pre-monsoon sowing in March-April)",
                "soil": "Alluvial, Loamy, and Clay soils",
                "ph": "6.0 - 7.2",
                "rainfall": "160 - 280 mm with high relative humidity (> 75%)",
                "temp": "24 C - 36 C",
                "seed_rate": "2.5 - 3.0 kg/acre with 25x5 cm spacing",
                "npk": "N: 40-60 kg/ha, P: 20-30 kg/ha, K: 20-30 kg/ha",
                "fertilizer": "Urea + NPK (Apply half N at basal, half at 3-4 weeks)",
                "irrigation": "Requires 1-2 irrigations before monsoon sets in.",
                "diseases": "Stem Rot (Macrophomina), Semi-looper, Yellow Mite. Treat seeds with Carbendazim.",
                "harvest": "Harvest at 50% flowering stage (120-135 days) for superior fiber tenacity."
            }
        }

    def generate_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        user: Optional[User] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Main conversational engine:
        1. Checks for personalized user farm/crop/prediction inquiries against real DB records.
        2. Detects off-topic queries and provides a polite agricultural redirection.
        3. Evaluates natural-language agricultural intents (diseases, soil, fertilizer, weather, irrigation, agronomy, ML).
        4. Ingests real-time page context (e.g. from prediction page or analytics).
        """
        raw_q = query.strip()
        q = raw_q.lower()
        now = datetime.now(timezone.utc)

        # -------------------------------------------------------------
        # 1. Check for Personalized User Account Lookups ("show my farms", "what is my predicted yield", "list my crops")
        # -------------------------------------------------------------
        lookup_patterns = [
            r"\b(show|list|view|what are|tell me|get)\b.*\b(my|our)\b.*\b(farm|farms|holding|holdings|plot|plots|crops|predictions|forecasts)\b",
            r"\b(what is my|what did i|show my|tell me my)\b.*\b(prediction|predictions|yield|forecast|result|results|history)\b",
            r"\b(my registered|my logged|my saved)\b.*\b(farms|crops|predictions)\b",
            r"\b(which farms|which crops)\b.*\b(do i have|i have|are registered)\b",
            r"\b(how is my farm|how are my crops doing|status of my farm)\b"
        ]
        is_personal_lookup = any(re.search(pat, q) for pat in lookup_patterns)

        # Do not treat general agronomic advice questions (e.g. "for my crop", "on my soil") as account lookups
        if is_personal_lookup and not any(w in q for w in ["how to", "when should", "what fertilizer", "how much", "how do i", "can i apply"]):
            return self._handle_personalized_query(q, user=user, db=db, now=now)
        elif is_personal_lookup and any(w in q for w in ["what are my", "show me my", "list my", "what did i predict", "what is my predicted yield"]):
            return self._handle_personalized_query(q, user=user, db=db, now=now)

        # -------------------------------------------------------------
        # 2. Check for Non-Agricultural / Out-of-Scope Questions
        # -------------------------------------------------------------
        if self._is_out_of_scope(q):
            reply = (
                "### [AgriSense AI Assistant]\n\n"
                "I am **AgriSense AI**, an agricultural intelligence assistant dedicated specifically to farming, crop management, soil health, and yield prediction on the YieldSense AI platform.\n\n"
                "While I cannot assist with topics outside agriculture, I would be delighted to help you with:\n"
                "- **Crop Management**: Cultivation guides, sowing windows, seed rates, spacing, and harvesting for 12 major crops.\n"
                "- **Soil Health & pH**: Soil acidity/alkalinity correction, testing, and N-P-K nutrient schedules.\n"
                "- **Pest & Disease Control**: Symptoms, organic remedies, and IPM treatments for blights, rusts, rot, and insects.\n"
                "- **Irrigation & Weather**: Scheduling, drought mitigation, waterlogging drainage, and heat stress protection.\n"
                "- **Yield Forecasting**: How our ML model predicts crop yields and how to maximize your harvest.\n\n"
                "What agricultural topic would you like to explore?"
            )
            suggestions = [
                "What is the ideal soil pH for Wheat?",
                "How to manage Pink Bollworm in Cotton?",
                "When should I apply DAP vs Urea for Soybean?",
                "How does the ML crop yield prediction work?"
            ]
            return {"reply": reply, "category": "out_of_scope", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 3. ML Model & System Specs Intent
        # -------------------------------------------------------------
        if any(w in q for w in ["model", "algorithm", "accuracy", "r2", "r^2", "rmse", "mae", "machine learning", "dataset size", "training records", "how does prediction work", "linear regression"]):
            meta = self.prediction_service.get_metadata()
            perf = meta.get("performance_metrics", {})
            reply = (
                "### [YieldSense AI Machine Learning Architecture]\n\n"
                "Our platform uses a trained and verified **Linear Regression** model (v2.0.0) built upon a standardized dataset of **1,500 agricultural field records** across 14 Indian states.\n\n"
                "**Verified Performance Metrics on Held-Out Test Data:**\n"
                "- **Model Algorithm**: Linear Regression (Selected for lowest test RMSE & MAE)\n"
                "- **Test MAE (Mean Absolute Error)**: `4,273.23 kg/acre`\n"
                "- **Test RMSE (Root Mean Squared Error)**: `11,381.99 kg/acre`\n"
                "- **Test R2 Score**: `0.0029` (Baseline linear relationship)\n"
                "- **Total Features**: 11 raw parameters (State, Crop, Soil Type, Fertilizer, N, P, K, Rainfall, Temperature, Soil pH, Year) transformed into **43 encoded dimensions** via One-Hot Categorical Encoding and Standard Scaling.\n\n"
                "**Compared Models Evaluated During Training:**\n"
                "1. Linear Regression (Selected Deployment Model)\n"
                "2. Random Forest Regressor (Train R2: 0.8392, Test RMSE: 11,867.55)\n"
                "3. Gradient Boosting Regressor (Train R2: 0.9676, Test RMSE: 12,348.92)\n"
                "4. Decision Tree Regressor (Train R2: 0.7318, Test RMSE: 13,268.03)\n"
            )
            suggestions = [
                "What features affect yield the most?",
                "How do I run a yield forecast?",
                "What crops are in the dataset?",
                "How can I improve my predicted yield?"
            ]
            return {"reply": reply, "category": "model_info", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 4. Crop Diseases, Pests & Integrated Pest Management (IPM)
        # -------------------------------------------------------------
        if any(w in q for w in ["disease", "pest", "blight", "rust", "rot", "wilt", "mildew", "bollworm", "aphid", "caterpillar", "borer", "fungus", "fungicide", "pesticide", "neem", "ipm", "insects", "yellow mosaic", "blast"]):
            matched_crop = self._match_crop(q)
            if matched_crop:
                guide = self.crops[matched_crop]
                reply = (
                    f"### [Crop Protection & Pest Management for {guide['name']}]\n\n"
                    f"**Key Diseases & Pest Threats**:\n"
                    f"{guide['diseases']}\n\n"
                    f"**Integrated Pest Management (IPM) Guidelines**:\n"
                    f"1. **Seed Sanitation**: Treat seeds with biocontrol agents (*Trichoderma viride* @ 4-5 g/kg) or fungicide (Thiram/Carbendazim @ 2 g/kg) before sowing.\n"
                    f"2. **Cultural Controls**: Maintain clean field borders, practice crop rotation with non-host crops, and avoid waterlogging to curb soil-borne pathogens.\n"
                    f"3. **Biological & Botanical Controls**: Install yellow sticky traps (10-15/acre) for sucking pests (aphids, whiteflies) and spray 5% Neem Seed Kernel Extract (NSKE) or Neem oil (1500 ppm @ 3 ml/L).\n"
                    f"4. **Judicious Chemical Intervention**: Apply recommended selective fungicides/insecticides only when pest populations cross Economic Threshold Levels (ETL).\n"
                )
            else:
                reply = (
                    "### [Comprehensive Agricultural Disease & Pest Management Guide]\n\n"
                    "Effective crop protection requires early diagnosis and Integrated Pest Management (IPM):\n\n"
                    "**1. Fungal & Bacterial Diseases**:\n"
                    "- **Rusts & Blights** (Wheat, Soybean, Groundnut): Leaf pustules and dark necrotic lesions. *Remedy*: Spray Propiconazole 25 EC (1 ml/L) or Mancozeb 75 WP (2 g/L).\n"
                    "- **Wilts & Root Rots** (Cotton, Pulses, Sugarcane): Vascular browning and sudden drooping. *Remedy*: Soil drenching with *Trichoderma harzianum* and ensuring field drainage.\n"
                    "- **Blast & Blights** (Rice, Maize): Spindle-shaped lesions. *Remedy*: Spray Tricyclazole 75 WP (0.6 g/L).\n\n"
                    "**2. Common Insect Pests**:\n"
                    "- **Sucking Pests** (Aphids, Jassids, Whiteflies, Thrips): Cause leaf curling and transmit viruses. *Remedy*: Yellow sticky traps + Neem oil spray (3 ml/L) or Imidacloprid 17.8 SL (0.3 ml/L).\n"
                    "- **Borers & Caterpillars** (Bollworm, Stem Borer, Fall Armyworm): Bore into stems and pods. *Remedy*: Pheromone traps (5/acre) + *Bacillus thuringiensis* (Bt) or Emamectin Benzoate 5 SG (0.4 g/L).\n\n"
                    "**3. General IPM Golden Rules**:\n"
                    "• Always rotate chemical modes of action to prevent pesticide resistance.\n"
                    "• Spray during calm morning or late evening hours to protect beneficial pollinators.\n"
                )
            suggestions = [
                "How to control Rust in Wheat?",
                "What is the remedy for Pink Bollworm in Cotton?",
                "How to prevent Yellow Mosaic Virus in Soybean?",
                "What organic pesticides work best?"
            ]
            return {"reply": reply, "category": "crop_protection", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 5. Sowing, Planting, Spacing & Harvesting Window Intent
        # -------------------------------------------------------------
        if any(w in q for w in ["sow", "sowing", "seed rate", "spacing", "planting", "harvest", "harvesting", "maturity", "seed treatment"]):
            matched_crop = self._match_crop(q)
            if matched_crop:
                guide = self.crops[matched_crop]
                reply = (
                    f"### [Sowing & Harvesting Protocol for {guide['name']}]\n\n"
                    f"- **Optimum Sowing Window**: {guide['season']}\n"
                    f"- **Recommended Seed Rate & Spacing**: {guide['seed_rate']}\n"
                    f"- **Ideal Sowing Soil & pH**: {guide['soil']} (pH `{guide['ph']}`)\n"
                    f"- **Sowing Temperature Range**: `{guide['temp']}`\n\n"
                    f"**Harvesting & Maturity Indicators**:\n"
                    f"{guide['harvest']}\n\n"
                    f"**Seed Treatment Best Practices**:\n"
                    f"Treat seeds sequentially with **Fungicide -> Insecticide -> Bio-fertilizer (Rhizobium/PSB)** (FIR rule) 24 hours prior to sowing to maximize germination and seedling vigor.\n"
                )
            else:
                reply = (
                    "### [Agronomic Sowing & Harvesting Guidelines]\n\n"
                    "Timely sowing and proper harvest timing are pivotal for yield maximization:\n\n"
                    "**1. Crop Seasons & Optimum Sowing Windows**:\n"
                    "- **Kharif Season (Monsoon)**: June - July (Soybean, Cotton, Rice, Maize, Groundnut, Jute).\n"
                    "- **Rabi Season (Winter)**: October - November (Wheat, Barley, Chickpea, Mustard).\n"
                    "- **Zaid / Summer Season**: February - March (Summer Pulses, Maize, Groundnut).\n\n"
                    "**2. Seed Preparation & FIR Rule**:\n"
                    "Always treat seed in this strict order (FIR):\n"
                    "1. **F - Fungicide**: Carbendazim or Thiram (2 g/kg seed) to kill seed-borne fungal spores.\n"
                    "2. **I - Insecticide**: Imidacloprid (3 ml/kg seed) for early sucking pest defense.\n"
                    "3. **R - Rhizobium / Biofertilizer**: Specific microbial inoculants (20 g/kg seed) for nitrogen fixation.\n\n"
                    "**3. Maturity & Safe Storage**:\n"
                    "Harvest crops at physiological maturity when grain/pod moisture is 14-18%, then sun-dry to **10-12% moisture** before bag storage to prevent storage fungal rot and weevil attacks.\n"
                )
            suggestions = [
                "What is the seed rate for Wheat per acre?",
                "When is the best time to harvest Soybean?",
                "How to treat Groundnut seeds before sowing?",
                "What is the spacing for Bt Cotton?"
            ]
            return {"reply": reply, "category": "sowing_harvesting", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 6. Fertilizer, N-P-K & Plant Nutrition Intent
        # -------------------------------------------------------------
        if any(w in q for w in ["fertilizer", "fertilizers", "npk", "nitrogen", "phosphorus", "potassium", "urea", "dap", "ssp", "mop", "compost", "zinc", "micronutrient", "manure", "vermicompost"]):
            matched_crop = self._match_crop(q)
            if matched_crop:
                guide = self.crops[matched_crop]
                reply = (
                    f"### [Fertilizer & Soil Nutrition Schedule for {guide['name']}]\n\n"
                    f"- **Recommended N-P-K Schedule**: `{guide['npk']}`\n"
                    f"- **Primary Fertilizer Program**: `{guide['fertilizer']}`\n"
                    f"- **Optimal Soil Type & pH**: {guide['soil']} (Target pH: `{guide['ph']}`)\n\n"
                    f"**Application Timing & Method**:\n"
                    f"1. **Basal Application**: Apply 100% of Phosphorus (DAP/SSP), 100% of Potassium (MOP), and 30-50% of Nitrogen at sowing.\n"
                    f"2. **Top Dressing**: Apply remaining Nitrogen (Urea) in 2 split doses at key vegetative and flowering growth milestones.\n"
                    f"3. **Micronutrient & Soil Support**: If Zinc deficiency occurs, apply Zinc Sulphate 21% @ 10 kg/acre. Maintain soil pH in the `{guide['ph']}` range for peak nutrient uptake.\n"
                )
            else:
                reply = (
                    "### [Balanced Fertilization & Plant Nutrition Protocol]\n\n"
                    "Achieving high crop yield requires matching crop nutrient demand with balanced soil supply:\n\n"
                    "**1. Primary Macronutrients (N-P-K)**:\n"
                    "- **Nitrogen (N)**: Drives vegetative leaf canopy, shoot elongation, and protein synthesis. *Deficiency*: Generalized yellowing of older leaves. *Excess*: Excessive vegetative growth, delayed flowering, and lodging.\n"
                    "- **Phosphorus (P)**: Powers root development, early energy transfer (ATP), and flower initiation. *Deficiency*: Purple/reddish tint on older leaves.\n"
                    "- **Potassium (K)**: Regulates stomatal conductance, water stress tolerance, and disease defense. *Deficiency*: Leaf margin burning / scorch.\n\n"
                    "**2. Common Fertilizers in YieldSense AI**:\n"
                    "- **DAP (18-46-0)**: Premier basal source for early root anchoring.\n"
                    "- **Urea (46% N)**: Fast-acting Nitrogen. Always split into 2-3 top-dressings to prevent leaching losses.\n"
                    "- **SSP (16% P2O5, 11% Sulphur, 19% Calcium)**: Superior source for oilseeds (Groundnut, Soybean) and pulses.\n"
                    "- **MOP (60% K2O)**: Premier Potassium source.\n"
                    "- **NPK Complexes (e.g. 10:26:26 / 12:32:16)**: Balanced multi-nutrient formulations.\n\n"
                    "**3. Split Application Rule of Thumb**:\n"
                    "Never apply 100% of Nitrogen at sowing. Split: **50% at sowing (Basal) + 25% at Knee-high/Tillering + 25% at Pre-flowering**.\n"
                )
            suggestions = [
                "When should I apply DAP vs Urea?",
                "What is the best fertilizer for Cotton?",
                "How to identify Potassium deficiency in crops?",
                "What are the benefits of Single Super Phosphate (SSP)?"
            ]
            return {"reply": reply, "category": "fertilizers", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 7. Soil Health, Soil pH & Soil Amendments Intent
        # -------------------------------------------------------------
        if any(w in q for w in ["soil", "ph", "acidity", "alkalinity", "salinity", "sodic", "lime", "gypsum", "loamy", "black soil", "red soil", "clay soil", "sandy", "soil test", "organic matter", "organic carbon"]):
            matched_crop = self._match_crop(q)
            if matched_crop:
                guide = self.crops[matched_crop]
                reply = (
                    f"### [Soil Health & pH Management for {guide['name']}]\n\n"
                    f"- **Optimal Soil Type**: {guide['soil']}\n"
                    f"- **Ideal Soil pH Range**: `{guide['ph']}`\n"
                    f"- **Primary Fertilizer**: `{guide['fertilizer']}`\n\n"
                    f"**Soil Amendment Guidelines**:\n"
                    f"• If soil pH is **< 6.0 (Acidic)**: Apply Agricultural Lime (CaCO3 @ 500-800 kg/acre) to prevent Phosphorus fixation for {guide['name']}.\n"
                    f"• If soil pH is **> 7.8 (Alkaline)**: Apply Agricultural Gypsum (CaSO4 @ 400-600 kg/acre) and organic compost to restore micronutrient absorption.\n"
                )
            else:
                reply = (
                    "### [Soil Health Management & Soil Amendment Protocol]\n\n"
                    "Soil health is the biological and chemical foundation of high crop yields:\n\n"
                    "**1. Soil pH Scale & Nutrient Availability**:\n"
                    "- **Strongly Acidic (< 5.5)**: High Aluminum/Manganese toxicity; locks up Phosphorus and Molybdenum. *Correction*: Apply Agricultural Lime (Calcium Carbonate, CaCO3) at 800-1,200 kg/acre 3 weeks prior to sowing.\n"
                    "- **Optimal Neutral (6.0 - 7.2) [BEST FOR MOST CROPS]**: Maximum bioavailability of primary (N, P, K) and secondary (Ca, Mg, S) macronutrients.\n"
                    "- **Alkaline / Sodic (> 7.8)**: High Calcium carbonate and Sodium locks up Zinc, Iron, and Boron. *Correction*: Apply Agricultural Gypsum (Calcium Sulfate, CaSO4) at 500-800 kg/acre + Green manuring (*Sesbania / Dhaincha*).\n\n"
                    "**2. Soil Textures in YieldSense AI**:\n"
                    "- **Loamy Soil**: Premier balance of water holding and aeration; ideal for Wheat, Maize, Soybean.\n"
                    "- **Black Regur Soil**: High clay cation exchange; ideal for Cotton, Soybean, Sugarcane.\n"
                    "- **Red Soil**: Porous and well-drained; ideal for Groundnut, Pulses, Millets.\n"
                    "- **Clay Soil**: High water retention; ideal for Rice and Sugarcane.\n"
                    "- **Sandy Soil**: High percolation; requires split fertilizer doses and organic mulching.\n\n"
                    "**3. Enhancing Soil Organic Carbon (SOC)**:\n"
                    "Incorporate 4-5 tons/acre of well-decomposed Farmyard Manure (FYM) or 2 tons/acre of Vermicompost annually to boost soil microbial activity and moisture retention.\n"
                )
            suggestions = [
                "How to treat acidic soil with lime?",
                "What fertilizer works best for Black soil?",
                "How to improve sandy soil water retention?",
                "What is the best soil pH for Soybean?"
            ]
            return {"reply": reply, "category": "soil_health", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 8. Irrigation, Water Management & Drought Mitigation Intent
        # -------------------------------------------------------------
        if any(w in q for w in ["irrigation", "water", "drip", "sprinkler", "flood", "drought", "drainage", "waterlogging", "moisture", "watering"]):
            reply = (
                "### [Smart Irrigation & Agricultural Water Management]\n\n"
                "Water availability at critical physiological stages dictates over 50% of final harvest yield:\n\n"
                "**1. High-Efficiency Irrigation Systems**:\n"
                "- **Drip Irrigation**: Delivers water and fertigation directly to the rhizosphere with **90-95% efficiency**, saving 40-60% water compared to flood irrigation. Best for Cotton, Sugarcane, Vegetables, and Orchards.\n"
                "- **Sprinkler Irrigation**: Ideal for undulating terrain and closely spaced crops (Wheat, Groundnut, Soybean, Pulses).\n"
                "- **Alternate Furrow Irrigation**: Saves 30% water while maintaining root zone aeration.\n\n"
                "**2. Critical Irrigation Growth Stages (Must Never Face Moisture Stress)**:\n"
                "- **Wheat**: Crown Root Initiation (21 DAS), Flowering, and Milking stages.\n"
                "- **Maize**: Tasseling and Silking stages.\n"
                "- **Soybean & Pulses**: Flowering and Pod elongation stages.\n"
                "- **Rice**: Panicle initiation and Heading.\n\n"
                "**3. Mitigating Drought & Water Deficits**:\n"
                "• **Organic Mulching**: Spread crop straw or dry leaves (3-4 tons/acre) to reduce evaporation by 30-40%.\n"
                "• **Anti-transpirants**: Foliar spray of Potassium Nitrate (1%) or Kaolin clay (5%) to reflect excess solar radiation.\n"
            )
            suggestions = [
                "What are the critical irrigation stages for Wheat?",
                "How does drip irrigation improve crop yield?",
                "How to protect crops during drought?",
                "How to prevent waterlogging damage in fields?"
            ]
            return {"reply": reply, "category": "irrigation", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 9. Weather, Climate & Abiotic Stress Management Intent
        # -------------------------------------------------------------
        if any(w in q for w in ["weather", "temperature", "heat", "heat stress", "frost", "cold", "rainfall", "monsoon", "climate", "hail"]):
            reply = (
                "### [Weather Impacts & Abiotic Climate Stress Mitigation]\n\n"
                "Climatic variables strongly influence photosynthetic efficiency and crop phenology:\n\n"
                "**1. Heat Stress (> 35 C)**:\n"
                "- Accelerates evapotranspiration, causes pollen sterility in cotton/maize, and leads to terminal heat stress in Rabi wheat.\n"
                "- *Remedies*: Early sowing of Wheat (mid-November), light irrigation during peak heat hours, and foliar spray of Salicylic acid (100 ppm) or Potassium.\n\n"
                "**2. Cold & Frost Hazard (< 4 C)**:\n"
                "- Causes cellular freezing and leaf tip scorching in winter crops.\n"
                "- *Remedies*: Light night irrigation (water releases latent heat), creating smoke screens (smudge fires) around field borders on calm cold nights.\n\n"
                "**3. Heavy Rainfall & Waterlogging (> 250 mm)**:\n"
                "- Causes root asphyxiation, nutrient leaching, and collar fungal rots.\n"
                "- *Remedies*: Construct 30 cm deep drainage trenches every 10-15 meters across fields and apply 20 kg/acre extra Nitrogen once soil dries.\n"
            )
            suggestions = [
                "How to protect Wheat from terminal heat stress?",
                "What crops are best for low rainfall areas?",
                "How does heavy rainfall affect soil nutrients?",
                "What is the ideal temperature for Maize?"
            ]
            return {"reply": reply, "category": "weather_climate", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 10. Agricultural Practices (Rotation, Intercropping, Zero Tillage, Mulching)
        # -------------------------------------------------------------
        if any(w in q for w in ["practice", "practices", "rotation", "intercrop", "intercropping", "tillage", "zero tillage", "organic farming", "mulch", "mulching", "cover crop", "farm management", "improve yield"]):
            reply = (
                "### [Agronomic Best Practices for Yield Optimization]\n\n"
                "Implementing modern sustainable agricultural practices significantly boosts net farm income:\n\n"
                "**1. Crop Rotation (The Cereal-Legume Principle)**:\n"
                "- Alternating heavy nutrient-depleting cereals (Wheat, Rice, Maize) with nitrogen-fixing legumes (Soybean, Chickpea, Moong) replenishes 30-50 kg/ha of biological atmospheric nitrogen, breaks pest cycles, and improves soil structure.\n\n"
                "**2. Strategic Intercropping Systems**:\n"
                "- **Maize + Soybean (1:2 row ratio)**: Maximizes light interception and delivers dual income.\n"
                "- **Cotton + Green Gram / Black Gram (1:1)**: Provides early cash flow before cotton canopy closes and suppresses weeds.\n\n"
                "**3. Conservation Tillage & Zero-Till**:\n"
                "- Direct drilling of Wheat using Happy Seeder into rice residue saves $30-40/acre in land preparation costs, preserves soil moisture, and curtails air pollution from stubble burning.\n\n"
                "**4. Organic Mulching**:\n"
                "- Retains 30-40% soil moisture, suppresses weed germination, and converts into organic carbon upon decomposition.\n"
            )
            suggestions = [
                "What are the best crop rotation combinations?",
                "How does intercropping reduce farming risks?",
                "What are the advantages of Zero Tillage?",
                "How to maximize yield for Soybean and Wheat?"
            ]
            return {"reply": reply, "category": "agronomic_practices", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 11. Specific Crop Inquiries (Matched by crop name)
        # -------------------------------------------------------------
        matched_crop = self._match_crop(q)
        if matched_crop:
            guide = self.crops[matched_crop]
            reply = (
                f"### [Agronomic Cultivation Profile: {guide['name']}]\n\n"
                f"- **Sowing Season**: {guide['season']}\n"
                f"- **Optimal Soil Type**: {guide['soil']}\n"
                f"- **Target Soil pH**: `{guide['ph']}`\n"
                f"- **Seasonal Moisture**: `{guide['rainfall']}`\n"
                f"- **Temperature Envelope**: `{guide['temp']}`\n"
                f"- **Recommended Seed Rate**: `{guide['seed_rate']}`\n"
                f"- **Fertilizer Program (N-P-K)**: `{guide['npk']}` ({guide['fertilizer']})\n"
                f"- **Irrigation Needs**: {guide['irrigation']}\n"
                f"- **Pest & Disease Management**: {guide['diseases']}\n"
                f"- **Harvesting**: {guide['harvest']}\n"
            )
            suggestions = [
                f"What fertilizer is best for {matched_crop.capitalize()}?",
                f"What are the main pests affecting {matched_crop.capitalize()}?",
                f"What is the ideal soil pH for {matched_crop.capitalize()}?",
                "How do I run an ML yield prediction?"
            ]
            return {"reply": reply, "category": "crop_profile", "suggestions": suggestions, "timestamp": now}

        # -------------------------------------------------------------
        # 12. General Farming Assistant Fallback
        # -------------------------------------------------------------
        reply = (
            "### [Welcome to AgriSense AI Assistant]\n\n"
            "I am your dedicated Agricultural Intelligence Assistant on YieldSense AI. I can assist you with:\n\n"
            "- **Crop Management**: Agronomic guidelines for 12 major crops (Soybean, Wheat, Rice, Cotton, Maize, Groundnut, Sugarcane, Pulses, etc.).\n"
            "- **Soil Health & Amendments**: Target soil pH, correcting acidity with lime, alkaline soil gypsum treatment, and N-P-K schedules.\n"
            "- **Pest & Disease Control**: Organic and chemical treatments for blights, rusts, wilts, bollworms, and sucking pests.\n"
            "- **Irrigation & Weather**: Critical growth stage watering, drip systems, drought resilience, and heat stress protection.\n"
            "- **Yield Forecasting**: Explaining our trained Machine Learning prediction pipeline (Linear Regression v2.0.0).\n"
            "- **Personalized Farm Data**: Reviewing your registered farms, crops, and historical predictions.\n\n"
            "How can I assist your farming operations today?"
        )
        suggestions = [
            "What is the best fertilizer for Soybean?",
            "How to treat acidic soil with lime?",
            "What are the critical irrigation stages for Wheat?",
            "How to control Pink Bollworm in Cotton?"
        ]
        return {"reply": reply, "category": "general_farming", "suggestions": suggestions, "timestamp": now}

    def _handle_personalized_query(
        self,
        q: str,
        user: Optional[User],
        db: Optional[Session],
        now: datetime
    ) -> Dict[str, Any]:
        """
        Answers personalized questions about the user's specific farms, crops, and predictions
        grounded strictly in real database records without hallucination.
        """
        if not user or not db:
            reply = (
                "### [Personalized Farm Intelligence]\n\n"
                "To access information about your registered farms, crops, or past yield predictions, please **log in** to your YieldSense AI account.\n\n"
                "Once logged in, I can automatically pull up:\n"
                "- Your registered farm parcels and soil types\n"
                "- Your active crop plantings\n"
                "- Your latest ML yield predictions and personalized advisories"
            )
            return {
                "reply": reply,
                "category": "personalized_data",
                "suggestions": ["Go to Sign In page", "What crops are supported?", "How does yield prediction work?"],
                "timestamp": now
            }

        # User is authenticated: query real database records
        user_farms = db.query(Farm).filter(Farm.user_id == user.id).all()
        user_preds = db.query(Prediction).filter(Prediction.user_id == user.id).order_by(Prediction.created_at.desc()).all()

        # A. Inquiries about Farms
        if any(w in q for w in ["farm", "farms", "holding", "plot", "land"]):
            if not user_farms:
                reply = (
                    f"### [Farm Records for {user.name}]\n\n"
                    f"You currently do not have any registered farms in your account.\n\n"
                    f"**How to add a farm**:\n"
                    f"1. Navigate to the **Farm Management** tab in the sidebar.\n"
                    f"2. Click **'Add New Farm'** and enter your farm name, location, area (acres), and soil type.\n"
                    f"3. Once logged, I will be able to provide customized soil and yield intelligence for your plot!"
                )
            else:
                farm_list = []
                for f in user_farms:
                    crops_list = ", ".join([c.crop_name for c in f.crops]) if f.crops else "None logged yet"
                    farm_list.append(f"- **{f.farm_name}**: `{f.area} acres` | Location: `{f.location}` | Soil: `{f.soil_type}` | Crops: `{crops_list}`")
                reply = (
                    f"### [Registered Farms for {user.name}]\n\n"
                    f"You have **{len(user_farms)} registered farm field(s)**:\n\n"
                    + "\n".join(farm_list) +
                    f"\n\n*Total Land Holding*: **{sum(f.area for f in user_farms):.1f} acres**."
                )
            suggestions = ["What crops can I grow on my soil?", "Run a yield prediction for my farm", "What are my latest predictions?"]
            return {"reply": reply, "category": "personalized_data", "suggestions": suggestions, "timestamp": now}

        # B. Inquiries about Predictions / Yield Forecasts
        if any(w in q for w in ["prediction", "predictions", "yield", "forecast", "result", "how much yield"]):
            if not user_preds:
                reply = (
                    f"### [Yield Prediction Records for {user.name}]\n\n"
                    f"You haven't run any crop yield predictions yet.\n\n"
                    f"**How to forecast your yield**:\n"
                    f"1. Go to the **Yield Prediction** page (`/predict`).\n"
                    f"2. Select your Crop, Location, Soil Type, Fertilizer, and input your soil pH, N-P-K, rainfall, and temperature.\n"
                    f"3. Click **'Predict Crop Yield'** to get instant forecasts in kg/acre and tons/acre."
                )
            else:
                latest = user_preds[0]
                reply = (
                    f"### [Latest Crop Yield Forecast for {user.name}]\n\n"
                    f"- **Crop**: `{latest.crop}` ({latest.state})\n"
                    f"- **Predicted Yield**: **{latest.predicted_yield_kg:,.1f} kg/acre** ({latest.predicted_yield_tons:.2f} tons/acre)\n"
                    f"- **Productivity Category**: `{latest.productivity_category or 'Standard'}`\n"
                    f"- **Field Conditions**: Soil: `{latest.soil_type}`, Fertilizer: `{latest.fertilizer}`, pH: `{latest.soil_ph:.2f}`, Rain: `{latest.rainfall_mm:.0f} mm`\n"
                    f"- **Forecast Date**: `{latest.created_at.strftime('%B %d, %Y')}`\n\n"
                    f"**Personalized Agronomic Advisory**:\n"
                    f"{latest.recommendation_summary or 'Maintain standard balanced N-P-K fertilization and monitor soil moisture.'}\n\n"
                    f"*You have run a total of **{len(user_preds)}** prediction(s). View full history in your Dashboard.*"
                )
            suggestions = ["How can I improve my predicted yield?", "What fertilizer is best for this crop?", "Run a new yield prediction"]
            return {"reply": reply, "category": "personalized_data", "suggestions": suggestions, "timestamp": now}

        # C. Inquiries about Crops
        all_crops = []
        for f in user_farms:
            for c in f.crops:
                all_crops.append(f"- **{c.crop_name}** on farm *{f.farm_name}* (Season: `{c.season}`) - Sown: `{c.sowing_date or 'N/A'}`")

        if all_crops:
            reply = (
                f"### [Logged Crops for {user.name}]\n\n"
                f"You have **{len(all_crops)} active crop planting(s)** logged:\n\n"
                + "\n".join(all_crops)
            )
        else:
            reply = (
                f"### [Crop Records for {user.name}]\n\n"
                f"You have not logged any specific crops under your farms yet.\n\n"
                f"Go to **Farm Management** to associate crops with your registered farms."
            )
        suggestions = ["What is the ideal sowing season for Wheat?", "How to fertilizer my crops?", "Run a yield prediction"]
        return {"reply": reply, "category": "personalized_data", "suggestions": suggestions, "timestamp": now}

    def _match_crop(self, q: str) -> Optional[str]:
        """Matches crop names from user query."""
        for crop_key in self.crops:
            if crop_key in q:
                return crop_key
        # Common synonyms
        if "paddy" in q:
            return "rice"
        if "corn" in q:
            return "maize"
        if "peanut" in q or "peanuts" in q:
            return "groundnut"
        if "chickpea" in q or "gram" in q or "legume" in q or "dal" in q:
            return "pulses"
        return None

    def _is_out_of_scope(self, q: str) -> bool:
        """
        Detects questions completely outside agriculture, farming, crops, soil, weather,
        or YieldSense AI operations.
        """
        # If any agricultural keywords are in the query, it is in scope
        agri_words = [
            "crop", "crops", "farm", "farms", "farmer", "farming", "agriculture", "agricultural",
            "soil", "ph", "fertilizer", "fertilizers", "npk", "nitrogen", "phosphorus", "potassium",
            "urea", "dap", "ssp", "mop", "compost", "manure", "seed", "seeds", "sow", "sowing",
            "harvest", "harvesting", "yield", "predict", "prediction", "forecast", "weather",
            "rain", "rainfall", "temperature", "heat", "frost", "irrigation", "water", "drip",
            "sprinkler", "drought", "drainage", "disease", "pest", "pests", "blight", "rust",
            "rot", "wilt", "mildew", "bollworm", "aphid", "borer", "ipm", "pesticide", "fungicide",
            "model", "dataset", "accuracy", "rmse", "mae", "linear regression", "wheat", "rice",
            "soybean", "cotton", "maize", "groundnut", "sugarcane", "barley", "pulses", "tea",
            "coffee", "jute", "rotation", "intercrop", "tillage", "mulch", "mulching", "variety",
            "cultivar", "monsoon", "organic"
        ]
        if any(w in q for w in agri_words):
            return False

        # Check for typical off-topic patterns
        off_topic_patterns = [
            r"\b(who is|who was|who wrote|who invented)\b",
            r"\b(capital of|president of|prime minister|movie|song|actor|actress|celebrity)\b",
            r"\b(write a code|write a python|javascript|c\+\+|crypto|bitcoin|stock market)\b",
            r"\b(football|cricket match|olympics|fifa|game|nba)\b",
            r"\b(tell me a joke|write a poem about love|recipe for pizza|travel to)\b"
        ]
        return any(re.search(pat, q) for pat in off_topic_patterns)
