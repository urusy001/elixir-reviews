from aiogram.fsm.state import StatesGroup, State

class DraftSubmission(StatesGroup):
    correction = State()
