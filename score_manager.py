import json
import os
from datetime import datetime
from typing import List, Dict

class ScoreManager:
    def __init__(self):
        self.scores_file = "high_scores.json"
        self.current_run = {
            "username": "",
            "total_score": 0,
            "levels_completed": []
        }
        self.high_scores = self._load_scores()
    
    def _load_scores(self) -> List[Dict]:
        if not os.path.exists(self.scores_file):
            return []
        try:
            with open(self.scores_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_run(self):
        if not self.current_run["username"]:
            return
            
        score_entry = {
            "username": self.current_run["username"],
            "score": self.current_run["total_score"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "levels_completed": self.current_run["levels_completed"]
        }
        
        self.high_scores.append(score_entry)
        self.high_scores.sort(key=lambda x: x["score"], reverse=True)
        self.high_scores = self.high_scores[:10]  # Keep top 10
        
        with open(self.scores_file, 'w') as f:
            json.dump(self.high_scores, f)
            
    def add_level_score(self, level: int, score: int):
        self.current_run["total_score"] += score
        self.current_run["levels_completed"].append(level)
        
    def reset_run(self):
        self.current_run["total_score"] = 0
        self.current_run["levels_completed"] = []
        
    def set_username(self, username: str):
        self.current_run["username"] = username