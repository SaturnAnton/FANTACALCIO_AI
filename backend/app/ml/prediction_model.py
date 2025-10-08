import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib
import logging
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..db.models import Player, Prediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FantacalcioPredictionModel:
    """
    ML model for predicting Fantacalcio player performance
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.preprocessor = None
        self.model_path = model_path or "model/fantacalcio_model.joblib"
        
        # Create model directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Try to load existing model
        if os.path.exists(self.model_path):
            self._load_model()
    
    def _load_model(self):
        """Load model from file"""
        try:
            pipeline = joblib.load(self.model_path)
            self.preprocessor = pipeline["preprocessor"]
            self.model = pipeline["model"]
            logger.info(f"Loaded model from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def _save_model(self):
        """Save model to file"""
        try:
            pipeline = {
                "preprocessor": self.preprocessor,
                "model": self.model
            }
            joblib.dump(pipeline, self.model_path)
            logger.info(f"Saved model to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def _prepare_data(self, players: List[Dict[str, Any]]):
        """Prepare player data for training or prediction"""
        # Convert to DataFrame
        df = pd.DataFrame(players)
        
        # Extract features from nested dictionaries
        self._extract_features(df)
        
        # Define feature columns
        numerical_features = [
            'minutes', 'goals', 'assists', 'shots', 'shots_on_target', 
            'passes_completed', 'key_passes', 'tackles', 'interceptions',
            'average_rating', 'form', 'age'
        ]
        
        categorical_features = [
            'team', 'role', 'opponent', 'home_away'
        ]
        
        # Filter to only include columns that exist in the DataFrame
        numerical_features = [col for col in numerical_features if col in df.columns]
        categorical_features = [col for col in categorical_features if col in df.columns]
        
        # Fill missing values
        for col in numerical_features:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0)
        
        for col in categorical_features:
            df[col] = df[col].fillna('Unknown')
        
        # Create preprocessor if it doesn't exist
        if self.preprocessor is None:
            numerical_transformer = StandardScaler()
            categorical_transformer = OneHotEncoder(handle_unknown='ignore')
            
            self.preprocessor = ColumnTransformer(
                transformers=[
                    ('num', numerical_transformer, numerical_features),
                    ('cat', categorical_transformer, categorical_features)
                ],
                remainder='drop'
            )
        
        return df, numerical_features, categorical_features
    
    def _extract_features(self, df: pd.DataFrame):
        """Extract features from nested dictionaries in player data"""
        # Extract stats features
        if 'stats' in df.columns:
            for player_idx, player_stats in df['stats'].items():
                if not isinstance(player_stats, dict):
                    continue
                
                # Extract basic stats
                for stat, value in player_stats.items():
                    if stat not in df.columns:
                        df[stat] = None
                    
                    try:
                        df.at[player_idx, stat] = value
                    except:
                        pass
                
                # Extract nested stats
                for category in ['shooting', 'passing', 'defense']:
                    if category in player_stats and isinstance(player_stats[category], dict):
                        for stat, value in player_stats[category].items():
                            col_name = f"{category}_{stat}"
                            if col_name not in df.columns:
                                df[col_name] = None
                            
                            try:
                                df.at[player_idx, col_name] = value
                            except:
                                pass
        
        # Extract Fantacalcio data features
        if 'fantacalcio_data' in df.columns:
            for player_idx, fanta_data in df['fantacalcio_data'].items():
                if not isinstance(fanta_data, dict):
                    continue
                
                # Extract basic Fantacalcio stats
                for stat, value in fanta_data.items():
                    if stat not in df.columns and stat != 'last_games' and stat != 'season_stats':
                        df[stat] = None
                    
                    try:
                        if stat != 'last_games' and stat != 'season_stats':
                            df.at[player_idx, stat] = value
                    except:
                        pass
                
                # Extract form from last games
                if 'last_games' in fanta_data and isinstance(fanta_data['last_games'], list):
                    # Calculate form as average of last ratings
                    ratings = []
                    for game in fanta_data['last_games']:
                        if isinstance(game, dict) and 'rating' in game:
                            try:
                                rating = float(game['rating'])
                                ratings.append(rating)
                            except:
                                pass
                    
                    if ratings:
                        df.at[player_idx, 'form'] = sum(ratings) / len(ratings)
                    else:
                        df.at[player_idx, 'form'] = 0
                
                # Extract season stats
                if 'season_stats' in fanta_data and isinstance(fanta_data['season_stats'], dict):
                    for stat, value in fanta_data['season_stats'].items():
                        col_name = f"season_{stat}"
                        if col_name not in df.columns:
                            df[col_name] = None
                        
                        try:
                            df.at[player_idx, col_name] = value
                        except:
                            pass
    
    def train(self, players: List[Dict[str, Any]], target_column: str = 'average_rating'):
        """Train the prediction model"""
        logger.info(f"Training model with {len(players)} players")
        
        # Prepare data
        df, numerical_features, categorical_features = self._prepare_data(players)
        
        # Check if target column exists
        if target_column not in df.columns:
            logger.error(f"Target column '{target_column}' not found in data")
            return False
        
        # Split features and target
        X = df.drop(columns=[target_column, 'name', 'stats', 'fantacalcio_data'])
        y = df[target_column]
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Fit preprocessor
        X_train_processed = self.preprocessor.fit_transform(X_train)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_processed, y_train)
        
        # Evaluate model
        X_test_processed = self.preprocessor.transform(X_test)
        score = self.model.score(X_test_processed, y_test)
        logger.info(f"Model R² score: {score:.4f}")
        
        # Save model
        self._save_model()
        
        return score
    
    def predict(self, players: List[Dict[str, Any]]):
        """Predict player performance"""
        if self.model is None or self.preprocessor is None:
            logger.error("Model not trained or loaded")
            return None
        
        # Prepare data
        df, _, _ = self._prepare_data(players)
        
        # Drop unnecessary columns
        X = df.drop(columns=['name', 'stats', 'fantacalcio_data'], errors='ignore')
        
        # Transform features
        X_processed = self.preprocessor.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_processed)
        
        # Calculate confidence (using prediction variance from trees)
        prediction_std = np.std([tree.predict(X_processed) for tree in self.model.estimators_], axis=0)
        confidence = 1 / (1 + prediction_std)  # Transform to 0-1 scale
        
        # Add predictions to player data
        result = []
        for i, player in enumerate(players):
            result.append({
                **player,
                'predicted_score': float(predictions[i]),
                'confidence': float(confidence[i])
            })
        
        return result
    
    def update_predictions(self, db: Session, matchday: int):
        """Update predictions for all players in the database"""
        try:
            # Get all players from database
            players = db.query(Player).all()
            
            # Convert to list of dictionaries
            player_dicts = []
            for player in players:
                player_dict = {
                    'name': player.name,
                    'team': player.team,
                    'role': player.role,
                    'price': player.price,
                    'stats': player.stats,
                    'fantacalcio_data': player.fantacalcio_data
                }
                player_dicts.append(player_dict)
            
            # Make predictions
            predictions = self.predict(player_dicts)
            
            if not predictions:
                logger.error("Failed to generate predictions")
                return False
            
            # Save predictions to database
            for pred in predictions:
                player = db.query(Player).filter(
                    Player.name == pred['name'],
                    Player.team == pred['team']
                ).first()
                
                if player:
                    # Check if prediction already exists
                    existing_pred = db.query(Prediction).filter(
                        Prediction.player_id == player.id,
                        Prediction.matchday == matchday
                    ).first()
                    
                    if existing_pred:
                        # Update existing prediction
                        existing_pred.predicted_score = pred['predicted_score']
                        existing_pred.confidence = pred['confidence']
                    else:
                        # Create new prediction
                        new_pred = Prediction(
                            player_id=player.id,
                            matchday=matchday,
                            predicted_score=pred['predicted_score'],
                            confidence=pred['confidence']
                        )
                        db.add(new_pred)
            
            db.commit()
            logger.info(f"Updated predictions for matchday {matchday}")
            return True
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating predictions: {str(e)}")
            return False