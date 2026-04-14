from app import Journal
from collections import Counter
import ast

def pattern():
     positive = []
     negative = []
     entries = Journal.query.order_by(Journal.id.desc()).all()
     for entry in entries:
          if (entry.sentiment_score>=0):
               for i in ast.literal_eval(entry.signals):
                    positive.append(i)
          else:
               for i in ast.literal_eval(entry.signals):
                    negative.append(i)
     positive_frequency = Counter(positive)
     negative_frequency = Counter(negative)
     return positive_frequency.most_common(3), negative_frequency.most_common(3)


               
               
