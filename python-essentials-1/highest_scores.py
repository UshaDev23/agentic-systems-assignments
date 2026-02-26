class StudentScores:
    def __init__(self, scores):
        self.scores = scores

    def highest_last_two(self):
        if len(self.scores) < 2:
            raise ValueError("Not enough scores to find highest value")
        else:
            return max(self.scores[-2:])

s1 = StudentScores([80, 90, 85, 70, 95])
print(f"Highest score among last two is: {s1.highest_last_two()}")