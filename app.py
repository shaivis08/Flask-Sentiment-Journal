from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from text_utils import lower_case, remove_punctuations, remove_stopwords, lemmatized_words, correct_spellings, signal_extraction
from datetime import datetime, timedelta
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import json
import nltk
import os
from dotenv import load_dotenv
import google.generativeai as genai
from nltk.probability import FreqDist
nltk.download('vader_lexicon')

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///./test.db'
db=SQLAlchemy(app)
sia = SentimentIntensityAnalyzer()

class Journal(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    userid=db.Column(db.String(50))
    content=db.Column(db.Text,nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    mood_label=db.Column(db.String(15))
    pos_score=db.Column(db.Float)
    neg_score=db.Column(db.Float)
    neu_score=db.Column(db.Float)
    compound_score=db.Column(db.Float)
    signals = db.Column(db.String)
    compound = db.Column(db.String)
    is_processed = db.Column(db.Boolean)

with app.app_context():
    db.create_all()
    if not Journal.query.first():
        sample=Journal(userid="ABC",content='I had a good day yesterday',compound_score=0.4404,mood_label='Happy',pos_score=0.444, neg_score = 0.0, neu_score=0.556)
        db.session.add(sample)
        db.session.commit()

def sentiment(text):
   tokens = sent_tokenize(text)
   if not tokens: return [0], 0, 0, 0, 1
   compound = []
   pos = []
   neg = []
   neu = []
   for i in tokens:
       scores = sia.polarity_scores(i)
       compound.append(scores['compound'])
       pos.append(scores['pos'])
       neg.append(scores['neg'])
       neu.append(scores['neu'])
   compound_score = sum(compound)/len(compound)
   pos_score = sum(pos)/len(pos)
   neg_score = sum(neg)/len(neg)
   neu_score = sum(neu)/len(neu)

   return compound, compound_score, pos_score, neg_score, neu_score
   

def analysis(compound_score, pos_score, neg_score, neu_score):
   if (compound_score>=0.85) and pos_score>0.6:
    mood_label='EUPHORIC'
   elif (compound_score>=0.45 and compound_score<0.85) and pos_score>neg_score*3:
    mood_label='JOYFUL'
   elif (compound_score>=0.15 and compound_score<0.45) and neu_score>0.5:
    mood_label='CONTENT'
   elif (compound_score>=-0.15 and compound_score<0.15) and neu_score>0.8:
    mood_label='NEUTRAL'
   elif (compound_score>=-0.45 and compound_score<-0.15) and neg_score>pos_score:
    mood_label='ANXIOUS'
   elif (compound_score>=-0.85 and compound_score<-0.45) and neg_score>0.4:
    mood_label='SAD'
   elif (compound_score<-0.85) and neg_score>0.7:
    mood_label='FRUSTRATED'
   else:
      mood_label = 'UNCERTAIN'

   return mood_label
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

def get_mood_stats():
    scores = []
    dates = []
    entries = Journal.query.order_by(Journal.date_created.asc()).all()
    for entry in entries:
        scores.append(entry.compound_score)
        dates.append(entry.date_created.strftime("%d %b"))
    chart_data = {
        "labels": dates,
        "sentiment": scores
    }
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday', 'Saturday', 'Sunday']
    mon, tue, wed, thur, fri, sat, sun = [],[],[],[],[],[],[]
    for entry in entries:
       if (entry.date_created.strftime("%A").upper() == "MONDAY" ):
          mon.append(entry.compound_score)
       elif (entry.date_created.strftime("%A").upper() == "TUESDAY" ):
          tue.append(entry.compound_score)
       elif (entry.date_created.strftime("%A").upper() == "WEDNESDAY" ):
          wed.append(entry.compound_score)
       elif (entry.date_created.strftime("%A").upper() == "THURSDAY" ):
          thur.append(entry.compound_score)
       elif (entry.date_created.strftime("%A").upper() == "FRIDAY" ):
          fri.append(entry.compound_score)
       elif (entry.date_created.strftime("%A").upper() == "SATURDAY" ):
          sat.append(entry.compound_score)
       elif (entry.date_created.strftime("%A").upper() == "SUNDAY" ):
          sun.append(entry.compound_score)
    day_scores = [mon, tue, wed, thur, fri, sat, sun]
    #weekly = [sum(i)/len(i) if len(i)!=0 else 0 for i in day_scores]
    weekly = [0.5, -0.2, 0.8, 0, 0.4, -0.1, 0.6]
    patterns = {
                "weekly_scores" : weekly,
                "labels" : days
               }
    return chart_data, patterns
    


@app.route('/')
def index():
    return render_template('cover.html')

@app.route('/contents')
def contents():
    first_entry = Journal.query.order_by(Journal.id.asc()).first()
    first_entry_id= first_entry.id if first_entry else None
    entries = Journal.query.order_by(Journal.id.desc()).all()
    return render_template('table_of_contents.html',first_entry_id=first_entry_id,entries=entries)


@app.route('/index',methods=['GET'])
def view():
     entries=Journal.query.order_by(Journal.date_created.desc()).all()
     return render_template('index.html',entries=entries)

@app.route('/create',methods=['GET'])
def create():
    entries = Journal.query.order_by(Journal.date_created.desc()).all()
    return render_template('index.html',new_entry_mode=True,entries=entries)
    
@app.route('/add',methods=['POST'])
def add():
    journal_entry=request.form['content']
    compound, compound_score, pos_score, neg_score, neu_score = sentiment(journal_entry)
    label = analysis(compound_score, pos_score, neg_score, neu_score)
    modified_1 = lower_case(journal_entry)
    modified_2 = remove_punctuations(modified_1)
    modified_3 = remove_stopwords(modified_2)
    modified_4 = correct_spellings(modified_3)
    modified_5 = lemmatized_words(modified_4)
    signal = signal_extraction(modified_5)
    new=Journal(content=journal_entry,compound_score=compound_score,pos_score=pos_score,neu_score=neu_score,neg_score=neg_score,compound=json.dumps(compound),mood_label=label, signals = json.dumps(signal))

    try:
        db.session.add(new)
        db.session.commit()
        newid=new.id
        return redirect(url_for('entry',id=newid))
    except:
        return 'Your journal entry could not be added'

    
@app.route('/entry/<int:id>')
def entry(id):
    entry_to_analyse = Journal.query.get_or_404(id)
    raw_compound = entry_to_analyse.compound

    if raw_compound and raw_compound != "[]":
     scores = json.loads(raw_compound)
     mean = entry_to_analyse.compound_score
     if (max(scores) - mean > mean - min(scores)):
        pivot = scores.index(max(scores))
     else:
        pivot = scores.index(min(scores))
    else:
     scores = [0, 0] 
     pivot = 0
     mean = entry_to_analyse.compound_score

    previous_entry = Journal.query.filter(Journal.id > id).order_by(Journal.id.asc()).first()
    next_entry = Journal.query.filter(Journal.id < id).order_by(Journal.id.desc()).first()

    previous_id = previous_entry.id if previous_entry else None
    next_id = next_entry.id if next_entry else None
    print(f"DEBUG: First score: {scores[0]}, Last score: {scores[-1]}")
    return render_template(
        'entry_detail.html',
        entry_to_analyse=entry_to_analyse,
        previous_id=previous_id,
        next_id=next_id,
        arc_data=scores,      
        pivotIndex=pivot      
    )

@app.route('/delete/<int:id>')
def delete(id):
    entry_to_delete=Journal.query.get_or_404(id)

    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Entry could not be deleted'
    
@app.route('/update/<int:id>',methods=['POST','GET'])
def update(id):
    entry_to_update=Journal.query.get_or_404(id)
    if request.method=='POST':
        entry_to_update.content=request.form['content']
    
        try:
         db.session.commit()
         return redirect('/contents')
    
        except:
         return 'Entry could not be updated'
    
    else:
        return render_template('update.html',entry_to_update=entry_to_update)
    

@app.route('/mood_chart',methods=['POST','GET'])
def weekly_chart():
    chart_data, patterns = get_mood_stats()
    
    return render_template('dashboard.html', data=chart_data, pattern_chart = patterns)

@app.route('/daily_insight/<int:id>',methods=['POST','GET'])
def daily_insights(id):
   entry_for_insight = Journal.query.get_or_404(id)
   compound = json.loads(entry_for_insight.compound)
   if not compound:
       return render_template('daily_insight.html', insight="Your metamorphosis is just beginning. Write today's entry and get insights!")
   data_snapshot = json.dumps({
    "sentence_scores": compound,
    "entry_text": entry_for_insight.content, # Optional: helps AI see the 'why'
    "overall_sentiment": entry_for_insight.compound_score 
}, indent=2)

   prompt = f"""
SYSTEM ROLE:
You are the "Metamorphosis Mentor." Your task is to provide a brief, soulful reflection 
on the user's single journal entry for today. You focus on the "micro-rhythms" of their 
thoughts and offer a single "seed of growth."

DATA CONTEXT:
1. 'sentence_scores': This is a chronological list of scores for every sentence in the entry. 
   - A sequence like [0.5, -0.1, 0.8] shows a "recovery" arc.
   - A sequence like [0.8, 0.2, -0.5] shows a "downward" emotional shift.

TODAY'S DATA:
{data_snapshot}

INSTRUCTIONS:
- OBSERVE THE ARC: Identify the emotional flow of the day. Did they start heavy and end light, or vice-versa? 
- CHOOSE A MOMENT: Reference a specific feeling or shift indicated by the sentence scores.
- THE GROWTH SEED: Suggest one tiny, actionable reflection or task for tomorrow that aligns with today's vibe.
- TONE: Encouraging, short, and "Boho-Academia." Use imagery like "ink," "roots," "stars," or "light."

OUTPUT FORMAT:
Provide exactly 3 to 4 sentences. It should feel like a quick note left on a desk.
"""
   try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    daily_reflection = response.text
   except Exception as e:
    daily_reflection = "Today's ink is still drying. Take a breath and reflect on your own progress for a moment."

   return render_template('daily_insight.html', insight=daily_reflection)
   
      

@app.route('/weekly_insight',methods=['POST','GET'])
def weekly_insights():
   model = genai.GenerativeModel('gemini-1.5-flash')
   stats = pattern()
   chart_data, patterns = get_mood_stats()
   if not stats or len(stats.get('top_triggers', [])) == 0:
        return render_template('weekly_insight.html', insight="Your metamorphosis is just beginning. Write a few more entries to unlock weekly patterns!")
   
   full_context = {
    "chronological_trend": chart_data,  # Dates and scores in order
    "day_of_week_averages": patterns,    # Monday-Sunday averages
    "linguistic_patterns": stats  #  triggers and hapaxes
}
   data_snapshot = json.dumps(full_context, indent=2)

   prompt = f"""
SYSTEM ROLE:
You are the "Metamorphosis Mentor," a deeply observant and intellectually curious companion 
for a user documenting their life in a digital journal. You don't just see numbers; you see 
an evolving story of a developer and creative mind.

DATA SCHEMA & CONTEXT:
1. 'chronological_trend': A timeline of the user's mood. Look for sharp dips or peaks across specific dates.
2. 'day_of_week_averages': The user's typical emotional baseline for each day (e.g., are Mondays consistently lower?).
3. 'positive/negative_triggers': The top keywords associated with emotional shifts.
4. 'unique_pos' (Hapaxes): Rare "seeds of growth" mentioned only once this week—high-value breakthroughs.

THE WEEKLY DATA SNAPSHOT:
{data_snapshot}

INSTRUCTIONS FOR THE ANALYSIS:
- SYNTHESIS: Compare a specific date from 'chronological_trend' with the 'negative_triggers.' If a dip happened, explain it through the words the user used.
- DAY PATTERNS: Mention if their current week is breaking or following their typical 'day_of_week_averages' (e.g., "Surprisingly, your Tuesday was vibrant despite it usually being a heavier day for you").
- MILESTONE: Select ONE word from 'unique_pos' and celebrate it as a sign of their metamorphosis.
- TONE: Warmly observant, "Boho-Academia" vibes—think of a mentor in a library filled with plants and codebooks. 
- AVOID: Generic "AI slop" or corporate buzzwords.

OUTPUT FORMAT:
Provide a single, cohesive paragraph of 6 to 8 sentences. The reflection should feel like a short, personal letter.
"""

   try:
        response = model.generate_content(prompt)
        return render_template('weekly_insight.html', insight=response.text)
   except Exception as e:
        return render_template('weekly_insight.html', insight="The AI is resting right now. Try again in a moment!")


if __name__ == '__main__':
    app.run(debug=True)



    
