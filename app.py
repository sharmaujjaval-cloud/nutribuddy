import os
import time
import json
import re
from datetime import datetime
import requests
import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------
# Environment & Page Configuration
# ---------------------------------------------------------
load_dotenv()
load_dotenv(".venv/.env")

st.set_page_config(
    page_title="NutriBuddy • SDG 2 Zero Hunger Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "meals_planned" not in st.session_state:
    st.session_state.meals_planned = 3

if "waste_saved_kg" not in st.session_state:
    st.session_state.waste_saved_kg = 2.4

if "money_saved_usd" not in st.session_state:
    st.session_state.money_saved_usd = 18.50

if "prompt_to_submit" not in st.session_state:
    st.session_state.prompt_to_submit = None

# ---------------------------------------------------------
# Custom Styling: Modern Glassmorphic Harvest Theme
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(245, 158, 11, 0.08) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    .hero-title-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.8rem;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(90deg, #34d399, #fbbf24);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        line-height: 1.5;
    }
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.6rem;
    }
    .sdg-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.3rem 0.7rem;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .waste-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.3rem 0.7rem;
        border-radius: 9999px;
        background: rgba(245, 158, 11, 0.18);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.3rem 0.7rem;
        border-radius: 9999px;
        background: rgba(99, 102, 241, 0.18);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }

    /* Cards & Container styles */
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .feature-card:hover {
        border-color: rgba(16, 185, 129, 0.4);
        transform: translateY(-2px);
    }
    .recipe-card {
        background: linear-gradient(145deg, rgba(16, 185, 129, 0.08) 0%, rgba(20, 26, 36, 0.8) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 14px;
        padding: 1.4rem;
        margin-top: 1rem;
    }
    .impact-stat-box {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .impact-stat-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #34d399;
    }
    .impact-stat-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.2rem;
    }

    /* Button polish */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        border-color: #10b981;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25);
    }
    
    /* Shelf life tags */
    .shelf-tag {
        display: inline-block;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-right: 0.4rem;
        font-weight: 600;
    }
    .shelf-pantry { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .shelf-fridge { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .shelf-freezer { background: rgba(168, 85, 247, 0.2); color: #c084fc; }

    /* Tabs formatting */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Comprehensive Knowledge & Recipe Database
# ---------------------------------------------------------
SHELF_LIFE_DB = [
    {
        "food": "Leafy Greens (Spinach, Kale, Lettuce)",
        "category": "Produce",
        "pantry": "Few hours",
        "fridge": "7 – 10 days",
        "freezer": "6 months (blanched)",
        "storage_tip": "Wrap dry leaves in a paper towel inside an airtight container. The towel absorbs rot-causing moisture.",
        "spoilage_signs": "Slime, black spots, yellowing, sour smell.",
        "revive_hack": "Soak limp greens in ice water for 20 minutes to restore crisp cell turgor."
    },
    {
        "food": "Bread & Bakery Loaves",
        "category": "Grains",
        "pantry": "4 – 6 days (cool, dry)",
        "fridge": "Not recommended (stales 3x faster)",
        "freezer": "3 months (sliced)",
        "storage_tip": "Keep room-temp bread in a bread box or paper bag. Never refrigerate bread—freeze slices and toast straight from frozen.",
        "spoilage_signs": "Green/white fuzzy mold, sour fermentation smell.",
        "revive_hack": "Sprinkle stale crust with water droplets and warm in a 350°F (175°C) oven for 5 mins to restore crunchy crust and soft interior."
    },
    {
        "food": "Cooked Rice & Grains",
        "category": "Prepared Food",
        "pantry": "Do not leave at room temp > 2 hrs",
        "fridge": "3 – 5 days",
        "freezer": "4 months",
        "storage_tip": "Cool rapidly in a shallow tray and refrigerate within 90 minutes to prevent Bacillus cereus spore multiplication.",
        "spoilage_signs": "Sour smell, slimy grain texture, discoloration.",
        "revive_hack": "Reheat with 1 tablespoon of water covered in microwave for 90s, or fry with oil and garlic into fried rice."
    },
    {
        "food": "Potatoes & Sweet Potatoes",
        "category": "Produce",
        "pantry": "3 – 5 weeks (cool, dark)",
        "fridge": "Do not refrigerate (starches turn to sugars)",
        "freezer": "10 months (parboiled/mashed)",
        "storage_tip": "Store in a breathable paper bag or basket in a dark cabinet. Keep far away from onions!",
        "spoilage_signs": "Deep wrinkling, green flesh (solanine toxin), soft mushy spots.",
        "revive_hack": "Small sprouts can be carved out; if skin is slightly soft, peel and boil for mashed potatoes or rustic potato soup."
    },
    {
        "food": "Onions & Garlic",
        "category": "Produce",
        "pantry": "1 – 2 months",
        "fridge": "Only if chopped (airtight, 5 days)",
        "freezer": "6 months (chopped)",
        "storage_tip": "Keep in a cool, dark, dry basket with good airflow. Ethylene from onions makes potatoes rot faster, so store separately.",
        "spoilage_signs": "Black mold on outer layers, soft neck, translucent mush.",
        "revive_hack": "If green shoots emerge from garlic or onion, plant them in a cup of water or soil for instant fresh scallion/garlic greens."
    },
    {
        "food": "Carrots & Celery",
        "category": "Produce",
        "pantry": "3 – 4 days",
        "fridge": "3 – 4 weeks (submerged in water)",
        "freezer": "10 months (blanched)",
        "storage_tip": "Store celery wrapped in aluminum foil. For carrots, cut green tops off and store in a container of cold water, changing water weekly.",
        "spoilage_signs": "White fuzzy mold, slimy skin, mushy core.",
        "revive_hack": "Limp carrots or rubbery celery will snap back like new after 30 minutes in a cold ice water bath."
    },
    {
        "food": "Eggs",
        "category": "Dairy & Protein",
        "pantry": "Not recommended in warm climates",
        "fridge": "4 – 5 weeks",
        "freezer": "1 year (beaten without shell)",
        "storage_tip": "Store in their original carton on the middle fridge shelf, not in the door where temperature fluctuates.",
        "spoilage_signs": "Float test: Fresh eggs sink flat. Bad eggs float to the surface (gas buildup from decay).",
        "revive_hack": "Older eggs that sink but stand on end are ideal for hard-boiling because they peel effortlessly!"
    },
    {
        "food": "Hard & Semi-Hard Cheeses",
        "category": "Dairy",
        "pantry": "1 – 2 days",
        "fridge": "3 – 6 weeks",
        "freezer": "6 months (grated)",
        "storage_tip": "Wrap in parchment or wax paper, then loosely in plastic. Cheese needs to breathe; tight plastic traps moisture and invites mold.",
        "spoilage_signs": "Surface mold on hard cheese (Cheddar, Parmesan) can be cut away 1 inch around the mold safely. Discard if mold penetrates soft cheese.",
        "revive_hack": "Save hard cheese rinds in the freezer; drop into simmering vegetable or bean soup for rich umami flavor."
    },
    {
        "food": "Canned Beans, Lentils & Tomatoes",
        "category": "Pantry Staples",
        "pantry": "2 – 5 years (unopened)",
        "fridge": "4 – 5 days (transferred to glass container)",
        "freezer": "3 months (cooked)",
        "storage_tip": "Never leave opened food in the tin can; transfer unused portions to an airtight glass or plastic container.",
        "spoilage_signs": "Bulging lid, dented seams, spurting liquid when punctured, metallic odor.",
        "revive_hack": "Rinse canned beans to reduce sodium by up to 40% while preserving fiber and protein."
    },
    {
        "food": "Bananas",
        "category": "Produce",
        "pantry": "3 – 7 days",
        "fridge": "5 – 7 days (peel turns black, but flesh stays firm)",
        "freezer": "8 months (peeled)",
        "storage_tip": "Wrap the stems (crown) in plastic wrap or foil to slow ethylene gas emission. Separate from other fruit to prevent premature ripening.",
        "spoilage_signs": "Liquefying fruit, fermented alcohol odor, black fruit flies.",
        "revive_hack": "Overripe, speckled brown bananas are at peak sweetness. Peel and freeze for smoothies, oatmeal, or 3-ingredient banana pancakes."
    }
]

# ---------------------------------------------------------
# Dynamic Offline Knowledge & Recipe Synthesis Engine
# ---------------------------------------------------------
def synthesize_dynamic_recipe(ingredients_str: str, dietary: str, budget: str, equip: str = "Stovetop / Pan", time_target: str = "20 mins") -> str:
    """
    Intelligently parses user pantry items, categorizes staples,
    and dynamically constructs an authentic zero-waste recipe tailored
    to diet and budget.
    """
    ing_lower = ingredients_str.lower()
    items = [x.strip() for x in re.split(r'[,;\n+]', ing_lower) if x.strip()]
    
    # Identify food groups
    has_rice = any(k in ing_lower for k in ["rice", "grain", "quinoa", "couscous"])
    has_bread = any(k in ing_lower for k in ["bread", "toast", "bun", "bagel", "crust"])
    has_pasta = any(k in ing_lower for k in ["pasta", "noodle", "spaghetti", "macaroni"])
    has_potato = any(k in ing_lower for k in ["potato", "potatoes", "sweet potato", "yam"])
    has_egg = any(k in ing_lower for k in ["egg", "eggs"])
    has_beans = any(k in ing_lower for k in ["bean", "beans", "lentil", "lentils", "chickpea", "dhal", "dal"])
    has_canned_fish = any(k in ing_lower for k in ["tuna", "sardine", "mackerel", "salmon", "canned fish"])
    has_tofu = any(k in ing_lower for k in ["tofu", "tempeh", "soy"])
    has_greens = any(k in ing_lower for k in ["spinach", "kale", "cabbage", "lettuce", "greens", "chard"])
    has_tomato = any(k in ing_lower for k in ["tomato", "tomatoes", "paste", "puree", "marinara"])
    has_onion_garlic = any(k in ing_lower for k in ["onion", "garlic", "shallot", "leek", "scallion"])
    has_dairy = any(k in ing_lower for k in ["cheese", "milk", "yogurt", "butter"])

    # Determine Dish Architecture
    if has_rice or (not has_pasta and not has_bread and not has_potato and not has_beans):
        dish_name = "Golden Pantry Leftover Stir-Fry Bowl"
        carb_desc = "Leftover cooked rice or grains"
        prep_method = [
            "**Prep the Base**: Heat 1 tbsp cooking oil in a pan over medium heat. Sizzle chopped aromatics (onions, garlic, or vegetable stems) for 2–3 minutes until fragrant.",
            "**Toss & Crisp**: Add your cooked rice/grains into the skillet. Press down gently with a spatula to get crispy golden edges without burning.",
            "**Incorporate Veggies & Protein**: Add in vegetables and your protein source (scramble an egg on one side, or fold in beans/tofu/fish). Toss with a splash of soy sauce, salt, pepper, or pinch of curry powder.",
            "**Garnish & Serve**: Finish with finely sliced green tops or a squeeze of lemon juice for brightness."
        ]
        waste_tip = "Never toss dry leftover rice—dry cold rice makes the absolute best crispy fried rice because it doesn't get soggy!"
    elif has_bread:
        dish_name = "Savory Crispy Bread & Vegetable Skillet Hash"
        carb_desc = "Stale bread or crusts cut into cubes"
        prep_method = [
            "**Toast the Croutons**: Cut stale bread into bite-sized cubes. Heat 1 tbsp oil or butter in a skillet, toast the bread cubes for 4 minutes until golden brown and crunchy.",
            "**Sauté the Garden Veggies**: Push croutons to the side or remove to a plate. Toss in vegetables and onions with a pinch of salt and black pepper.",
            "**Combine & Bind**: Return bread cubes to the pan. If using eggs, pour beaten eggs over the mixture and cook gently like a savory French toast hash. If vegan, toss with beans and diced tomatoes.",
            "**Serve Hot**: Enjoy while the bread has soaked in the savory juices while maintaining a crisp bite."
        ]
        waste_tip = "Stale bread is dry, which makes it perfect for absorbing broths, garlic oil, and eggs without falling apart."
    elif has_pasta:
        dish_name = "15-Minute Zero-Waste Pasta Aglio e Pantry"
        carb_desc = "Cooked or dry pasta / noodles"
        prep_method = [
            "**Cook / Reheat Pasta**: Boil pasta in salted water (save 1/2 cup of starchy pasta water before draining!). If pasta is already cooked, rinse with warm water.",
            "**Infuse the Oil**: In a pan, warm 1.5 tbsp oil with minced garlic, onion, or chili flakes over gentle low heat.",
            "**Wilt the Veggies**: Add chopped greens, tomatoes, or leftover vegetables. Sauté until tender.",
            "**Emulsify**: Add pasta and 2-3 tbsp reserved pasta water into the skillet. Toss vigorously—the starchy water binds with the oil to create a silky, glossy sauce.",
            "**Protein Add-in**: Fold in beans, canned tuna, or an egg yolk off heat for rich creaminess."
        ]
        waste_tip = "Starchy pasta water is liquid gold for sauces! It emulsifies oil and broth into restaurant-quality sauce for $0."
    elif has_potato:
        dish_name = "Rustic Crispy Potato & Garden Scramble"
        carb_desc = "Boiled or roasted potatoes, sliced or crushed"
        prep_method = [
            "**Sizzle the Potatoes**: Cut potatoes into 1/2-inch pieces. Heat oil in a pan, sear potatoes over medium-high heat until edges turn golden and blistered (5 mins).",
            "**Add Seasoning & Onions**: Toss in diced onions, garlic, and available vegetables (carrots, peppers, greens).",
            "**Layer Protein**: Crack in eggs, or toss in canned beans/lentils. Season with salt, cumin, smoked paprika, or black pepper.",
            "**Steam & Finish**: Cover pan for 2 minutes to let greens wilt and eggs set. Serve hot."
        ]
        waste_tip = "Keep potato skins on! Up to 50% of the dietary fiber and key minerals (potassium & iron) are located in and right beneath the skin."
    else:
        dish_name = "One-Pot Hearty Protein & Vegetable Stew"
        carb_desc = "Pantry pulses, root vegetables, and broth"
        prep_method = [
            "**Sauté the Base**: Warm 1 tbsp oil in a pot. Cook chopped onions and garlic until translucent and sweet.",
            "**Simmer with Liquid**: Add 1.5 cups of water or vegetable broth, diced tomatoes, potatoes or beans, and spices (turmeric, cumin, or curry powder).",
            "**Tenderize**: Cover and simmer gently on low heat for 12–15 minutes until vegetables are tender and flavors meld.",
            "**Final Touch**: Stir in delicate leafy greens during the last 2 minutes so they stay vibrant green and nutrient-dense."
        ]
        waste_tip = "Save vegetable peels, carrot tops, and onion skins in a freezer bag. Boil them together to make zero-cost homemade vegetable broth!"

    # Tailor for dietary constraints
    dietary_notice = ""
    if "vegan" in dietary.lower():
        dietary_notice = "🌱 **100% Plant-Based Verified**: Uses legumes/tofu instead of animal proteins."
    elif "halal" in dietary.lower():
        dietary_notice = "🌙 **Halal Compliant**: Clean vegetable & permissible protein preparation."
    elif "diabetic" in dietary.lower():
        dietary_notice = "🩸 **Diabetic-Friendly**: High fiber base with low glycemic index to stabilize blood glucose."
    elif "iron" in dietary.lower() or "maternal" in dietary.lower():
        dietary_notice = "🛡️ **High-Iron & Folate**: Rich in plant iron and paired with Vitamin C for optimal absorption."

    steps_formatted = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(prep_method)])
    
    ingredients_list_str = "\n".join([f"- **{it.capitalize()}** (from your pantry)" for it in items]) if items else "- Mixed pantry staples & aromatics"

    return f"""### 🍲 {dish_name}
{dietary_notice}
**Profile**: {dietary} | **Budget**: {budget} | **Equipment**: {equip}

---

#### ⏱️ Recipe Overview
* **Active Prep Time**: ~{time_target}
* **Estimated Cost**: **~$0.90 – $1.40 per portion**
* **SDG 2 Impact**: 100% Zero Food Waste & High Nutrient Utilization

#### 🛒 Ingredients Used:
{ingredients_list_str}
- 1–2 tbsp cooking oil or butter
- Salt, pepper, garlic, or your favorite spices to taste

#### 👨‍🍳 Step-by-Step Instructions:
{steps_formatted}

#### 💡 NutriBuddy Zero-Waste Secret:
> {waste_tip}

#### 📊 Nutritional Estimate (Per Serving):
* **Energy**: ~380 – 450 kcal
* **Protein**: 14 – 20 g (High Satiety)
* **Fiber**: 6 – 9 g (Digestive & Blood Sugar Support)
* **Key Micronutrients**: Iron, Potassium, Vitamin A & C
"""

def generate_offline_response(prompt: str, recipe_mode: bool, dietary: str, budget: str) -> str:
    """
    Modular, rich offline knowledge engine. Covers recipes, budget plans,
    storage, micronutrients, food safety, and UN SDG 2 targets.
    """
    p = prompt.lower().strip()

    # 1. Leftovers & Recipe Query
    if recipe_mode or any(k in p for k in ["recipe", "leftover", "cook", "ingredients", "dish from", "meal from"]):
        # Extract pantry ingredients from prompt
        cleaned = re.sub(r'(recipe|leftover|cook|ingredients|suggest|make|food|can i|please|how to|i have|with)+', ' ', p)
        return synthesize_dynamic_recipe(cleaned, dietary, budget)

    # 2. Food Storage, Spoilage, and Waste Prevention (High specificity)
    if any(k in p for k in ["store", "waste", "spoil", "fresh", "preserve", "rot", "mold", "freezer", "shelf", "expire"]):
        return """### 🥫 Food Storage & Spoilage Prevention Guide

According to the UN FAO, over **1.3 billion tons of food is wasted globally every year** while 730+ million people experience hunger. Keep your food fresh 2x longer with these proven kitchen techniques:

1. **Leafy Greens & Herbs**:
   * Wash only right before eating. Wrap dry unwashed greens in a reusable paper or cloth towel inside an airtight container. The towel absorbs moisture while keeping high humidity.
   * Treat fresh cilantro, parsley, and asparagus like cut flowers: trim stem ends and stand upright in a glass jar with 1 inch of water in the fridge door.

2. **Bread & Bakery**:
   * **Rule #1: Never refrigerate bread!** The 40°F (4°C) fridge temperature accelerates retrogradation, crystallizing starch molecules and making bread stale 3x faster.
   * Store 2–3 days of bread at room temp; slice and freeze the rest. Toast frozen slices directly without thawing.

3. **Ethylene Gas Separation**:
   * Apples, bananas, tomatoes, and onions emit high levels of natural ethylene ripening gas.
   * **Keep potatoes far from onions**: Stored together, onions trigger premature potato sprouting and rot within days.

4. **Reviving Dehydrated Produce**:
   * Limp celery, floppy carrots, and bendable radishes are just dehydrated, not rotten!
   * Submerge them in a bowl of ice water for 30–45 minutes—capillary action refills their plant cells with water, making them crisp and crunchy again.
"""

    # 3. Micronutrients, Anemia & Malnutrition (High specificity)
    if any(k in p for k in ["iron", "vitamin", "malnutrition", "nutrient", "anemia", "deficiency", "zinc", "calcium", "stunting"]):
        return """### 🛡️ Defeating Hidden Hunger: Affordable Micronutrients

UN SDG Target 2.2 focuses on eradicating all forms of malnutrition, including micronutrient deficiencies ("hidden hunger") affecting over 2 billion people worldwide:

#### 1. Iron Deficiency & Anemia Defense
* **Symptoms**: Chronic fatigue, dizziness, cold hands/feet, brain fog, brittle nails.
* **Top Affordable Sources**: Brown lentils, chickpeas, dark leafy greens (spinach, moringa, kale), pumpkin seeds, fortified whole grains.
* **The Synergy Hack**: Plant-based (non-heme) iron requires an acidic environment to convert into absorbable Fe2+. Always pair lentils/beans with **Vitamin C** (lemon juice, tomatoes, bell peppers).
* **Caution**: Tannins in black tea and coffee block up to 60% of iron absorption when drank with meals. Drink them 1 hour before or after eating.

#### 2. Vitamin A (Vision & Immune Barrier)
* **Essential for**: Night vision, skin integrity, lung and gut lining defense against pathogens.
* **Affordable Sources**: Carrots, sweet potatoes, pumpkin, dark green leaves.
* **Absorption Hack**: Beta-carotene is fat-soluble. Always cook with a teaspoon of oil or seeds to absorb the vitamins.

#### 3. Zinc (Cell Division & Child Growth)
* **Crucial for**: Wound healing, immune defense, cognitive development, preventing childhood stunting.
* **Affordable Sources**: Whole oats, dry beans, sesame seeds, sunflower seeds, eggs.
"""

    # 4. UN SDG 2 Zero Hunger & Global Food Security
    if any(k in p for k in ["sdg", "zero hunger", "hunger", "goal", "united nations", "fao", "un", "target"]):
        return """### 🌍 Understanding UN Sustainable Development Goal 2: Zero Hunger

**Goal 2: End hunger, achieve food security and improved nutrition, and promote sustainable agriculture by 2030.**

#### Key Targets Established by the United Nations:
1. **Target 2.1**: Universal access to safe, nutritious, and sufficient food year-round.
2. **Target 2.2**: End all forms of malnutrition, including halting stunting and wasting in children under 5, and addressing nutritional needs of pregnant and lactating women.
3. **Target 2.3**: Double the agricultural productivity and incomes of small-scale food producers (farmers, herders, fishers).
4. **Target 2.4**: Ensure sustainable food production systems and implement climate-resilient farming practices.
5. **Target 12.3 (Interlinked)**: Halve per-capita global food waste at retail and consumer levels.

#### Practical Actions You Can Take Today:
* **Zero-Waste Cooking**: Use vegetable peelings for stocks, stale bread for croutons, overripe fruit for baking.
* **Shift to Legume Staples**: Pulses require significantly less water and fertilizer to grow, fixing natural nitrogen into the soil.
* **Support Community Fridges & Food Drives**: Donate surplus unexpired pantry items to local hunger relief programs.
"""

    # 5. Budget Meal Plans & Cost Saving
    if any(k in p for k in ["budget", "cheap", "cost", "dollar", "$", "money", "affordable", "student", "plan", "grocer"]):
        return f"""### 💰 High-Nutrition, Low-Cost Meal Plan (~$3.00 to $4.50 / Day)

**Personalized Profile**: {dietary} • Budget Focus: {budget} (SDG Target 2.1)

#### 🌅 1. Breakfast: Golden Power Porridge (~$0.55)
* **Ingredients**: 1/2 cup rolled oats, 1 cup water/milk, 1 tbsp crushed peanuts or peanut butter, 1/2 sliced ripe banana, dash of cinnamon.
* **Nutrition**: Beta-glucan soluble fiber for sustained energy + 9g plant protein.

#### ☀️ 2. Lunch: Mediterranean Lentil & Seasonal Veggie Bowl (~$1.15)
* **Ingredients**: 1 cup cooked brown lentils, 1 cup rice or bulgur, shredded cabbage or spinach, squeeze of fresh lemon, 1 tsp oil, pinch of cumin & garlic.
* **Nutrition**: Complete protein (all 9 essential amino acids) + 6.5mg non-heme iron. Vitamin C from lemon boosts iron absorption by 300%.

#### 🌙 3. Dinner: Hearty Kidney Bean & Sweet Potato Stew (~$1.35)
* **Ingredients**: 1 cup cooked kidney beans, 1 diced sweet potato or regular potato, canned or fresh tomatoes, onion, garlic, turmeric.
* **Nutrition**: Vitamin A (beta-carotene for immune health), potassium, and 14g gut-friendly dietary fiber.

#### 🍎 4. Snack: Toasted Spiced Chickpeas or Hard-Boiled Egg (~$0.40)
* **Benefit**: Protein and zinc to curb cravings between meals.

---
💡 **NutriBuddy Budget Rule**: Buying dried pulses (lentils, chickpeas, beans) in 1kg bulk bags costs up to **75% less per gram of protein** than canned equivalents and 85% less than animal meats.
"""

    # 3. Storage, Spoilage, and Food Waste
    if any(k in p for k in ["store", "waste", "spoil", "fresh", "preserve", "rot", "mold", "freezer", "shelf", "expire"]):
        return """### 🥫 Food Storage & Spoilage Prevention Guide

According to the UN FAO, over **1.3 billion tons of food is wasted globally every year** while 730+ million people experience hunger. Keep your food fresh 2x longer with these proven kitchen techniques:

1. **Leafy Greens & Herbs**:
   * Wash only right before eating. Wrap dry unwashed greens in a reusable paper or cloth towel inside an airtight container. The towel absorbs moisture while keeping high humidity.
   * Treat fresh cilantro, parsley, and asparagus like cut flowers: trim stem ends and stand upright in a glass jar with 1 inch of water in the fridge door.

2. **Bread & Bakery**:
   * **Rule #1: Never refrigerate bread!** The 40°F (4°C) fridge temperature accelerates retrogradation, crystallizing starch molecules and making bread stale 3x faster.
   * Store 2–3 days of bread at room temp; slice and freeze the rest. Toast frozen slices directly without thawing.

3. **Ethylene Gas Separation**:
   * Apples, bananas, tomatoes, and onions emit high levels of natural ethylene ripening gas.
   * **Keep potatoes far from onions**: Stored together, onions trigger premature potato sprouting and rot within days.

4. **Reviving Dehydrated Produce**:
   * Limp celery, floppy carrots, and bendable radishes are just dehydrated, not rotten!
   * Submerge them in a bowl of ice water for 30–45 minutes—capillary action refills their plant cells with water, making them crisp and crunchy again.
"""

    # 4. Micronutrients, Anemia & Malnutrition
    if any(k in p for k in ["iron", "vitamin", "malnutrition", "nutrient", "anemia", "deficiency", "zinc", "calcium"]):
        return """### 🛡️ Defeating Hidden Hunger: Affordable Micronutrients

UN SDG Target 2.2 focuses on eradicating all forms of malnutrition, including micronutrient deficiencies ("hidden hunger") affecting over 2 billion people worldwide:

#### 1. Iron Deficiency & Anemia Defense
* **Symptoms**: Chronic fatigue, dizziness, cold hands/feet, brain fog, brittle nails.
* **Top Affordable Sources**: Brown lentils, chickpeas, dark leafy greens (spinach, moringa, kale), pumpkin seeds, fortified whole grains.
* **The Synergy Hack**: Plant-based (non-heme) iron requires an acidic environment to convert into absorbable Fe2+. Always pair lentils/beans with **Vitamin C** (lemon juice, tomatoes, bell peppers).
* **Caution**: Tannins in black tea and coffee block up to 60% of iron absorption when drank with meals. Drink them 1 hour before or after eating.

#### 2. Vitamin A (Vision & Immune Barrier)
* **Essential for**: Night vision, skin integrity, lung and gut lining defense against pathogens.
* **Affordable Sources**: Carrots, sweet potatoes, pumpkin, dark green leaves.
* **Absorption Hack**: Beta-carotene is fat-soluble. Always cook with a teaspoon of oil or seeds to absorb the vitamins.

#### 3. Zinc (Cell Division & Child Growth)
* **Crucial for**: Wound healing, immune defense, cognitive development, preventing childhood stunting.
* **Affordable Sources**: Whole oats, dry beans, sesame seeds, sunflower seeds, eggs.
"""

    # 5. UN SDG 2 Zero Hunger & Global Food Security
    if any(k in p for k in ["sdg", "zero hunger", "hunger", "goal", "united nations", "fao", "un", "target"]):
        return """### 🌍 Understanding UN Sustainable Development Goal 2: Zero Hunger

**Goal 2: End hunger, achieve food security and improved nutrition, and promote sustainable agriculture by 2030.**

#### Key Targets Established by the United Nations:
1. **Target 2.1**: Universal access to safe, nutritious, and sufficient food year-round.
2. **Target 2.2**: End all forms of malnutrition, including halting stunting and wasting in children under 5, and addressing nutritional needs of pregnant and lactating women.
3. **Target 2.3**: Double the agricultural productivity and incomes of small-scale food producers (farmers, herders, fishers).
4. **Target 2.4**: Ensure sustainable food production systems and implement climate-resilient farming practices.
5. **Target 12.3 (Interlinked)**: Halve per-capita global food waste at retail and consumer levels.

#### Practical Actions You Can Take Today:
* **Zero-Waste Cooking**: Use vegetable peelings for stocks, stale bread for croutons, overripe fruit for baking.
* **Shift to Legume Staples**: Pulses require significantly less water and fertilizer to grow, fixing natural nitrogen into the soil.
* **Support Community Fridges & Food Drives**: Donate surplus unexpired pantry items to local hunger relief programs.
"""

    # 6. Default Encouraging Assistant Greeting
    return f"""### 🥗 Welcome to NutriBuddy — Your SDG 2 Nutrition & Zero-Hunger Partner

I'm here to help you turn kitchen ingredients into nutritious meals, stretch your food budget, and prevent food waste!

#### 💡 Instant Things You Can Try:
1. **Leftover Kitchen Rescue**: Type the items in your fridge (e.g., *"I have 2 eggs, leftover pasta, and half an onion"*) to get an immediate custom recipe.
2. **Low-Cost Meal Planning**: Ask for a *$3/day high-protein student meal plan* or a *weekly family grocery list*.
3. **Food Storage & Shelf Life**: Ask how to store greens, bread, or dairy to stop them from spoiling.
4. **Micronutrient Defense**: Learn the best plant-based combinations to prevent anemia and vitamin deficiencies.

*Current Profile: {dietary} • {budget} Budget.*

What would you like to cook or learn today?
"""

# ---------------------------------------------------------
# Sidebar Configuration & Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Control Center")
    
    # Mode selection
    recipe_mode = st.toggle("🍲 Recipe Mode", value=False, help="Forces responses to be formatted as structured zero-waste recipes.")
    demo_mode = st.toggle("🧪 Force Offline Engine", value=False, help="Use the fast built-in dynamic knowledge engine without external network calls.")
    
    st.markdown("---")
    st.markdown("### 🥗 Dietary & Budget Profile")
    dietary_pref = st.selectbox(
        "Dietary Preference",
        ["Standard / Omnivore", "Vegetarian", "Vegan", "Halal", "Diabetic-Friendly", "High-Iron / Maternal", "Gluten-Free"],
        index=0
    )
    budget_level = st.selectbox(
        "Budget Tier",
        ["Ultra-Low Cost / Survival ($1-$2/day)", "Student Budget ($3-$5/day)", "Balanced Family ($5-$8/day)"],
        index=1
    )

    st.markdown("---")
    st.markdown("### ⚡ AI Configuration (OpenRouter)")
    
    # Retrieve env key if available
    env_api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not env_api_key:
        for env_path in [".env", ".venv/.env"]:
            if os.path.exists(env_path):
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f.read().splitlines():
                            line = line.strip()
                            if line.startswith("OPENROUTER_API_KEY="):
                                env_api_key = line.split("OPENROUTER_API_KEY=", 1)[1].strip().strip('"').strip("'")
                except Exception:
                    pass

    user_api_key = st.text_input(
        "OpenRouter API Key",
        value="",
        type="password",
        placeholder="sk-or-v1-... (auto-loaded from .env)",
        help="Reads OPENROUTER_API_KEY from .env automatically or paste your key here."
    )
    user_api_key = (user_api_key or "").strip()
    env_api_key = (env_api_key or "").strip()
    active_api_key = user_api_key or env_api_key

    model_choice = st.selectbox(
        "AI Model",
        ["openrouter/free"],
        index=0,
        help="OpenRouter automatically routes this to an available free model."
    )

    col_test, col_clear = st.columns(2)
    with col_test:
        test_key_btn = st.button("🧪 Test API", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    if test_key_btn:
        if not active_api_key:
            st.warning("⚠️ No API key found. Please add `OPENROUTER_API_KEY` to your `.env` file or paste it above.")
        else:
            with st.spinner("Testing OpenRouter connection..."):
                try:
                    test_headers = {
                        "Authorization": f"Bearer {active_api_key}",
                        "HTTP-Referer": "http://localhost:8502",
                        "X-Title": "NutriBuddy",
                        "Content-Type": "application/json"
                    }
                    test_payload = {
                        "model": model_choice,
                        "messages": [{"role": "user", "content": "Say 'NutriBuddy Ready!' in 3 words"}],
                        "max_tokens": 20,
                        "provider": {"sort": "latency"}
                    }
                    resp = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=test_headers,
                        json=test_payload,
                        timeout=20
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        reply_content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        routed_model = data.get("model", model_choice)
                        st.success(f"✅ **OpenRouter Connection Succeeded!**\n\n- **Model**: `{routed_model}`\n- **Response**: *{reply_content}*")
                    elif resp.status_code == 401:
                        st.error("🚫 **Invalid or Missing API Key (401 Unauthorized)**: OpenRouter rejected the key. Please check your `OPENROUTER_API_KEY` in `.env`.")
                    elif resp.status_code in [404, 429, 503]:
                        st.warning(
                            f"⚠️ **OpenRouter Free Model Unavailable ({resp.status_code})**: "
                            "The free model router is currently busy or rate-limited. "
                            "The Offline Knowledge Engine remains available."
                        )
                    else:
                        try:
                            error_data = resp.json()
                            error_message = error_data.get("error", {}).get("message", "Unknown API error")
                        except Exception:
                            error_message = "Unknown API error"
                        st.error(f"❌ **OpenRouter API Error ({resp.status_code})**: {str(error_message)[:250]}")
                except requests.exceptions.Timeout:
                    st.warning("⏱️ OpenRouter request timed out. The offline knowledge engine remains ready as fallback.")
                except Exception as ex:
                    st.error(f"❌ Connection Error: {str(ex)}")

    st.markdown("---")
    # Live SDG 2 Session Impact Metrics
    st.markdown("### 📈 Your SDG 2 Session Impact")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"""
        <div class="impact-stat-box">
            <div class="impact-stat-number">{st.session_state.meals_planned}</div>
            <div class="impact-stat-label">Meals Planned</div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
        <div class="impact-stat-box">
            <div class="impact-stat-number">{st.session_state.waste_saved_kg:.1f}kg</div>
            <div class="impact-stat-label">Food Saved</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-top: 0.6rem;" class="impact-stat-box">
        <div class="impact-stat-number">${st.session_state.money_saved_usd:.2f}</div>
        <div class="impact-stat-label">Estimated Money Saved</div>
    </div>
    """, unsafe_allow_html=True)

    # Chat Transcript Export Options
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 📥 Export Session")
        chat_markdown = "# 🥗 NutriBuddy Chat Transcript (UN SDG 2)\n\n"
        chat_markdown += f"*Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        chat_markdown += f"*Dietary Profile: {dietary_pref} | Budget Tier: {budget_level}*\n\n---\n\n"
        for m in st.session_state.messages:
            chat_markdown += f"### {m['role'].capitalize()}\n{m['content']}\n\n"

        st.download_button(
            "📄 Export as Markdown (.md)",
            data=chat_markdown,
            file_name=f"nutribuddy_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )

# ---------------------------------------------------------
# Main Page Header & Hero
# ---------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title-row">
        <div>
            <h1 class="hero-title">🥗 NutriBuddy</h1>
            <div class="hero-sub">
                Intelligent Assistant for <strong>UN SDG 2: Zero Hunger</strong> • High-Nutrition Low-Cost Cooking, Food Waste Elimination & Pantry Rescue.
            </div>
        </div>
        <div class="badge-container">
            <span class="sdg-badge">🎯 SDG 2: Zero Hunger</span>
            <span class="waste-badge">♻️ Zero Food Waste</span>
            <span class="ai-badge">⚡ OpenRouter Free AI + Smart Engine</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Multi-Tab Navigation
# ---------------------------------------------------------
tab_chat, tab_studio, tab_planner, tab_storage, tab_calc = st.tabs([
    "💬 NutriBuddy Chat",
    "🍳 Smart Leftover Studio",
    "📅 7-Day Budget Meal Planner",
    "🥫 Food Shelf-Life & Spoilage",
    "📊 Macro Target & Impact Calculator"
])

# ---------------------------------------------------------
# TAB 1: NutriBuddy Chat Assistant
# ---------------------------------------------------------
with tab_chat:
    # Starter Prompt Chips
    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.4rem; font-weight: 600;'>✨ Quick Starter Questions:</p>", unsafe_allow_html=True)
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        if st.button("🍳 $3 High-Protein Plan", use_container_width=True):
            st.session_state.prompt_to_submit = "Create a healthy, high-protein daily meal plan for under $3 using accessible staple ingredients."
            st.rerun()
    with c_p2:
        if st.button("🥬 Stop Veggie Spoilage", use_container_width=True):
            st.session_state.prompt_to_submit = "How do I store leafy greens, bread, and root vegetables so they stay fresh 2x longer?"
            st.rerun()
    with c_p3:
        if st.button("👶 Affordable Iron & Vitamins", use_container_width=True):
            st.session_state.prompt_to_submit = "What are the cheapest plant-based sources of iron and vitamin A to prevent anemia and malnutrition?"
            st.rerun()
    with c_p4:
        if st.button("🌍 What is UN SDG 2?", use_container_width=True):
            st.session_state.prompt_to_submit = "Explain UN Sustainable Development Goal 2 (Zero Hunger) and 4 practical habits people can adopt to reduce hunger."
            st.rerun()

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input bar
    chat_input_val = st.chat_input("Ask NutriBuddy about leftover ingredients, budget meal prep, food storage, or SDG 2...")

    # Determine prompt to run
    prompt_to_run = None
    if st.session_state.prompt_to_submit:
        prompt_to_run = st.session_state.prompt_to_submit
        st.session_state.prompt_to_submit = None
    elif chat_input_val:
        prompt_to_run = chat_input_val

    if prompt_to_run:
        # Append and show user message
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Assistant response
        with st.chat_message("assistant"):
            final_reply = ""
            used_offline = False

            # Check if using offline mode
            if demo_mode or not active_api_key:
                used_offline = True
                with st.spinner("NutriBuddy is consulting the SDG 2 Knowledge Engine..."):
                    time.sleep(0.2)
                    final_reply = generate_offline_response(
                        prompt_to_run,
                        recipe_mode=recipe_mode,
                        dietary=dietary_pref,
                        budget=budget_level
                    )
                    st.markdown(final_reply)
                    if not active_api_key and not demo_mode:
                        st.caption("ℹ️ *Powered by NutriBuddy Intelligent Offline Engine. Add OPENROUTER_API_KEY to your .env file for live model streaming.*")
            else:
                # Prepare System Prompt
                sys_instruction = (
                    "You are NutriBuddy, an expert compassionate AI nutritionist and food security advisor dedicated to UN SDG 2 (Zero Hunger). "
                    f"User Profile: Dietary Preference is '{dietary_pref}', Budget Tier is '{budget_level}'. "
                    "Your mission: provide affordable, highly nutritious culinary guidance, food waste reduction strategies, and smart leftover recipes. "
                    "Be practical, encouraging, clear, and prioritize low-cost, accessible staple ingredients. Include practical zero-waste cooking tips."
                )
                if recipe_mode:
                    sys_instruction += " RECIPE MODE: Always format answer with Prep Time, Cost Estimate, Ingredients, and Step-by-Step Instructions."

                # Construct OpenAI-compatible message history for OpenRouter
                openrouter_messages = [{"role": "system", "content": sys_instruction}]
                for m in st.session_state.messages:
                    openrouter_messages.append({
                        "role": "user" if m["role"] == "user" else "assistant",
                        "content": m["content"]
                    })

                headers = {
                    "Authorization": f"Bearer {active_api_key}",
                    "HTTP-Referer": "http://localhost:8502",
                    "X-Title": "NutriBuddy",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_choice,
                    "messages": openrouter_messages,
                    "stream": True,
                    "temperature": 0.7,
                    "max_tokens": 700,
                    "provider": {"sort": "latency"}
                }

                # Attempt Streaming from OpenRouter API
                try:
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        stream=True,
                        timeout=35
                    )

                    if response.status_code == 200:
                        def stream_openrouter_chunks():
                            for line in response.iter_lines():
                                if line:
                                    decoded_line = line.decode('utf-8').strip()
                                    if decoded_line.startswith('data: '):
                                        data_content = decoded_line[6:].strip()
                                        if data_content == '[DONE]':
                                            break
                                        try:
                                            chunk_json = json.loads(data_content)
                                            delta = chunk_json.get('choices', [{}])[0].get('delta', {})
                                            chunk_text = delta.get('content', '')
                                            if chunk_text:
                                                yield chunk_text
                                        except Exception:
                                            pass

                        final_reply = st.write_stream(stream_openrouter_chunks())

                    elif response.status_code == 401:
                        st.error("🚫 **Invalid OpenRouter Key (401 Unauthorized)**: Please verify your `OPENROUTER_API_KEY` in `.env`.")
                        used_offline = True
                    elif response.status_code in [404, 429, 503]:
                        st.warning(
                            f"⚠️ **OpenRouter Free Model Notice ({response.status_code})**: "
                            "The free model router is temporarily unavailable or rate-limited. "
                            "Switching to the Offline Knowledge Engine."
                        )
                        used_offline = True
                    else:
                        # Show only the provider's error message; never echo request headers or the API key.
                        try:
                            error_data = response.json()
                            error_message = error_data.get("error", {}).get("message", "Unknown API error")
                        except Exception:
                            error_message = "Unknown API error"
                        st.warning(
                            f"⚠️ **OpenRouter API Notice ({response.status_code})**: "
                            f"{str(error_message)[:250]}. Switching to the Offline Knowledge Engine."
                        )
                        used_offline = True

                except requests.exceptions.Timeout:
                    st.warning("⏱️ OpenRouter request timed out. Seamlessly switching to Offline Knowledge Engine.")
                    used_offline = True
                except Exception as ex:
                    st.warning(f"⚠️ OpenRouter connection notice ({str(ex)[:100]}...). Seamlessly switching to Offline Knowledge Engine.")
                    used_offline = True

                # Fallback if streaming failed or threw error
                if used_offline or not final_reply:
                    final_reply = generate_offline_response(
                        prompt_to_run,
                        recipe_mode=recipe_mode,
                        dietary=dietary_pref,
                        budget=budget_level
                    )
                    st.markdown(final_reply)

            # Update session state & impact metrics
            st.session_state.messages.append({"role": "assistant", "content": final_reply})
            st.session_state.meals_planned += 1
            st.session_state.waste_saved_kg += 0.35
            st.session_state.money_saved_usd += 2.80

# ---------------------------------------------------------
# TAB 2: Smart Leftover Studio
# ---------------------------------------------------------
with tab_studio:
    st.markdown("### 🍳 Zero-Waste Leftover & Pantry Studio")
    st.write("Select or type whatever ingredients are currently sitting in your fridge, crisper drawer, or pantry. NutriBuddy will craft a low-cost, waste-free recipe instantly!")

    col_tag1, col_tag2, col_tag3 = st.columns(3)
    with col_tag1:
        st.markdown("**🍚 Grains & Starches**")
        selected_grains = st.multiselect(
            "Starches",
            ["Cooked White Rice", "Cooked Brown Rice", "Stale Bread / Bagel", "Leftover Pasta", "Boiled Potatoes", "Rolled Oats", "Tortillas / Flatbread"],
            default=["Cooked White Rice"],
            label_visibility="collapsed"
        )
    with col_tag2:
        st.markdown("**🥚 Proteins & Legumes**")
        selected_proteins = st.multiselect(
            "Proteins",
            ["Eggs", "Canned Black Beans", "Canned Chickpeas", "Brown Lentils", "Canned Tuna", "Tofu / Tempeh", "Cottage Cheese / Paneer"],
            default=["Eggs"],
            label_visibility="collapsed"
        )
    with col_tag3:
        st.markdown("**🥬 Vegetables & Aromatics**")
        selected_veggies = st.multiselect(
            "Veggies",
            ["Wilted Spinach / Greens", "Onion & Garlic", "Tomatoes / Tomato Paste", "Carrots / Celery Stems", "Broccoli / Stems", "Bell Pepper", "Cabbage"],
            default=["Wilted Spinach / Greens", "Onion & Garlic"],
            label_visibility="collapsed"
        )

    st.markdown("**Custom Ingredients (Add anything else)**:")
    custom_items_input = st.text_input(
        "Custom items",
        placeholder="e.g. 1/2 can coconut milk, half a lime, leftover roasted chicken, parmesan rind",
        label_visibility="collapsed"
    )

    c_opt1, c_opt2, c_opt3 = st.columns(3)
    with c_opt1:
        cook_time = st.select_slider("Target Cooking Time", options=["10 mins", "15 mins", "20 mins", "30 mins", "45 mins"], value="15 mins")
    with c_opt2:
        cook_equip = st.selectbox("Cooking Method", ["Stovetop / Skillet", "One-Pot Simmer", "Microwave Only", "Sheet Pan / Oven Bake"], index=0)
    with c_opt3:
        servings_count = st.number_input("Servings", min_value=1, max_value=8, value=2)

    gen_studio_btn = st.button("🔥 Generate Zero-Waste Recipe", type="primary", use_container_width=True)

    if gen_studio_btn:
        combined_ingredients = selected_grains + selected_proteins + selected_veggies
        if custom_items_input.strip():
            combined_ingredients.append(custom_items_input.strip())

        ing_joined = ", ".join(combined_ingredients) if combined_ingredients else "Rice, onion, egg, cooking oil"
        
        with st.spinner("Chef NutriBuddy is designing your zero-waste meal..."):
            time.sleep(0.3)
            recipe_result = synthesize_dynamic_recipe(
                ing_joined,
                dietary=dietary_pref,
                budget=budget_level,
                equip=cook_equip,
                time_target=cook_time
            )
            
            st.session_state.meals_planned += servings_count
            st.session_state.waste_saved_kg += round(0.3 * servings_count, 2)
            st.session_state.money_saved_usd += round(3.5 * servings_count, 2)

            st.markdown(f'<div class="recipe-card">{recipe_result}</div>', unsafe_allow_html=True)

            col_send, col_space = st.columns([1, 2])
            with col_send:
                if st.button("💬 Send this Recipe to Chat to Ask Questions", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"I just generated this recipe from leftovers: {ing_joined}. Can you suggest alternative spices or variations?"
                    })
                    st.session_state.prompt_to_submit = "Can you suggest additional seasoning tips or variations for this leftover meal?"
                    st.rerun()

