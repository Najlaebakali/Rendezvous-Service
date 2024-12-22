from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)  # ID du médecin
    appointment_date = db.Column(db.Date, nullable=False)  # Date uniquement
    appointment_time = db.Column(db.Time, nullable=False)  # Heure exacte
    notes = db.Column(db.Text, nullable=True)
    is_cancelled = db.Column(db.Boolean, default=False)  # En cas d'annulation dun rendez-vous

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'appointment_date', name='unique_doctor_appointment'),
    )

    def __repr__(self):
        return f'<Appointment {self.id} - Doctor {self.doctor_id} - Patient {self.patient_id}>'