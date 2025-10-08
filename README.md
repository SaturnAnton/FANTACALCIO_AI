# FANTACALCIO_AI

A data-driven web application for Fantacalcio (Italian fantasy football) players to make smarter decisions using AI predictions.

## 🎯 App Goal

This application helps Fantacalcio players make data-driven decisions by:
- Predicting Serie A player performances
- Recommending optimal formations and lineups
- Suggesting trade opportunities
- All based on real data from FBref and Fantacalcio.it

## 📊 Data Sources

- **FBref**: Advanced football statistics (xG, xA, passes, shots, minutes, etc.)
- **Fantacalcio.it**: Official fantasy ratings, performance scores, and player form

## ⚙️ Main Features

1. **User Authentication & Profiles**
   - JWT/OAuth2 authentication
   - Personalized user profiles

2. **Custom Squad Builder**
   - Create a 25-player squad (3 GK, 8 DEF, 8 MID, 6 FWD)
   - Select from Serie A player database
   - Edit squad anytime

3. **AI Performance Prediction**
   - ML model to predict next-game fantasy ratings
   - Considers form, opponent, team momentum, injuries

4. **Formation & Lineup Optimization**
   - Recommends best formation for each gameweek
   - Suggests optimal starting 11

5. **Smart Trade Suggestions**
   - Identifies underperforming players
   - Suggests alternatives with higher predicted performance

6. **Dashboard & Visualization**
   - Interactive dashboard with squad overview, predictions, lineup recommendations, and trade suggestions
   - Player search, filters, and comparison graphs

## 🧠 AI & Logic Layer

- Combined dataset from FBref and Fantacalcio
- Weekly updated predictive models
- Model candidates: RandomForestRegressor, XGBoost, or PyTorch-based DNN

## 🧩 Tech Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL
- **ML/AI**: scikit-learn or PyTorch
- **Scraping**: BeautifulSoup / Scrapy
- **Auth**: JWT or OAuth2

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL
- Git

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/FANTACALCIO_AI.git
   cd FANTACALCIO_AI
   ```

2. Set up backend
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up frontend
   ```
   cd ../frontend
   npm install
   ```

4. Configure database
   - Create PostgreSQL database
   - Update database connection settings in `backend/config.py`

5. Run the application
   ```
   # Terminal 1 (Backend)
   cd backend
   uvicorn main:app --reload

   # Terminal 2 (Frontend)
   cd frontend
   npm start
   ```

## 📁 Project Structure

```
FANTACALCIO_AI/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Core functionality
│   │   ├── db/              # Database models and connections
│   │   ├── ml/              # Machine learning models
│   │   └── scraping/        # Data scraping modules
│   ├── requirements.txt     # Python dependencies
│   └── main.py              # Application entry point
├── frontend/                # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Application pages
│   │   ├── services/        # API services
│   │   └── utils/           # Utility functions
│   ├── package.json         # Node.js dependencies
│   └── tailwind.config.js   # Tailwind CSS configuration
└── README.md                # Project documentation
```

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/signup | Register a new user |
| POST | /auth/login | Log in and return JWT token |
| GET | /players | Get all Serie A players with stats |
| GET | /player/{id} | Get detailed data for a single player |
| POST | /squad | Save or update user's 25-player squad |
| GET | /squad/{user_id} | Retrieve saved squad |
| GET | /predict/{matchday} | Get predicted performances for next matchday |
| GET | /formation | Get recommended lineup and formation |
| GET | /trade-suggestions | Get suggested trades for underperforming players |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
