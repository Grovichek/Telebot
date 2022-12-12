from telebot.handler_backends import State, StatesGroup


class MainStates(StatesGroup):
    main_menu = State()
    get_city = State()
    get_check_in = State()
    get_check_out = State()
    get_num_of_results = State()
    get_is_show_photo = State()
    get_num_of_photos = State()
    show_result = State()
