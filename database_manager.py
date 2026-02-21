
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'tsmart_licenses.db')}"

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    licenses = relationship('License', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(email='{self.email}', is_active={self.is_active})>"

class License(Base):
    __tablename__ = 'licenses'

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    hwid = Column(String, nullable=True) # Hardware ID, initially None
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    is_used = Column(Boolean, default=False)

    user = relationship('User', back_populates='licenses')

    def __repr__(self):
        return f"<License(key='{self.key}', user_email='{self.user.email if self.user else 'N/A'}', hwid='{self.hwid}', expires_at='{self.expires_at}', is_active={self.is_active}, is_used={self.is_used})>"

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_user(self, email: str, password: str) -> tuple[User | None, str]:
        db = self.SessionLocal()
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            db.close()
            return None, "User with this email already exists."
        
        new_user = User(email=email)
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        return new_user, "User created successfully."

    def get_user_by_email(self, email: str) -> User | None:
        db = self.SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        db.close()
        return user

    def create_license_for_user(self, user_id: int, duration_months: int) -> License:
        db = self.SessionLocal()
        expires_at = datetime.utcnow() + timedelta(days=30 * duration_months)
        key = self._generate_unique_license_key()
        new_license = License(key=key, user_id=user_id, expires_at=expires_at)
        db.add(new_license)
        db.commit()
        db.refresh(new_license)
        db.close()
        return new_license

    def _generate_unique_license_key(self, length=12):
        while True:
            key = "TSMART-PRO-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not self.get_license_by_key(key):
                return key

    def get_license_by_key(self, key: str) -> License | None:
        db = self.SessionLocal()
        license = db.query(License).filter(License.key == key).first()
        db.close()
        return license

    def bind_hwid_to_license(self, key: str, hwid: str) -> tuple[bool, str]:
        db = self.SessionLocal()
        license = db.query(License).filter(License.key == key).first()
        if not license:
            db.close()
            return False, "License key not found."
        
        if license.hwid and license.hwid != hwid:
            db.close()
            return False, "License is already bound to another HWID."
        
        license.hwid = hwid
        license.is_used = True # Mark as used once HWID is bound
        db.commit()
        db.refresh(license)
        db.close()
        return True, "HWID bound to license successfully."

    def activate_license(self, key: str, hwid: str) -> tuple[bool, str]:
        db = self.SessionLocal()
        license = db.query(License).filter(License.key == key).first()

        if not license:
            db.close()
            return False, "License key not found."

        if not license.is_active:
            db.close()
            return False, "License is inactive."

        if license.expires_at < datetime.utcnow():
            license.is_active = False
            db.commit()
            db.close()
            return False, "License has expired."

        # If license is used and HWID matches, it's already active for this device
        if license.is_used and license.hwid == hwid:
            db.close()
            return True, "License is already active on this device."

        # If license is used and HWID does not match
        if license.is_used and license.hwid != hwid:
            db.close()
            return False, "License is already in use on another device."
        
        # If license is not used, bind HWID and activate
        if not license.is_used:
            license.hwid = hwid
            license.is_used = True
            # When a license is activated, its expiration date is set from the activation date
            # This logic might need adjustment based on whether duration starts from creation or activation
            # For now, we assume duration starts from creation, and this is just for tracking usage.
            db.commit()
            db.refresh(license)
            db.close()
            return True, "License activated successfully."
        
        db.close()
        return False, "An unexpected error occurred during activation."

    def deactivate_license(self, key: str) -> bool:
        db = self.SessionLocal()
        license = db.query(License).filter(License.key == key).first()
        if license:
            license.is_active = False
            db.commit()
            db.close()
            return True
        db.close()
        return False

    def get_all_licenses(self) -> list[License]:
        db = self.SessionLocal()
        licenses = db.query(License).all()
        db.close()
        return licenses

    def get_licenses_by_hwid(self, hwid: str) -> list[License]:
        db = self.SessionLocal()
        licenses = db.query(License).filter(License.hwid == hwid).all()
        db.close()
        return licenses

    def update_license_expiration(self, key: str, new_expires_at: datetime) -> bool:
        db = self.SessionLocal()
        license = db.query(License).filter(License.key == key).first()
        if license:
            license.expires_at = new_expires_at
            db.commit()
            db.close()
            return True
        db.close()
        return False

    def delete_license(self, key: str) -> bool:
        db = self.SessionLocal()
        license = db.query(License).filter(License.key == key).first()
        if license:
            db.delete(license)
            db.commit()
            db.close()
            return True
        db.close()
        return False

    def get_all_users(self) -> list[User]:
        db = self.SessionLocal()
        users = db.query(User).all()
        db.close()
        return users


if __name__ == '__main__':
    db_manager = DatabaseManager()
    print("Database initialized and models created.")

    # Example usage:
    # user, msg = db_manager.create_user("test@example.com", "password123")
    # if user: print(f"Created user: {user.email}")

    # license = db_manager.create_license_for_user(user.id, 6)
    # print(f"Created license for user: {license.key}")

    # retrieved_user = db_manager.get_user_by_email("test@example.com")
    # if retrieved_user and retrieved_user.check_password("password123"):
    #     print(f"User {retrieved_user.email} authenticated.")

    # all_users = db_manager.get_all_users()
    # print("All users:")
    # for u in all_users:
    #     print(u)

    # all_licenses = db_manager.get_all_licenses()
    # print("All licenses:")
    # for lic in all_licenses:
    #     print(lic)
