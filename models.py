from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)  # ID du médecin
    appointment_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    is_cancelled = db.Column(db.Boolean, default=False)  # En cas d'annulation dun rendez-vous

    def __repr__(self):
        return f'<Appointment {self.id} - {self.patient_name} with {self.doctor_name}>'
