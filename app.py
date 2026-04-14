from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from text_utils import lower_case, remove_punctuations, remove_stopwords, lemmatized_words, correct_spellings, signal_extraction
from datetime import datetime, timedelta
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import json
import nltk
nltk.download('vader_lexicon')

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
    scores = []
    dates = []
    entries = Journal.query.order_by(Journal.date_created.asc()).limit(7).all()
    for entry in entries:
        scores.append(entry.compound_score)
        dates.append(entry.date_created.strftime("%d %b"))
    chart_data = {
        "labels": dates,
        "sentiment": scores
    }
    return render_template('dashboard.html', data=chart_data)
def day_chart():
    scores = []
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday', 'Saturday', 'Sunday']




    


    


if __name__ == '__main__':
    app.run(debug=True)



    