# ---------------------------------------------------------
# TAB 3: 7-Day Budget Meal Planner & Grocery List
# ---------------------------------------------------------
with tab_planner:
    st.markdown("### 📅 7-Day Budget Meal Planner & Smart Grocery List")
    st.write("Generate a balanced, high-protein meal schedule tailored to your budget tier and dietary needs, designed to maximize bulk staples and minimize cost.")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        plan_days = st.radio("Plan Duration", ["1 Day (Quick Snapshot)", "7 Days (Full Week)"], index=1, horizontal=True)
    with col_p2:
        calorie_target_plan = st.select_slider("Daily Energy Target", options=["1,600 kcal", "1,800 kcal", "2,000 kcal", "2,200 kcal", "2,500 kcal"], value="2,000 kcal")
    with col_p3:
        include_snacks = st.checkbox("Include Afternoon Snacks", value=True)

    gen_plan_btn = st.button("📋 Generate Budget Meal Plan & Grocery List", type="primary", use_container_width=True)

    if gen_plan_btn:
        st.session_state.meals_planned += 7 if "7" in plan_days else 3
        st.session_state.waste_saved_kg += 1.2
        st.session_state.money_saved_usd += 24.0

        st.markdown(f"""
        <div class="feature-card">
            <h3 style="color: #34d399; margin-bottom: 0.5rem;">🥗 Plan Summary: {dietary_pref} ({calorie_target_plan}/day)</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Estimated Total Weekly Cost: <strong style="color: #fbbf24;">$24.50 – $32.00</strong> (~$3.50/day per person). Designed in accordance with UN SDG 2.1 & 2.2.
            </p>
        </div>
        """, unsafe_allow_html=True)

        days_data = [
            ("Monday", "Rolled oats porridge with sliced banana & peanut butter ($0.55)", "Lentil & rice bowl with sautéed greens & lemon ($1.10)", "Hearty chickpea & potato curry with flatbread ($1.30)"),
            ("Tuesday", "2 Scrambled or boiled eggs with wholewheat toast ($0.65)", "Leftover chickpea curry with cucumber salad ($0.70)", "Zero-waste vegetable fried rice with peas & garlic ($1.15)"),
            ("Wednesday", "Oatmeal with cinnamon & grated apple ($0.50)", "Black bean & corn wrap with cabbage slaw ($1.20)", "One-pot red lentil dhal with steamed rice & spinach ($1.10)"),
            ("Thursday", "Toast with peanut butter & seasonal fruit ($0.60)", "Leftover red lentil dhal with warm pita ($0.65)", "Tuna or bean pasta skillet with garlic & tomato sauce ($1.40)"),
            ("Friday", "Golden turmeric porridge or boiled egg with toast ($0.65)", "Minestrone soup with pasta, beans, and leftover veggies ($1.15)", "Crispy potato, onion, and egg/tofu hash ($1.25)"),
            ("Saturday", "Banana oat blender pancakes ($0.75)", "Savory panzanella bread salad with tomatoes & greens ($1.05)", "Mediterranean roasted root vegetables with chickpeas ($1.35)"),
            ("Sunday", "Pantry clean-out frittata or tofu scramble ($0.80)", "Lentil & vegetable stew with toasted crusts ($1.10)", "Pantry celebration stir-fry using remaining produce ($1.20)")
        ]

        if "1 Day" in plan_days:
            days_data = [days_data[0]]

        for day_name, b_meal, l_meal, d_meal in days_data:
            with st.expander(f"📌 **{day_name}** — Planned Cost: ~$3.00 to $3.50"):
                st.markdown(f"🍳 **Breakfast**: {b_meal}")
                st.markdown(f"🥗 **Lunch**: {l_meal}")
                st.markdown(f"🍲 **Dinner**: {d_meal}")
                if include_snacks:
                    st.markdown("🍎 **Snack**: Handful of roasted chickpeas or seasonal fruit (~$0.35)")

        # Itemized Grocery List
        st.markdown("---")
        st.markdown("### 🛒 Consolidated Low-Cost Grocery Aisle List")
        c_g1, c_g2, c_g3 = st.columns(3)
        with c_g1:
            st.markdown("**🌾 Grains & Pulses (~$9.50)**")
            st.markdown("- [ ] 1 kg Dried Brown or Red Lentils ($2.20)\n- [ ] 2 kg Long Grain White or Brown Rice ($3.10)\n- [ ] 1 kg Rolled Oats ($1.90)\n- [ ] 1 Loaf 100% Wholewheat Bread ($1.50)\n- [ ] 500g Pasta ($0.80)")
        with c_g2:
            st.markdown("**🥬 Produce & Aromatics (~$11.00)**")
            st.markdown("- [ ] 2 kg Potatoes ($2.40)\n- [ ] 1 kg Yellow Onions & 1 Head Garlic ($2.00)\n- [ ] 1 Bunch Spinach or Kale ($1.50)\n- [ ] 1 Head Cabbage ($1.40)\n- [ ] 1 Bunch Bananas ($1.60)\n- [ ] 1 kg Carrots ($1.20)\n- [ ] 2 Lemons ($0.90)")
        with c_g3:
            st.markdown("**🥫 Pantry & Protein Staples (~$9.00)**")
            st.markdown("- [ ] 1 Dozen Eggs or 2 Blocks Tofu ($2.80)\n- [ ] 2 Cans Chopped Tomatoes ($1.60)\n- [ ] 1 Jar Peanut Butter ($2.20)\n- [ ] Cooking Oil & Basic Salt/Spices ($2.40)")

        # Export Meal Plan
        plan_text_export = f"# NutriBuddy Budget Meal Plan ({dietary_pref})\n\n"
        for day_name, b_meal, l_meal, d_meal in days_data:
            plan_text_export += f"## {day_name}\n- Breakfast: {b_meal}\n- Lunch: {l_meal}\n- Dinner: {d_meal}\n\n"
        st.download_button(
            "📥 Download Meal Plan & Grocery List (.txt)",
            data=plan_text_export,
            file_name="nutribuddy_meal_plan.txt",
            mime="text/plain",
            use_container_width=True
        )

