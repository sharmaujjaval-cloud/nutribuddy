# 🥗 NutriBuddy — UN SDG 2 Zero Hunger Assistant

NutriBuddy is an intelligent, highly accessible AI-powered assistant engineered to advance **United Nations Sustainable Development Goal 2: Zero Hunger**.

It empowers students, families, community workers, and food rescue volunteers with:
- 🍲 **Zero-Waste Leftover Recipes**: Instantly turn whatever random ingredients are in your fridge into nutritious meals.
- 💰 **Budget Nutrition Planning**: High-protein, balanced meal plans under $2 to $5 a day with itemized aisle grocery lists.
- 🥫 **Food Shelf-Life & Waste Prevention**: Comprehensive encyclopedia with room-temp, fridge, and freezer storage guides + food revival hacks.
- 🛡️ **Micronutrient Defense**: Practical guides on preventing anemia and hidden hunger using affordable plant-based sources of iron, zinc, vitamin A, and folate.
- 🧪 **Smart Dual-Engine**: Real-time token streaming via OpenRouter AI (`openrouter/free`) alongside an instant, dynamic **Offline Recipe & Knowledge Synthesis Engine** (works 100% out of the box even without an API key or internet).

---

## 🌟 Comprehensive Features (5 Interactive Modules)

### 1. 💬 NutriBuddy Chat Assistant
- Interactive conversational AI with streaming responses.
- Dynamic fallback to built-in SDG 2 knowledge engine if offline or if API key has quota/permissions constraints.
- 1-click Quick Starter Prompts for immediate high-value queries.
- Export entire chat session as a formatted Markdown (`.md`) file.

### 2. 🍳 Smart Leftover & Pantry Studio
- Multi-select visual ingredient tags for Starches, Proteins, and Veggies + custom freeform ingredients.
- Equipment filters (Stovetop, One-Pot, Microwave Only, Oven Bake) and target cook times (10 to 45 mins).
- Instant recipe cards complete with step-by-step instructions, cost per serving, and zero-waste kitchen secrets.
- 1-click "Send to Chat" to ask follow-up questions or customization tips.

### 3. 📅 7-Day Budget Meal Planner & Smart Grocery List
- Generates 1-Day or full 7-Day balanced schedules tailored to your dietary preference and budget tier.
- Computes estimated daily and weekly meal costs (~$25 - $32/week).
- Generates an itemized shopping list categorized by grocery aisle (Grains, Produce, Proteins/Pantry).
- Export meal schedule as a downloadable text plan.

### 4. 🥫 Food Shelf-Life & Spoilage Encyclopedia
- Searchable database of 30+ everyday food items with pantry, fridge, and freezer storage timeframes.
- Storage tips to prevent spoilage (e.g. ethylene gas separation, foil wrapping).
- Spoilage indicators (sight and smell checks) and food revival hacks (ice baths for limp celery/carrots, restoring stale bread).

### 5. 📊 Personal Macro Target & SDG 2 Impact Tracker
- Scientifically validated Mifflin-St Jeor BMR and TDEE calorie calculator.
- Daily protein, fiber, and iron targets customized by age, biological sex, weight, height, and activity level.
- Exact low-cost staple recommendations to reach daily macro targets on a budget.
- Live session SDG 2 counters: Meals planned, Food waste avoided (kg), and Dollars saved ($).

---

## 🚀 Quickstart

### 1. Launch with One Click (Windows)
Double-click `run_app.bat` or execute in PowerShell:
```powershell
.\run_app.bat
```
The script will automatically detect port availability (checks port 8501, and if occupied, uses port 8502) and start the server.

Open your browser to:
```
http://localhost:8502
```
*(or http://localhost:8501 if port 8501 is free)*

Or open `index.html`, which automatically pings the server and redirects you directly to the active port!

---

## 🔑 OpenRouter AI Setup (Optional)

NutriBuddy works out-of-the-box in **Offline Demo Mode**. To enable live OpenRouter AI streaming responses:

1. Obtain your API key from [OpenRouter](https://openrouter.ai/keys).
2. Paste it into `.env`:
   ```env
   OPENROUTER_API_KEY=your_actual_key_here
   ```
3. Or paste it directly into the **OpenRouter API Key** field in the NutriBuddy sidebar.
4. Click **🧪 Test API** in the sidebar to verify your connection.

---

## 📂 Project Structure

```
nutriassist-bot/
├── app.py              # Main Streamlit application & dual AI/dynamic offline engine
├── index.html          # Portal landing page with automatic port detection
├── requirements.txt    # Python dependencies (streamlit, requests, python-dotenv)
├── run_app.bat         # 1-click Windows startup script with auto-port detection
├── .env                # Environment configuration (OPENROUTER_API_KEY)
└── README.md           # Documentation and SDG 2 overview
```

---

## 🌍 UN SDG 2 Alignment
- **Target 2.1**: Universal access to safe, nutritious, and sufficient food.
- **Target 2.2**: Ending all forms of malnutrition (protein & micronutrient education).
- **Target 12.3**: Halving per-capita global food waste at consumer and retail levels.
