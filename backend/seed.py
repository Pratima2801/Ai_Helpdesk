import uuid
from .db import SessionLocal, init_db
from .models import BusinessInfo, Supervisor
from sqlalchemy.exc import IntegrityError

def seed():
    init_db()
    db = SessionLocal()
    try:
        # seed business info for the salon
        biz = BusinessInfo(
            id="biz_aurora",
            name="Aurora Salon",
            hours="Mon–Sat 9:00–19:00, Sun closed",
            services="Haircut: ₹600; Coloring from ₹1500; Blow-dry ₹400",
            phone="+919999900000",
            note="10% off first visit; cancellation requires 24-hour notice"
        )
        db.add(biz)

        # one supervisor user
        sup = Supervisor(
            id="super_1",
            name="Supervisor One",
            phone="+911234567890",
            email="supervisor@example.com"
        )
        db.add(sup)

        db.commit()
        print("Seeded DB with business info and one supervisor.")
    except IntegrityError:
        db.rollback()
        print("Seed already ran / entries exist.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
