from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import date, datetime
from app.db.models.itinerary import Itinerary
from app.db.models.itinerary_step import ItineraryStep
from app.db.models.location import Location

class ItineraryService:
    @staticmethod
    def get_or_create_itinerary(user_id: str, date_: date, db: Session) -> Itinerary:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        # 같은 날짜에 이미 itinerary가 있으면 반환, 없으면 생성
        itinerary = db.query(Itinerary).filter(
            Itinerary.user_id == user_id,
            Itinerary.start_date <= date_,
            Itinerary.end_date >= date_,
            Itinerary.delete_yn == 'N',
            Itinerary.use_yn == 'Y',
        ).first()
        if itinerary:
            return itinerary
        # 새 itinerary 생성 (start_date = end_date = date_)
        itinerary = Itinerary(
            id=uuid4(),
            user_id=user_id,
            start_date=date_,
            end_date=date_,
            use_yn='Y',
            delete_yn='N',
        )
        db.add(itinerary)
        db.commit()
        db.refresh(itinerary)
        return itinerary

    @staticmethod
    def add_step(user_id: str, location_id: str, date_: date, start_time: datetime, end_time: datetime, db: Session) -> ItineraryStep:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(location_id, str):
            location_id = UUID(location_id)
        itinerary = ItineraryService.get_or_create_itinerary(user_id, date_, db)
        # 해당 itinerary의 기존 step들 불러오기
        steps = db.query(ItineraryStep).filter(
            ItineraryStep.itinerary_id == itinerary.id,
            ItineraryStep.delete_yn == 'N',
            ItineraryStep.use_yn == 'Y',
        ).order_by(ItineraryStep.date, ItineraryStep.start_time).all()
        # 새 step의 step_order 결정
        insert_index = 0
        for i, step in enumerate(steps):
            if (step.date, step.start_time) < (date_, start_time):
                insert_index = i + 1
        step_order = insert_index
        # step_order 이후의 step들은 +1씩 밀기 (DB에 반영)
        for i in range(len(steps)-1, step_order-1, -1):
            steps[i].step_order += 1
            db.add(steps[i])
        # 새 step 생성
        new_step = ItineraryStep(
            id=uuid4(),
            itinerary_id=itinerary.id,
            location_id=location_id,
            step_order=step_order,
            date=date_,
            start_time=start_time,
            end_time=end_time,
            use_yn='Y',
            delete_yn='N',
        )
        db.add(new_step)
        db.commit()
        db.refresh(new_step)
        return new_step 