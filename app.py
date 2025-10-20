
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from textblob import TextBlob 

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///./test.db'
db=SQLAlchemy(app)

class Journal(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    userid=db.Column(db.String(50))
    content=db.Column(db.Text,nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    sentiment_score=db.Column(db.Float,nullable=False)
    mood_label=db.Column(db.String(15),nullable=False)
    subjectivity_score=db.Column(db.Float,nullable=False)

with app.app_context():
    db.create_all()
    if not Journal.query.first():
        sample=Journal(userid="ABC",content='I had a good day yesterday',sentiment_score=0.8,mood_label='Happy',subjectivity_score=0.9)
        db.session.add(sample)
        db.session.commit()


def analysis(text):
    blob=TextBlob(text)
    
    sentiment_score=blob.sentiment.polarity
    subjectivity_score=blob.sentiment.subjectivity
    
    if sentiment_score>=0.81:
        mood_label='EUPHORIC'
    elif sentiment_score>=0.51:
        mood_label='JOYFUL'
    elif sentiment_score>=0.21:
        mood_label='CONTENT'
    elif sentiment_score>=-0.20:
        mood_label='NEUTRAL'
    elif sentiment_score>=-0.50:
        mood_label='ANXIOUS'
    elif sentiment_score>=-0.80:
        mood_label='SAD'
    else:
        mood_label='FRUSTRATED'
    
    return sentiment_score,mood_label,subjectivity_score

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
    score,label,subjectivity=analysis(journal_entry)
    new=Journal(content=journal_entry,sentiment_score=score,mood_label=label,subjectivity_score=subjectivity)

    try:
        db.session.add(new)
        db.session.commit()
        newid=new.id
        return redirect(url_for('entry',id=newid))
    except:
        return 'Your journal entry could not be added'

    
@app.route('/entry/<int:id>')
def entry(id):
    entry_to_analyse=Journal.query.get_or_404(id)

    previous_entry=Journal.query.filter(Journal.id>id).order_by(Journal.id.asc()).first()
    next_entry=Journal.query.filter(Journal.id<id).order_by(Journal.id.desc()).first()

    previous_id=previous_entry.id if previous_entry else None
    next_id=next_entry.id if next_entry else None

    return render_template('entry_detail.html',entry_to_analyse=entry_to_analyse,previous_id=previous_id,next_id=next_id)
    


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
    


    


if __name__ == '__main__':
    app.run(debug=True)



    
