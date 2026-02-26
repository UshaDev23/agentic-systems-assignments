class StudentPerformance:
    def __init__(self, scores):
        self.scores = scores

    def score_difference(self):
        if len(self.scores) < 1:
            raise ValueError("No scores available to calculate difference")
        else:
            return self.scores[-1] - self.scores[0]

s1 = StudentPerformance([80, 90, 85, 70, 95])
print(f"Difference between last and first score is: {s1.score_difference()}")