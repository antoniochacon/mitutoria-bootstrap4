from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Date, text, desc, DateTime, Boolean, Time, desc, DECIMAL
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql import func, or_, and_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.sql.functions import ReturnTypeFromArgs
# **************************************
import random
import datetime
# **************************************
from config import Server_Config
engine = create_engine(Server_Config.engine_url, echo=False)
# **************************************
# create a configured Session_SQL class
Session_SQL = sessionmaker(bind=engine)
Base = declarative_base()
# create a Session_SQL
Session_SQL = sessionmaker()
Session_SQL.configure(bind=engine)
session_sql = Session_SQL()


class User (UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    password = Column(String(80))
    email = Column(String(120), unique=True)
    settings = relationship('Settings', uselist=False, back_populates='user', cascade='delete')


class Settings (Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='settings')
    email_validated = Column(Boolean, default=False)
    email_validated_intentos = Column(Integer, default=1)
    email_robinson = Column(Boolean, default=False)
    role = Column(String(80), default='user')
    ban = Column(Boolean, default=False)
    calendar = Column(Boolean, default=False)
    tutoria_timeout = Column(Boolean, default=True)
    show_asignaturas_analisis = Column(Boolean, default=True)
    diferencial = Column(Integer, default=25)
    grupo_activo_id = Column(Integer)
    grupos = relationship('Grupo', backref='settings', lazy='dynamic', cascade='delete')
    preguntas = relationship('Association_Settings_Pregunta', cascade='delete')
    created_at = Column(DateTime, default=datetime.datetime.now())
    edited_at = Column(DateTime, default=datetime.datetime.now())
    visit_last = Column(DateTime, default=datetime.datetime.now())
    visit_number = Column(Integer, default=1)


class Grupo (Base):
    __tablename__ = 'grupo'
    id = Column(Integer, primary_key=True)
    settings_id = Column(Integer, ForeignKey('settings.id'))
    nombre = Column(String(80))
    tutor = Column(String(80))
    curso_academico = Column(Integer)
    centro = Column(String(80))
    alumnos = relationship('Alumno', backref='grupo', lazy='dynamic', cascade='delete')
    asignaturas = relationship('Asignatura', backref='grupo', lazy='dynamic', cascade='delete')
    created_at = Column(DateTime, default=datetime.datetime.now())


class Pregunta (Base):
    __tablename__ = 'pregunta'
    id = Column(Integer, primary_key=True)
    enunciado = Column(String)
    enunciado_ticker = Column(String)  # evita enunciados largo en eje X de los graficos
    orden = Column(Integer)
    visible = Column(Boolean, default=False)  # Controla la visibilidad hacia los usuarios
    active_default = Column(Boolean, default=False)  # controla las preguntas activas por defecto estaran activas para un nuevo usuario. Al crear nuevo usuario, habra que insertar estas preguntas en su preguntas de settings
    respuestas = relationship('Respuesta', backref='pregunta', lazy='dynamic', cascade='delete')
    created_at = Column(DateTime, default=datetime.datetime.now())


class Association_Settings_Pregunta (Base):
    __tablename__ = 'association_settings_pregunta'
    id = Column(Integer, primary_key=True)
    settings_id = Column(Integer, ForeignKey('settings.id'))
    pregunta_id = Column(Integer, ForeignKey('pregunta.id'))
    settings = relationship('Settings', backref=backref('pregunta_association_settings_pregunta', cascade='delete, delete-orphan'))
    pregunta = relationship('Pregunta', backref=backref('settings_association_settings_pregunta', cascade='delete, delete-orphan'))
    edited_at = Column(DateTime, default=datetime.datetime.now())


class Respuesta (Base):
    __tablename__ = 'respuesta'
    id = Column(Integer, primary_key=True)
    informe_id = Column(Integer, ForeignKey('informe.id'))
    pregunta_id = Column(Integer, ForeignKey('pregunta.id'))
    resultado = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())