# ---------------------------------------------------------
# TAB 4: Food Shelf-Life & Spoilage Guide
# ---------------------------------------------------------
with tab_storage:
    st.markdown("### 🥫 Interactive Food Shelf-Life & Spoilage Encyclopedia")
    st.write("Food waste is one of the leading contributors to global resource depletion and food insecurity. Search any kitchen staple to learn exact shelf-life, proper storage conditions, and how to revive it.")

    search_query = st.text_input("🔍 Search food item (e.g. spinach, bread, rice, eggs, potato, cheese, banana)", "").lower().strip()

    filtered_items = [
        item for item in SHELF_LIFE_DB
        if not search_query or (search_query in item["food"].lower() or search_query in item["category"].lower())
    ]

    if not filtered_items:
        st.info("No exact match found in quick database. You can ask NutriBuddy in the Chat Assistant tab for any specific food item!")
    else:
        for it in filtered_items:
            with st.expander(f"🥬 **{it['food']}** ({it['category']})", expanded=bool(search_query)):
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.markdown(f"<span class='shelf-tag shelf-pantry'>Pantry</span> {it['pantry']}", unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"<span class='shelf-tag shelf-fridge'>Fridge</span> {it['fridge']}", unsafe_allow_html=True)
                with col_t3:
                    st.markdown(f"<span class='shelf-tag shelf-freezer'>Freezer</span> {it['freezer']}", unsafe_allow_html=True)

                st.markdown(f"**🛡️ Best Storage Method**: {it['storage_tip']}")
                st.markdown(f"**⚠️ Spoilage Warning Signs**: {it['spoilage_signs']}")
                st.markdown(f"**💡 Revive & Rescue Hack**: {it['revive_hack']}")

