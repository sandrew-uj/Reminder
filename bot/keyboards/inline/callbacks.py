from aiogram.utils.callback_data import CallbackData

menu_callback = CallbackData("menu", "cbtype")
choose_type_callback = CallbackData("remind_type", "choose", "remind_type")
settings_callback = CallbackData("settings", "cbtype")
remind_type_callback = CallbackData("remind_type", "is_many_times")
choose_remind_callback = CallbackData("choose_remind", "remind_id", "pos", "temp")
choose_tz_callback = CallbackData("choose_tz", "tz", "temp")
delete_callback = CallbackData("delete", "is_del", "remind_id")
create_remind_or_deal = CallbackData("create_remind_or_deal", "action", "deal")

choose_unsorted_callback = CallbackData("choose_unsorted", "deal_id", "pos", "temp")
delete_unsorted_callback = CallbackData("delete_unsorted", "is_del", "deal_id")
