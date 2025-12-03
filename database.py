import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TestHistory(Base):
    __tablename__ = "test_history"
    
    id = Column(Integer, primary_key=True, index=True)
    main_topic = Column(String(100))
    subtopic = Column(String(255))
    test_type = Column(String(100))
    level = Column(String(10))
    score = Column(Float)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class FavoriteSubtopic(Base):
    __tablename__ = "favorite_subtopics"
    
    id = Column(Integer, primary_key=True, index=True)
    main_topic = Column(String(100))
    subtopic = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class SeenSubtopic(Base):
    __tablename__ = "seen_subtopics"
    
    id = Column(Integer, primary_key=True, index=True)
    main_topic = Column(String(100))
    subtopic = Column(String(255))
    times_seen = Column(Integer, default=1)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def save_test_result(main_topic, subtopic, test_type, level, score, total_questions, correct_answers):
    db = SessionLocal()
    try:
        history = TestHistory(
            main_topic=main_topic,
            subtopic=subtopic,
            test_type=test_type,
            level=level,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers
        )
        db.add(history)
        db.commit()
    finally:
        db.close()

def mark_subtopic_seen(main_topic, subtopic):
    db = SessionLocal()
    try:
        existing = db.query(SeenSubtopic).filter(
            SeenSubtopic.main_topic == main_topic,
            SeenSubtopic.subtopic == subtopic
        ).first()
        
        if existing:
            existing.times_seen += 1
            existing.last_seen_at = datetime.utcnow()
        else:
            seen = SeenSubtopic(main_topic=main_topic, subtopic=subtopic)
            db.add(seen)
        
        db.commit()
    finally:
        db.close()

def get_seen_subtopics(main_topic=None):
    db = SessionLocal()
    try:
        if main_topic:
            return db.query(SeenSubtopic).filter(SeenSubtopic.main_topic == main_topic).all()
        return db.query(SeenSubtopic).all()
    finally:
        db.close()

def get_unseen_subtopics(main_topic, all_subtopics):
    db = SessionLocal()
    try:
        seen = db.query(SeenSubtopic.subtopic).filter(
            SeenSubtopic.main_topic == main_topic
        ).all()
        seen_set = {s[0] for s in seen}
        return [st for st in all_subtopics if st not in seen_set]
    finally:
        db.close()

def add_favorite(main_topic, subtopic):
    db = SessionLocal()
    try:
        existing = db.query(FavoriteSubtopic).filter(
            FavoriteSubtopic.main_topic == main_topic,
            FavoriteSubtopic.subtopic == subtopic
        ).first()
        
        if not existing:
            fav = FavoriteSubtopic(main_topic=main_topic, subtopic=subtopic)
            db.add(fav)
            db.commit()
            return True
        return False
    finally:
        db.close()

def remove_favorite(main_topic, subtopic):
    db = SessionLocal()
    try:
        db.query(FavoriteSubtopic).filter(
            FavoriteSubtopic.main_topic == main_topic,
            FavoriteSubtopic.subtopic == subtopic
        ).delete()
        db.commit()
    finally:
        db.close()

def get_favorites(main_topic=None):
    db = SessionLocal()
    try:
        if main_topic:
            return db.query(FavoriteSubtopic).filter(FavoriteSubtopic.main_topic == main_topic).all()
        return db.query(FavoriteSubtopic).all()
    finally:
        db.close()

def is_favorite(main_topic, subtopic):
    db = SessionLocal()
    try:
        return db.query(FavoriteSubtopic).filter(
            FavoriteSubtopic.main_topic == main_topic,
            FavoriteSubtopic.subtopic == subtopic
        ).first() is not None
    finally:
        db.close()

def get_test_history(limit=50):
    db = SessionLocal()
    try:
        return db.query(TestHistory).order_by(TestHistory.created_at.desc()).limit(limit).all()
    finally:
        db.close()

def get_topic_stats():
    db = SessionLocal()
    try:
        from sqlalchemy import func
        stats = db.query(
            TestHistory.main_topic,
            func.count(TestHistory.id).label('test_count'),
            func.avg(TestHistory.score).label('avg_score')
        ).group_by(TestHistory.main_topic).all()
        return stats
    finally:
        db.close()

def get_weak_topics(threshold=60):
    db = SessionLocal()
    try:
        from sqlalchemy import func
        stats = db.query(
            TestHistory.main_topic,
            func.avg(TestHistory.score).label('avg_score'),
            func.count(TestHistory.id).label('test_count')
        ).group_by(TestHistory.main_topic).having(func.avg(TestHistory.score) < threshold).all()
        return stats
    finally:
        db.close()

def clear_seen_subtopics(main_topic=None):
    db = SessionLocal()
    try:
        if main_topic:
            db.query(SeenSubtopic).filter(SeenSubtopic.main_topic == main_topic).delete()
        else:
            db.query(SeenSubtopic).delete()
        db.commit()
    finally:
        db.close()
