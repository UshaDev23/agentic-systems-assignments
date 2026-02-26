class StudentMarks:
    def __init__(self, marks):
        self.marks = marks

    def last_three_avg(self):
        if len(self.marks) < 3:
            raise ValueError("Not enough marks to calculate average")
        else:
            total = sum(self.marks[-3:])
            return total/3    

s1 = StudentMarks([80, 90, 85, 70, 95])
print(f"Average of last 3 marks is: {s1.last_three_avg()}")