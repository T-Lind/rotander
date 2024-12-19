import json
import os

class HighScoreManager:
    def __init__(self, filename='data/high_scores.json'):
        self.filename = filename
        self.high_scores = self._load_high_scores()

    def _load_high_scores(self):
        if not os.path.exists(self.filename):
            return {}
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save_high_scores(self):
        with open(self.filename, 'w') as f:
            json.dump(self.high_scores, f)

    def add_score(self, username, score):
        if username in self.high_scores:
            if score > self.high_scores[username]:
                self.high_scores[username] = score
        else:
            self.high_scores[username] = score
        self.save_high_scores()

    def get_top_scores(self, top_n=10):
        return sorted(self.high_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]