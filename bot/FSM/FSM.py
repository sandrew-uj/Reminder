from aiogram.dispatcher.filters.state import StatesGroup, State


class FSM(StatesGroup):
    default_state = State()

    title_state = State()
    text_state = State()
    text_state_deal = State()
    remind_type_state = State()
    settings_timezone = State()
    add_remind_timezone = State()
    # list_deals = State()
    # set_deals = State()
    # remind_time_state = State()