class Prueba_Evaluable (Base):
    __tablename__ = 'prueba_evaluable'
    id = Column(Integer, primary_key=True)
    informe_id = Column(Integer, ForeignKey('informe.id'))
    nombre = Column(String(80))
    nota = Column(DECIMAL)
    created_at = Column(DateTime, default=datetime.datetime.now())


class Informe (Base):
    __tablename__ = 'informe'
    id = Column(Integer, primary_key=True)
    tutoria_id = Column(Integer, ForeignKey('tutoria.id'))
    asignatura_id = Column(Integer, ForeignKey('asignatura.id'))
    respuestas = relationship('Respuesta', backref='informe', lazy='dynamic', cascade='delete')
    pruebas_evaluables = relationship('Prueba_Evaluable', backref='informe', lazy='dynamic', cascade='delete')
    comentario = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())


class Alumno (Base):
    __tablename__ = 'alumno'
    id = Column(Integer, primary_key=True)
    grupo_id = Column(Integer, ForeignKey('grupo.id'))
    nombre = Column(String(80))
    apellidos = Column(String(80))
    tutorias = relationship('Tutoria', backref='alumno', lazy='dynamic', cascade='delete')
    asignaturas = relationship('Asignatura', secondary='association_alumno_asignatura', lazy='dynamic', passive_deletes=True, single_parent=True)
    created_at = Column(DateTime, default=datetime.datetime.now())


class Asignatura (Base):
    __tablename__ = 'asignatura'
    id = Column(Integer, primary_key=True)
    grupo_id = Column(Integer, ForeignKey('grupo.id'))
    asignatura = Column(String(80))
    nombre = Column(String(80))
    apellidos = Column(String(80))
    email = Column(String(120))
    informes = relationship('Informe', backref='asignatura', lazy='dynamic', cascade='delete')
    created_at = Column(DateTime, default=datetime.datetime.now())


class Association_Alumno_Asignatura (Base):
    __tablename__ = 'association_alumno_asignatura'
    id = Column(Integer, primary_key=True)
    alumno_id = Column(Integer, ForeignKey('alumno.id'))
    asignatura_id = Column(Integer, ForeignKey('asignatura.id'))
    alumno = relationship('Alumno', backref=backref('asignatura_alumno_asignatura', cascade='delete, delete-orphan'))
    asignatura = relationship('Asignatura', backref=backref('alumno_alumno_asignatura', cascade='delete, delete-orphan'))
    created_at = Column(DateTime, default=datetime.datetime.now())


class Tutoria (Base):
    __tablename__ = 'tutoria'
    id = Column(Integer, primary_key=True)
    alumno_id = Column(Integer, ForeignKey('alumno.id'))
    fecha = Column(Date)
    hora = Column(Time)
    activa = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
    informes = relationship('Informe', backref='tutoria', lazy='dynamic', cascade='delete')
    created_at = Column(DateTime, default=datetime.datetime.now())


class Association_Tutoria_Asignatura (Base):
    __tablename__ = 'association_tutoria_asignatura'
    id = Column(Integer, primary_key=True)
    tutoria_id = Column(Integer, ForeignKey('tutoria.id'))
    asignatura_id = Column(Integer, ForeignKey('asignatura.id'))
    asignatura = relationship('Asignatura', backref=backref('tutoria_tutoria_asignatura', cascade='delete, delete-orphan'))
    tutoria = relationship('Tutoria', backref=backref('asignautra_tutoria_asignatura', cascade='delete, delete-orphan'))
    created_at = Column(DateTime, default=datetime.datetime.now())


class Cita (Base):
    __tablename__ = 'cita'
    id = Column(Integer, primary_key=True)
    frase = Column(String)
    autor = Column(String)
    visible = Column(Boolean, default=True)  # Controla la visibilidad hacia los usuarios
    created_at = Column(DateTime, default=datetime.datetime.now())
