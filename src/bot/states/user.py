from aiogram.fsm.state import State, StatesGroup

class EditDraft(StatesGroup):
    drugs = State()
    age = State()
    gender = State()
    height = State()
    starting_weight = State()
    current_weight = State()
    desired_weight = State()
    lost_weight = State()
    time_period = State()
    course = State()
    photo = State()
    commentary = State()
