from app import Journal
from collections import Counter
import ast
from nltk.probability import FreqDist
import json

def pattern():
     positive = []
     negative = []
     neutral = []
     entries = Journal.query.order_by(Journal.id.desc()).limit(7)
     weekly_average = 0
     ct = 0
     for entry in entries:
          weekly_average+=entry.compound_score
          ct+=1
          if (entry.compound_score>=0.05):
               for i in json.loads(entry.signals):
                    positive.append(i)
          elif (entry.compound_score<=-0.05):
               for i in json.loads(entry.signals):
                    negative.append(i)
          else:
               for i in json.loads(entry.signals):
                    neutral.append(i)
     weekly_average = weekly_average/len(entries) if entries else 0
     f_pos = FreqDist(word.lower() for word in positive)
     f_neg = FreqDist(word.lower() for word in negative)
     f_neu = FreqDist(word.lower() for word in neutral)

     return {
    "meta": {
        "average_sentiment": weekly_average,
        "sample_size": ct
    },
    "patterns": {
        "positive_triggers": f_pos.most_common(5),
        "negative_triggers": f_neg.most_common(5),
        "neutral_themes": f_neu.most_common(5),
        "unique_pos": f_pos.hapaxes()[:5]
    }
}





          
     


               
               
