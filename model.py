from .__init__ import db

class Index(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    refer_id = db.Column(db.String(100))
    frequency =  db.Column(db.String(30))
    ref_data = db.relationship('Data',backref='index',lazy='dynamic')

    def __init__(self,frequency,refer_id):

        self.frequency = frequency
        self.refer_id = refer_id

class Data(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    refer_foreign_id = db.Column(db.String(100))
    date =  db.Column(db.String(30))
    data =  db.Column(db.Float)
    index_id = db.Column(db.Integer,db.ForeignKey('index.id'))

    def __init__(self,date,data,index_id,refer_foreign_id):

        self.date = date
        self.data = data
        self.refer_foreign_id = refer_foreign_id
        self.index_id = index_id

db.create_all()
