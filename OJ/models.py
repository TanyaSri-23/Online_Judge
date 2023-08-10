from distutils.command.build_scripts import first_line_re
import imp
from django.db import models
# from froala_editor.fields import FroalaField

class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name
    
    
class Problem(models.Model):
    DIFFICULTY=(("Easy", "Easy"), ("Medium", "Medium"), ("Tough", "Tough"))
    STATUS=(("Unsolved", "Unsolved"), ("Solved", "Solved"))
    name = models.CharField(max_length=100, default="")
    description = models.CharField(max_length = 150000, default="")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY)
    time_limit = models.IntegerField(default=2, help_text="in seconds")
    memory_limit = models.IntegerField(default=128, help_text="in kb")
    problem_id = models.CharField(max_length=50)
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE)


    def __str__(self):
        return self.name
    
class Testcase(models.Model):
    problem=models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()

    def __str__(self):
        return ("TC: " + str(self.id) + " for Problem: " + str(self.problem))
    

