# FANTACALCIO_AI

A data-driven web application for Fantacalcio (Italian fantasy football) players to make smarter decisions using AI predictions.

## 🎯 App Goal

This application helps Fantacalcio players make data-driven decisions by:
- Predicting Serie A player performances
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

## 🧠 AI & Logic Layer

- Combined dataset from FBref and Fantacalcio
- Weekly updated predictive models

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/FANTACALCIO_AI.git
   cd FANTACALCIO_AI
   ```
   
2. Run the application
   ```
   # Terminal 1 (Backend)
   cd backend
   python -m venv venv
   source venv/bin/activate
   uvicorn main:app --reload

   # Terminal 2 (Frontend)
   cd frontend
   npm start
   ```

This project is licensed under the MIT License - see the LICENSE file for details.