# ---------------------------------------------------------
# TAB 5: Macro Target & SDG 2 Impact Tracker
# ---------------------------------------------------------
with tab_calc:
    st.markdown("### 📊 Personal Nutrition Target & SDG 2 Impact Tracker")
    st.write("Calculate your daily caloric and macronutrient needs based on scientifically validated nutritional guidelines, and explore accessible low-cost staple foods that fulfill them.")

    c_calc1, c_calc2 = st.columns([1, 1])
    with c_calc1:
        st.markdown("#### 👤 Your Profile Details")
        user_gender = st.radio("Biological Sex", ["Male", "Female"], horizontal=True)
        user_age = st.slider("Age (Years)", 12, 90, 25)
        user_weight = st.slider("Weight (kg)", 35, 150, 65)
        user_height = st.slider("Height (cm)", 130, 210, 172)
        user_activity = st.selectbox(
            "Physical Activity Level",
            ["Sedentary (desk work, minimal exercise)", "Moderate (active daily / exercise 3x week)", "High (heavy labor / athletic training)"]
        )

    with c_calc2:
        # Calculate Mifflin-St Jeor BMR
        if user_gender == "Male":
            bmr = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) + 5
        else:
            bmr = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) - 161

        activity_factor = 1.2 if "Sedentary" in user_activity else (1.55 if "Moderate" in user_activity else 1.8)
        tdee = int(bmr * activity_factor)
        
        # Protein recommendations (g/day)
        protein_g = int(user_weight * (0.85 if "Sedentary" in user_activity else (1.3 if "Moderate" in user_activity else 1.6)))
        fiber_g = 28 if user_gender == "Female" else 36
        iron_mg = 18 if (user_gender == "Female" and user_age <= 50) else 10

        st.markdown("#### 🎯 Your Estimated Daily Nutrient Targets")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Total Daily Energy", f"{tdee} kcal")
            st.metric("Target Protein", f"{protein_g} g / day")
        with col_res2:
            st.metric("Target Fiber", f"{fiber_g} g / day")
            st.metric("Iron Target", f"{iron_mg} mg / day")

    st.markdown("---")
    st.markdown("#### 🥗 Low-Cost Staples to Meet Your Exact Targets")
    st.write(f"To reach **{protein_g}g protein** and **{iron_mg}mg iron** on a student or survival budget:")
    
    c_st1, c_st2, c_st3 = st.columns(3)
    with c_st1:
        st.markdown("""
        **1. Cooked Brown Lentils (1.5 cups)**
        * **Protein**: ~27 g
        * **Iron**: ~9.9 mg (100% daily need!)
        * **Fiber**: 23 g
        * **Cost**: ~$0.75
        """)
    with c_st2:
        st.markdown("""
        **2. Rolled Oats (1 cup dry)**
        * **Protein**: ~11 g
        * **Iron**: ~3.4 mg
        * **Fiber**: 8 g
        * **Cost**: ~$0.40
        """)
    with c_st3:
        st.markdown("""
        **3. Two Large Eggs or 1/2 Block Tofu**
        * **Protein**: ~13 – 16 g
        * **Choline & B12**: Essential brain & nerve nutrients
        * **Cost**: ~$0.50
        """)

# ---------------------------------------------------------
# Footer & SDG 2 Notice
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1rem 0;">
    NutriBuddy is an open educational and community initiative dedicated to <strong>United Nations SDG 2: Zero Hunger</strong>.<br>
    Target 2.1 (Universal Food Access) • Target 2.2 (Ending Malnutrition) • Target 12.3 (Halving Global Food Waste).
</div>
""", unsafe_allow_html=True)
