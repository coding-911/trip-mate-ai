from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import date, datetime
from app.db.models.itinerary import Itinerary
from app.db.models.itinerary_step import ItineraryStep

class ItineraryStepService:
    @staticmethod
    def create_step(user_id: str, location_id: str, date_: date, start_time: datetime, end_time: datetime, db: Session, itinerary_id: str = None) -> ItineraryStep:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(location_id, str):
            location_id = UUID(location_id)
        # itinerary_id가 있으면 해당 itinerary 사용, 없으면 생성
        if itinerary_id:
            if isinstance(itinerary_id, str):
                itinerary_id = UUID(itinerary_id)
            itinerary = db.query(Itinerary).filter(
                Itinerary.id == itinerary_id,
                Itinerary.delete_yn == 'N',
                Itinerary.use_yn == 'Y',
            ).first()
            if not itinerary:
                raise ValueError('해당 itinerary가 존재하지 않거나 이미 삭제됨')
        else:
            itinerary = db.query(Itinerary).filter(
                Itinerary.user_id == user_id,
                Itinerary.start_date <= date_,
                Itinerary.end_date >= date_,
                Itinerary.delete_yn == 'N',
                Itinerary.use_yn == 'Y',
            ).first()
            if not itinerary:
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
        # step_order 결정
        steps = db.query(ItineraryStep).filter(
            ItineraryStep.itinerary_id == itinerary.id,
            ItineraryStep.delete_yn == 'N',
            ItineraryStep.use_yn == 'Y',
        ).order_by(ItineraryStep.date, ItineraryStep.start_time).all()
        insert_index = 0
        for i, step in enumerate(steps):
            if (step.date, step.start_time) < (date_, start_time):
                insert_index = i + 1
        step_order = insert_index
        for i in range(len(steps)-1, step_order-1, -1):
            steps[i].step_order += 1
            db.add(steps[i])
        new_step = ItineraryStep(
            id=uuid4(),
            itinerary_id=itinerary.id,
            location_id=location_id,
            step_order=0,  # 임시값
            date=date_,
            start_time=start_time,
            end_time=end_time,
            use_yn='Y',
            delete_yn='N',
        )
        db.add(new_step)
        db.commit()
        db.refresh(new_step)
        # step_order 재정렬 보장 (여기서만 일괄 부여)
        ItineraryStepService.reorder_steps(itinerary.id, db)
        db.refresh(new_step)
        return new_step

    @staticmethod
    def update_step(step_id: str, update_data: dict, db: Session) -> ItineraryStep:
        step = db.query(ItineraryStep).filter(ItineraryStep.id == UUID(step_id), ItineraryStep.delete_yn == 'N').first()
        if not step:
            raise ValueError('해당 step이 존재하지 않거나 이미 삭제됨')
        if update_data.get('date') is not None:
            step.date = update_data['date']
        if update_data.get('start_time') is not None:
            step.start_time = update_data['start_time']
        if update_data.get('end_time') is not None:
            step.end_time = update_data['end_time']
        if update_data.get('location_id') is not None:
            step.location_id = UUID(update_data['location_id']) if isinstance(update_data['location_id'], str) else update_data['location_id']
        db.add(step)
        db.commit()
        db.refresh(step)
        # step_order 재정렬
        ItineraryStepService.reorder_steps(step.itinerary_id, db)
        db.refresh(step)
        return step

    @staticmethod
    def delete_step(step_id: str, db: Session):
        step = db.query(ItineraryStep).filter(ItineraryStep.id == UUID(step_id), ItineraryStep.delete_yn == 'N').first()
        if not step:
            raise ValueError('해당 step이 존재하지 않거나 이미 삭제됨')
        step.delete_yn = 'Y'
        db.add(step)
        db.commit()
        # step_order 재정렬
        ItineraryStepService.reorder_steps(step.itinerary_id, db)
        # 모든 step이 삭제되면 itinerary도 소프트 삭제
        ItineraryStepService.delete_itinerary_if_all_steps_deleted(step.itinerary_id, db)

    @staticmethod
    def reorder_steps(itinerary_id: UUID, db: Session):
        steps = db.query(ItineraryStep).filter(
            ItineraryStep.itinerary_id == itinerary_id,
            ItineraryStep.delete_yn == 'N',
            ItineraryStep.use_yn == 'Y',
        ).order_by(ItineraryStep.date, ItineraryStep.start_time).all()
        for idx, step in enumerate(steps):
            step.step_order = idx
            db.add(step)
        db.commit()

    @staticmethod
    def delete_itinerary_if_all_steps_deleted(itinerary_id: UUID, db: Session):
        steps = db.query(ItineraryStep).filter(
            ItineraryStep.itinerary_id == itinerary_id,
            ItineraryStep.delete_yn == 'N',
            ItineraryStep.use_yn == 'Y',
        ).all()
        if not steps:
            itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id, Itinerary.delete_yn == 'N').first()
            if itinerary:
                itinerary.delete_yn = 'Y'
                db.add(itinerary)
                db.commit() 