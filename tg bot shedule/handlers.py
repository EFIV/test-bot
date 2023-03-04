import sqlalchemy.exc

import main
from langs import langs
import keyboards
from models import *
from utils import *
import settings

from typing import Union

from db.main import connect
from db.model import *
from sqlalchemy.sql import select
from sqlalchemy import null

from aiogram.types import Message, CallbackQuery, Update
from aiogram.dispatcher.dispatcher import FSMContext
from aiogram.utils.exceptions import RetryAfter, MessageNotModified

import datetime
from dateutil.relativedelta import relativedelta

dp = main.dp
bot = main.bot
schedule = AsyncIOScheduler()


async def max_lim(action, symbols):
    await text_message(action, create_text(action, 'max_lim', symbols=symbols))


@dp.errors_handler()
async def error(update: Update, err):
    msg = update.callback_query.message if update.callback_query else update.message
    if msg.chat.type == 'private':
        name = msg.chat.username if msg.chat.username else msg.chat.first_name
    else:
        name = msg.chat.title
    text = f"<b><i>Error occurred!</i></b> It was in <i>{msg.chat.type}</i> chat. Name of chat: <i>{name}</i>. Message text:\n\n<i>{msg.text}</i> \n\n{type(err).__name__}: {err}"

    for ADMIN in settings.ADMINS:
        await bot.send_message(ADMIN, text, parse_mode='HTML')


"""
BASE COMMANDS
"""


@dp.message_handler(lambda message: message.chat.type == 'private', commands='start', state=all_states)
async def start(action: Union[Message, CallbackQuery], state: FSMContext):
    s = connect()
    user = s.query(Users).filter(Users.telegram_id == action.from_user.id)
    if user.count() == 0:
        new_user = Users(telegram_id=str(action.from_user.id), lang=choose_language(action))
        s.add(new_user)
        s.commit()
    await state.finish()
    await action.answer(create_text(action, 'start', name=get_user_name(action)))


@dp.message_handler(lambda message: message.chat.type == 'group', commands='start', state=all_states)
async def start(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()
    await action.answer(create_text(action, 'start', name=get_user_name(action)))


@dp.message_handler(commands='help', state=all_states)
async def help_cmd(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()
    await action.answer(create_text(action, 'help'))


@dp.message_handler(commands='support', state=all_states)
async def support_cmd(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()
    await action.answer(create_text(action, 'support'))



"""
MESSAGE HANDLERS
"""


@dp.message_handler(lambda message: message.chat.type == 'group', commands='verify', state=all_states)
async def class_verify(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()

    user_admin = False
    for admin in await action.chat.get_administrators():
        if admin['user']['id'] == action.from_user.id and (admin['status'] == 'creator' or admin['status'] == 'administrator'):
            user_admin = True
            break
    if user_admin:
        s = connect()
        if s.query(Classes).filter(Classes.chat_id == action.chat.id).count() == 0:
            if s.query(Users).filter(Users.telegram_id == action.from_user.id).count() > 0:
                bad_classes = s.query(Classes).filter(Classes.chat_id == -1).all()
                if len(bad_classes) > 0:
                    for clas in bad_classes:
                        user_class = s.query(UserClasses).filter(UserClasses.class_id == clas.id).filter(UserClasses.user_id == s.query(Users).filter(Users.telegram_id == action.from_user.id).one().id)
                        if user_class.count() > 0:
                            s.query(Classes).filter(Classes.id == clas.id).update({'chat_id': action.chat.id})
                            s.commit()
                            await bot.send_message(action.from_user.id, create_text(action, 'class_added'))
                else:
                    await text_message(action, create_text(action, 'no_classes'))
        else:
            await text_message(action, create_text(action, 'class_exists'))
    else:
        await text_message(action, create_text(action, 'not_admin'))


@dp.message_handler(lambda message: message.chat.type == 'private', commands='settings', state=all_states)
async def settings_cmd(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()

    s = connect()
    user = s.query(Users).filter(Users.telegram_id == action.from_user.id)
    if user.count() == 0:
        new_user = Users(telegram_id=str(action.from_user.id), lang=choose_language(action))
        s.add(new_user)
        s.commit()

    await PrivateStates.settings.set()
    await text_message(action, create_text(action, 'settings'), keyboard=keyboards.settings(action, {'lang': user.one().lang}))


@dp.message_handler(lambda message: message.chat.type == 'private', commands='class', state=all_states)
async def class_cmd(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()

    s = connect()
    user = s.query(Users).filter(Users.telegram_id == action.from_user.id)
    if user.count() == 0:
        new_user = Users(telegram_id=str(action.from_user.id), lang=choose_language(action))
        s.add(new_user)
        s.commit()

    bad_classes = s.query(Classes).filter(Classes.chat_id == -1).all()
    for clas in bad_classes:
        user_class = s.query(UserClasses).filter(UserClasses.class_id == clas.id and UserClasses.user_id == s.query(Users).filter(Users.telegram_id == action.from_user.id).one().id)
        if user_class.count() > 0:
            user_class.delete()
            s.query(Classes).filter(Classes.id == clas.id).delete()
            s.commit()
    user_classes = s.query(UserClasses).filter(UserClasses.user_id == s.query(Users).filter(Users.telegram_id == action.from_user.id).one().id)
    if user_classes.count() > 0:
        await PrivateStates.class_choose.set()
        classes = list()
        for user_class in user_classes.all():
            clas = s.query(Classes).filter(Classes.id == user_class.class_id).one()
            classes.append(clas)
        await text_message(action, create_text(action, 'class_choose'), keyboard=keyboards.class_choose(action, sorted(classes, key=lambda x: x.name)))
    else:
        await class_create(action, state)


@dp.message_handler(lambda message: message.chat.type == 'group', commands='class', state=all_states)
async def chat_class_cmd(action: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()

    s = connect()
    clas = s.query(Classes).filter(Classes.chat_id == action.chat.id)
    if clas.count() == 0:
        await text_message(action, create_text(action, 'no_class'))
    else:
        clas = clas.one()
        groups = s.query(Groups).filter(Groups.class_id == clas.id)
        if groups.count() == 0:
            await text_message(action, create_text(action, 'no_groups', name=clas.name))
        else:
            groups = groups.all()
            await GroupStates.choose_group.set()
            await text_message(action, create_text(action, 'group_choose_timetable', name=clas.name), keyboard=keyboards.group_choose(action, groups, group=True))


"""
CLASS MESSAGE HANDLERS
"""


async def class_create(action: Union[Message, CallbackQuery], state: FSMContext):
    await PrivateStates.class_create_name.set()
    await text_message(action, create_text(action, 'class_create_name'), keyboard=keyboards.class_create_name(action))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.class_create_name)
async def class_create_name(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 64
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        s = connect()
        new_class = Classes(action.text)
        s.add(new_class)
        s.commit()
        new_user_class = UserClasses(s.query(Users).filter(Users.telegram_id == action.from_user.id).one().id, s.query(Classes).filter(Classes.name == action.text).all()[-1].id)
        s.add(new_user_class)
        s.commit()

        await PrivateStates.class_verify.set()
        await text_message(action, create_text(action, 'class_verify', name=action.text))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.class_change_name)
async def class_change_name(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 64
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
        s = connect()
        s.query(Classes).filter(Classes.id == class_id).update({'name': action.text})
        s.commit()

        await PrivateStates.class_now.set()
        name = s.query(Classes).filter(Classes.id == class_id).one().name
        await text_message(action, create_text(action, 'class_now', name=name), keyboard=keyboards.class_now(action))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.class_add_admin)
async def class_add_admin(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 10
    if not action.text.isdigit():
        async with state.proxy() as data:
            class_id = data['class_id']
        s = connect()
        clas = s.query(Classes).filter(Classes.id == class_id).one()
        await text_message(action, create_text(action, 'class_add_admin', name=clas.name), keyboard=keyboards.class_add_admin(action))
    elif len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
        s = connect()
        user = s.query(Users).filter(Users.telegram_id == action.text)
        if user.count() == 0:
            user = Users(action.text)
            s.add(user)
            s.commit()
        user = s.query(Users).filter(Users.telegram_id == action.text).one()
        user_classes = s.query(UserClasses).filter(UserClasses.user_id == user.id and UserClasses.class_id == class_id)
        if user_classes.count() == 0:
            user_classes = UserClasses(user.id, class_id)
            s.add(user_classes)
            s.commit()

        admin_ids = s.query(UserClasses).filter(UserClasses.class_id == class_id).all()
        admins = [s.query(Users).filter(Users.id == admin_id.user_id).one().telegram_id for admin_id in admin_ids]
        await PrivateStates.class_admins.set()
        await text_message(action, create_text(action, 'class_admins'), keyboard=keyboards.class_admins(action, admins))


"""
GROUP MESSAGE HANDLERS
"""


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.group_create_name)
async def group_create_name(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 64
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
        s = connect()
        new_group = Groups(class_id, action.text)
        s.add(new_group)
        s.commit()

        clas = s.query(Classes).filter(Classes.id == class_id).one()
        groups = s.query(Groups).filter(Groups.class_id == class_id).all()

        await PrivateStates.group_choose.set()
        await text_message(action, create_text(action, 'group_choose', name=clas.name), keyboard=keyboards.group_choose(action, sorted(groups, key=lambda x: x.name)))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.group_change_name)
async def group_change_name(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 64
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
        s = connect()
        s.query(Groups).filter(Groups.id == group_id).update({'name': action.text})
        s.commit()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()
        await PrivateStates.group_now.set()
        await text_message(action, create_text(action, 'group_now', clas=clas.name, group=group.name), keyboard=keyboards.group_now(action))


"""
LESSON MESSAGE HANDLERS
"""


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.lesson_create_name)
async def lesson_create_name(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 64
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
            date = data['date']
            data['lesson_name'] = action.text

        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(action, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await PrivateStates.lesson_create.set()
        await text_message(action, create_text(action, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(action, data))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.lesson_create_homework)
async def lesson_create_homework(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 1024
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
            date = data['date']
            data['lesson_homework'] = action.text

        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(action, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await PrivateStates.lesson_create.set()
        await text_message(action, create_text(action, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(action, data))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.lesson_create_place)
async def lesson_create_place(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 256
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
            date = data['date']
            data['lesson_place'] = action.text

        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(action, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await PrivateStates.lesson_create.set()
        await text_message(action, create_text(action, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(action, data))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.lesson_name)
async def lesson_name(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 64
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
            date = data['date']
            lesson = data['lesson']
            lesson.name = action.text
            data['lesson'] = lesson
            week = data['week']

        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(action, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(action, create_text(action, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(action, {'lesson_weekly': lesson.weekly}, week))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.lesson_homework)
async def lesson_homework(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 1024
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
            date = data['date']
            lesson = data['lesson']
            lesson.homework = action.text
            data['lesson'] = lesson
            week = data['week']

        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(action, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(action, create_text(action, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(action, {'lesson_weekly': lesson.weekly}, week))


@dp.message_handler(lambda message: message.chat.type == 'private', state=PrivateStates.lesson_place)
async def lesson_place(action: Union[Message, CallbackQuery], state: FSMContext):
    symbols = 256
    action.text = action.text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").strip()
    if len(action.text) > symbols:
        await max_lim(action, symbols)
    else:
        async with state.proxy() as data:
            class_id = data['class_id']
            group_id = data['group_id']
            date = data['date']
            lesson = data['lesson']
            lesson.place = action.text
            data['lesson'] = lesson
            week = data['week']

        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(action, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(action, create_text(action, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(action, {'lesson_weekly': lesson.weekly}, week))


"""
CALLBACK HANDLERS
"""


@dp.callback_query_handler(state=PrivateStates.settings)
async def callback_settings(callback: CallbackQuery, state: FSMContext):
    s = connect()
    user = s.query(Users).filter(Users.telegram_id == callback.from_user.id).one()

    if callback.data == 'settings_lang':
        lang = s.query(Users).filter(Users.telegram_id == str(callback.from_user.id)).one().lang
        new_lang = settings.LANGS[(settings.LANGS.index(user.lang) + 1) % len(settings.LANGS)]
        if lang != new_lang:
            s.query(Users).filter(Users.telegram_id == callback.from_user.id).update({'lang': new_lang})
            s.commit()
        await text_message(callback, create_text(callback, 'settings'), keyboard=keyboards.settings(callback, {'lang': new_lang}))
    elif callback.data == 'settings_cancel':
        await state.finish()
        await callback.message.delete()


"""
CLASS CALLBACKS
"""


@dp.callback_query_handler(state=PrivateStates.class_create_name)
async def callback_class_create_name(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'class_create_name_cancel':
        await state.finish()
        await callback.message.delete()


@dp.callback_query_handler(state=PrivateStates.class_choose)
async def callback_class_choose(callback: CallbackQuery, state: FSMContext):
    if callback.data[-1].isdigit() and callback.data.startswith('class_choose'):
        await PrivateStates.class_now.set()
        class_id = int(callback.data[13:])
        async with state.proxy() as data:
            data['class_id'] = class_id
        s = connect()
        name = s.query(Classes).filter(Classes.id == class_id).one().name
        await text_message(callback, create_text(callback, 'class_now', name=name), keyboard=keyboards.class_now(callback))
    elif callback.data == 'class_choose_add':
        await class_create(callback, state)
    elif callback.data == 'class_choose_cancel':
        await state.finish()
        await callback.message.delete()


@dp.callback_query_handler(state=PrivateStates.class_now)
async def callback_class_now(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_now_name':
        await PrivateStates.class_change_name.set()
        await text_message(callback, create_text(callback, 'class_change_name', name=clas.name), keyboard=keyboards.class_change_name(callback))
    elif callback.data == 'class_now_back':
        await class_cmd(callback, state)
    elif callback.data == 'class_now_settings':
        await PrivateStates.class_settings.set()
        await text_message(callback, create_text(callback, 'class_settings', name=clas.name), keyboard=keyboards.class_settings(callback, clas))
    elif callback.data == 'class_now_groups':
        groups = s.query(Groups).filter(Groups.class_id == class_id)
        if groups.count() > 0:
            await PrivateStates.group_choose.set()
            groups = s.query(Groups).filter(Groups.class_id == class_id).all()
            await text_message(callback, create_text(callback, 'group_choose', name=clas.name), keyboard=keyboards.group_choose(callback, sorted(groups, key=lambda x: x.name)))
        else:
            await PrivateStates.group_create_name.set()
            await text_message(callback, create_text(callback, 'group_create_name', name=clas.name), keyboard=keyboards.group_create_name(callback))
    elif callback.data == 'class_now_delete':
        await PrivateStates.class_delete.set()
        await text_message(callback, create_text(callback, 'class_delete', name=clas.name), keyboard=keyboards.class_delete(callback))


@dp.callback_query_handler(state=PrivateStates.class_change_name)
async def callback_class_change_name(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_change_name_back':
        await PrivateStates.class_now.set()
        await text_message(callback, create_text(callback, 'class_now', name=clas.name), keyboard=keyboards.class_now(callback))


@dp.callback_query_handler(state=PrivateStates.class_delete)
async def callback_class_delete(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_delete_no':
        await PrivateStates.class_now.set()
        await text_message(callback, create_text(callback, 'class_now', name=clas.name), keyboard=keyboards.class_now(callback))
    elif callback.data == 'class_delete_yes':
        groups_ids = s.query(Groups.id).filter(Groups.class_id == class_id)
        lessons_ids = s.query(Lessons.id).filter(Lessons.group_id.in_(select(groups_ids.subquery())))
        for lesson_id in lessons_ids.all():
            schedule.remove_job(f'lesson_{lesson_id}')
        schedule.remove_job(f'daily_{clas.id}')
        s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id.in_(select(lessons_ids.subquery()))).delete(synchronize_session='fetch')
        s.query(Lessons).filter(Lessons.group_id.in_(select(groups_ids.subquery()))).delete(synchronize_session='fetch')
        s.query(Groups).filter(Groups.class_id == class_id).delete(synchronize_session='fetch')
        s.query(UserClasses).filter(UserClasses.class_id == class_id).delete(synchronize_session='fetch')
        s.query(Classes).filter(Classes.id == class_id).delete(synchronize_session='fetch')
        s.commit()

        await state.finish()

        await text_message(callback, create_text(callback, 'class_deleted', name=clas.name))


@dp.callback_query_handler(state=PrivateStates.class_settings)
async def callback_class_settings(callback: CallbackQuery, state: FSMContext):
    global schedule
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_settings_admins':
        admin_ids = s.query(UserClasses).filter(UserClasses.class_id == class_id).all()
        admins = [s.query(Users).filter(Users.id == admin_id.user_id).one().telegram_id for admin_id in admin_ids]
        await PrivateStates.class_admins.set()
        await text_message(callback, create_text(callback, 'class_admins', name=clas.name), keyboard=keyboards.class_admins(callback, admins))
    elif callback.data == 'class_settings_lang':
        lang = clas.lang

        new_lang = settings.LANGS[(settings.LANGS.index(clas.lang) + 1) % len(settings.LANGS)]
        if lang != new_lang:
            s.query(Classes).filter(Classes.id == class_id).update({'lang': new_lang})
            s.commit()
            clas.lang = new_lang
        await text_message(callback, create_text(callback, 'class_settings', name=clas.name), keyboard=keyboards.class_settings(callback, clas))
    elif callback.data == 'class_settings_notify':
        clas.notify = (clas.notify + 1) % 2
        if clas.notify:
            groups_ids = s.query(Groups.id).filter(Groups.class_id == class_id)
            lessons_ids = s.query(Lessons.id).filter(Lessons.group_id.in_(select(groups_ids.subquery())))
            for lesson_id in lessons_ids.all():
                lesson = s.query(Lessons).filter(Lessons.id == lesson_id).one()
                schedule = lesson_notify(schedule, lesson)
            schedule = class_notify(schedule, clas)
        else:
            groups_ids = s.query(Groups.id).filter(Groups.class_id == class_id)
            lessons_ids = s.query(Lessons.id).filter(Lessons.group_id.in_(select(groups_ids.subquery())))
            for lesson_id in lessons_ids.all():
                schedule.remove_job(f'lesson_{lesson_id}')
            schedule.remove_job(f'daily_{clas.id}')
        s.query(Classes).filter(Classes.id == class_id).update({'notify': clas.notify})
        s.commit()
        await text_message(callback, keyboard=keyboards.class_settings(callback, clas))
    elif callback.data == 'class_settings_tz':
        await PrivateStates.class_timezone.set()
        await text_message(callback, create_text(callback, 'class_settings_tz'), keyboard=keyboards.class_settings_tz(callback, clas))
    elif callback.data == 'class_settings_time':
        await PrivateStates.class_notifications.set()
        async with state.proxy() as data:
            data['hrs'] = clas.notify_day_before.hour
            data['mins'] = clas.notify_day_before.minute
            data['gap'] = clas.notify_before_lesson
        await text_message(callback, create_text(callback, 'class_settings_time', name=clas.name), keyboard=keyboards.class_settings_time(callback, data))
    elif callback.data == 'class_settings_back':
        await PrivateStates.class_now.set()
        await text_message(callback, create_text(callback, 'class_now', name=clas.name), keyboard=keyboards.class_now(callback))
    s.close()


@dp.callback_query_handler(state=PrivateStates.class_admins)
async def callback_class_admins(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_admins_back':
        await PrivateStates.class_settings.set()
        await text_message(callback, create_text(callback, 'class_settings', name=clas.name), keyboard=keyboards.class_settings(callback, clas))
    elif callback.data == 'class_add_admin':
        await PrivateStates.class_add_admin.set()
        await text_message(callback, create_text(callback, 'class_add_admin', name=clas.name), keyboard=keyboards.class_add_admin(callback))
    elif callback.data.startswith('none_class_admin'):
        await alert(callback)
    elif callback.data.startswith('class_admin'):
        admin_ids = s.query(UserClasses).filter(UserClasses.class_id == class_id).all()
        admins = [s.query(Users).filter(Users.id == admin_id.user_id).one().telegram_id for admin_id in admin_ids]
        id = callback.data.split('class_admin_')[1]
        if id in admins:
            user_id = s.query(Users).filter(Users.telegram_id == id).one().id
            s.query(UserClasses).filter(UserClasses.user_id == user_id and UserClasses.class_id == class_id).delete()
            s.commit()
            admin_ids = s.query(UserClasses).filter(UserClasses.class_id == class_id).all()
            admins = [s.query(Users).filter(Users.id == admin_id.user_id).one().telegram_id for admin_id in admin_ids]
        await text_message(callback, create_text(callback, 'class_admins', name=clas.name), keyboard=keyboards.class_admins(callback, admins))


@dp.callback_query_handler(state=PrivateStates.class_add_admin)
async def callback_class_add_admin(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_add_admin_back':
        admin_ids = s.query(UserClasses).filter(UserClasses.class_id == class_id).all()
        admins = [s.query(Users).filter(Users.id == admin_id.user_id).one().telegram_id for admin_id in admin_ids]
        await PrivateStates.class_admins.set()
        await text_message(callback, create_text(callback, 'class_admins', name=clas.name), keyboard=keyboards.class_admins(callback, admins))


@dp.callback_query_handler(state=PrivateStates.class_timezone)
async def callback_class_settings_tz(callback: CallbackQuery, state: FSMContext):
    global schedule
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_settings_tz_back':
        await PrivateStates.class_settings.set()
        await text_message(callback, keyboard=keyboards.class_settings(callback, clas))
    elif callback.data.startswith('class_settings_tz_'):
        clas.tz = int(callback.data.split('class_settings_tz_')[-1])
        s.query(Classes).filter(Classes.id == class_id).update({'tz': clas.tz})
        s.commit()
        groups_ids = s.query(Groups.id).filter(Groups.class_id == class_id)
        lessons_ids = s.query(Lessons.id).filter(Lessons.group_id.in_(select(groups_ids.subquery())))
        for lesson_id in lessons_ids.all():
            lesson = s.query(Lessons).filter(Lessons.id == lesson_id[0]).one()
            schedule = lesson_notify(schedule, lesson)
        schedule = class_notify(schedule, clas)
        await PrivateStates.class_settings.set()
        await text_message(callback, keyboard=keyboards.class_settings(callback, clas))


@dp.callback_query_handler(state=PrivateStates.class_notifications)
async def callback_class_settings_time(callback: CallbackQuery, state: FSMContext):
    global schedule
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'class_settings_time_back':
        await PrivateStates.class_settings.set()
        await text_message(callback, keyboard=keyboards.class_settings(callback, clas))
    elif callback.data.startswith('none_class_settings_time'):
        await alert(callback)
    elif callback.data == 'class_settings_time_save':
        async with state.proxy() as data:
            s.query(Classes).filter(Classes.id == class_id).update({
                'notify_day_before': datetime.datetime(year=2005, month=9, day=9, hour=data['hrs'], minute=data['mins']),
                'notify_before_lesson': data['gap']})
            s.commit()

        groups_ids = s.query(Groups.id).filter(Groups.class_id == class_id)
        lessons_ids = s.query(Lessons.id).filter(Lessons.group_id.in_(select(groups_ids.subquery())))
        for lesson_id in lessons_ids.all():
            lesson = s.query(Lessons).filter(Lessons.id == lesson_id[0]).one()
            schedule = lesson_notify(schedule, lesson)
        schedule = class_notify(schedule, clas)

        await PrivateStates.class_settings.set()
        clas = s.query(Classes).filter(Classes.id == class_id).one()
        await text_message(callback, keyboard=keyboards.class_settings(callback, clas))
    elif callback.data.startswith('class_settings_time'):
        async with state.proxy() as data:
            if callback.data == 'class_settings_time_hrs_left':
                data['hrs'] = (data['hrs'] - 1) % 24
            elif callback.data == 'class_settings_time_hrs_right':
                data['hrs'] = (data['hrs'] + 1) % 24
            elif callback.data == 'class_settings_time_mins_left':
                data['mins'] = (data['mins'] - 10) % 60
            elif callback.data == 'class_settings_time_mins_right':
                data['mins'] = (data['mins'] + 10) % 60
            elif callback.data == 'class_settings_time_gap_left':
                data['gap'] = (data['gap'] - 5) % 60
            elif callback.data == 'class_settings_time_gap_right':
                data['gap'] = (data['gap'] + 5) % 60

            await text_message(callback, keyboard=keyboards.class_settings_time(callback, data))


"""
GROUP CALLBACKS
"""


@dp.callback_query_handler(state=PrivateStates.group_create_name)
async def callback_group_create_name(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'group_create_name_back':
        if groups:
            await PrivateStates.group_choose.set()
            await text_message(callback, create_text(callback, 'group_choose', name=clas.name), keyboard=keyboards.group_choose(callback, sorted(groups, key=lambda x: x.name)))
        else:
            await PrivateStates.class_now.set()
            await text_message(callback, create_text(callback, 'class_now', name=clas.name), keyboard=keyboards.class_now(callback))


@dp.callback_query_handler(state=PrivateStates.group_choose)
async def callback_group_choose(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'group_choose_back':
        await PrivateStates.class_now.set()
        await text_message(callback, create_text(callback, 'class_now', name=clas.name), keyboard=keyboards.class_now(callback))
    elif callback.data == 'group_choose_add':
        await PrivateStates.group_create_name.set()
        await text_message(callback, create_text(callback, 'group_create_name', name=clas.name), keyboard=keyboards.group_create_name(callback))
    elif callback.data.startswith('group_choose'):
        group_id = int(callback.data[13:])
        async with state.proxy() as data:
            data['group_id'] = group_id
        group = s.query(Groups).filter(Groups.id == group_id).one()
        await PrivateStates.group_now.set()
        await text_message(callback, create_text(callback, 'group_now', clas=clas.name, group=group.name), keyboard=keyboards.group_now(callback))


@dp.callback_query_handler(state=GroupStates.choose_group)
async def callback_chat_group_choose(callback: CallbackQuery, state: FSMContext):
    s = connect()
    clas = s.query(Classes).filter(Classes.chat_id == callback.message.chat.id).one()
    if callback.data == 'group_choose_cancel':
        await state.finish()
        await callback.message.delete()
    elif callback.data.startswith('group_choose'):
        group_id = int(callback.data[13:])
        async with state.proxy() as data:
            data['group_id'] = group_id
        group = s.query(Groups).filter(Groups.id == group_id).one()
        await GroupStates.timetable.set()

        date_utc = datetime.datetime.utcnow()
        delta = datetime.timedelta(hours=clas.tz)
        date = date_utc + delta

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date

        await text_message(callback, create_text(callback, 'timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date, group=True))


@dp.callback_query_handler(state=PrivateStates.group_now)
async def callback_group_now(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'group_now_back':
        await PrivateStates.group_choose.set()
        await text_message(callback, create_text(callback, 'group_choose', name=clas.name), keyboard=keyboards.group_choose(callback, sorted(groups, key=lambda x: x.name)))
    elif callback.data == 'group_now_name':
        await PrivateStates.group_change_name.set()
        await text_message(callback, create_text(callback, 'group_change_name', clas=clas.name, group=group.name), keyboard=keyboards.group_change_name(callback))
    elif callback.data == 'group_now_timetable':
        await PrivateStates.group_timetable.set()

        date_utc = datetime.datetime.utcnow()
        delta = datetime.timedelta(hours=clas.tz)
        date = date_utc + delta

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date

        await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))
    elif callback.data == 'group_now_delete':
        await PrivateStates.group_delete.set()
        await text_message(callback, create_text(callback, 'group_delete', clas=clas.name, group=group.name), keyboard=keyboards.group_delete(callback))


@dp.callback_query_handler(state=PrivateStates.group_delete)
async def callback_group_delete(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'group_delete_yes':
        await PrivateStates.class_now.set()

        lessons_ids = s.query(Lessons.id).filter(Lessons.group_id == group.id)
        for lesson_id in lessons_ids.all():
            schedule.remove_job(f'lesson_{lesson_id}')
        schedule.remove_job(f'daily_{clas.id}')

        lessons_ids = s.query(Lessons.id).filter(Lessons.group_id == group_id)
        s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id.in_(select(lessons_ids.subquery()))).delete(synchronize_session='fetch')
        s.query(Lessons).filter(Lessons.group_id == group_id).delete(synchronize_session='fetch')
        s.query(Groups).filter(Groups.id == group_id).delete(synchronize_session='fetch')
        s.commit()
        await text_message(callback, create_text(callback, 'class_now', name=clas.name), keyboard=keyboards.class_now(callback))
    elif callback.data == 'group_delete_no':
        await PrivateStates.group_now.set()
        await text_message(callback, create_text(callback, 'group_now', clas=clas.name, group=group.name), keyboard=keyboards.group_now(callback))


@dp.callback_query_handler(state=PrivateStates.group_change_name)
async def callback_group_change_name(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'group_change_name_back':
        await PrivateStates.group_now.set()
        await text_message(callback, create_text(callback, 'group_now', clas=clas.name, group=group.name), keyboard=keyboards.group_now(callback))


@dp.callback_query_handler(state=PrivateStates.group_timetable)
async def callback_group_timetable(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    if callback.data == 'group_timetable_add':
        async with state.proxy() as data:
            data['date'] = date.replace(hour=9, minute=0)
            data['lesson_name'] = False
            data['lesson_homework'] = False
            data['lesson_place'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False
            data['lesson_length'] = 45
        await PrivateStates.lesson_create_name.set()
        await text_message(callback, create_text(callback, 'lesson_create_name'), keyboard=keyboards.lesson_name(callback))
    elif callback.data.startswith('group_timetable_lesson_'):
        lesson_id = int(callback.data.split('group_timetable_lesson_')[1])
        lesson = s.query(Lessons).filter(Lessons.id == lesson_id).one()
        if lesson.start.date() == date.date():
            async with state.proxy() as data:
                data['date'] = lesson.start
                data['lesson'] = lesson
                data['week'] = None
                week = None
        else:
            async with state.proxy() as data:
                date = data['date']
                data['date'] = lesson.start
                week = (date.date() - lesson.start.date()).days // 7
                data['week'] = week
            weekly_lesson = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == lesson.id, WeeklyLessons.week == week)
            if weekly_lesson.count() > 0:
                weekly_lesson = weekly_lesson.one()
                lesson.name = weekly_lesson.name
                lesson.homework = weekly_lesson.homework
                lesson.place = weekly_lesson.place
            async with state.proxy() as data:
                data['lesson'] = lesson
            if weekly_lesson.count() > 0:
                lesson.start += datetime.timedelta(days=week * 7)

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
    elif callback.data == 'group_timetable_back':
        await PrivateStates.group_now.set()
        await text_message(callback, create_text(callback, 'group_now', clas=clas.name, group=group.name), keyboard=keyboards.group_now(callback))
    elif callback.data.startswith('none_group_timetable'):
        await alert(callback)
    elif callback.data.startswith('group_timetable_month'):
        if callback.data.endswith('left'):
            k = -1
        else:
            k = 1
        timedelta = relativedelta(months=k)
        new_date = date + timedelta
        date = new_date

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = new_date
            data['lesson_name'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False

        await text_message(callback, keyboard=keyboards.group_timetable(callback, lessons, new_date))
    elif callback.data.startswith('group_timetable_day'):
        if callback.data.endswith('left'):
            k = -1
        else:
            k = 1
        timedelta = datetime.timedelta(days=k)
        new_date = date + timedelta
        date = new_date

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = new_date

        await text_message(callback, keyboard=keyboards.group_timetable(callback, lessons, new_date))


@dp.callback_query_handler(state=GroupStates.timetable)
async def callback_chat_group_timetable(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        group_id = data['group_id']
        date = data['date']

    s = connect()
    clas = s.query(Classes).filter(Classes.chat_id == callback.message.chat.id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    if callback.data.startswith('group_timetable_lesson_'):
        lesson_id = int(callback.data.split('group_timetable_lesson_')[1])
        lesson = s.query(Lessons).filter(Lessons.id == lesson_id).one()
        if lesson.start.date() != date.date():
            week = (date.date() - lesson.start.date()).days // 7
            weekly_lesson = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == lesson.id, WeeklyLessons.week == week)
            if weekly_lesson.count() > 0:
                weekly_lesson = weekly_lesson.one()
                lesson.name = weekly_lesson.name
                lesson.homework = weekly_lesson.homework
                lesson.place = weekly_lesson.place
                lesson.start += datetime.timedelta(days=week * 7)

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"
        await alert(callback)
        await callback.message.answer(create_text(callback, 'group_lesson', clas=clas.name, group=group.name) + markdownv2(info))
    elif callback.data == 'group_timetable_back':
        groups = s.query(Groups).filter(Groups.class_id == clas.id).all()
        await GroupStates.choose_group.set()
        await text_message(callback, create_text(callback, 'group_choose_timetable', name=clas.name), keyboard=keyboards.group_choose(callback, groups, group=True))
    elif callback.data.startswith('none_group_timetable'):
        await alert(callback)
    elif callback.data.startswith('group_timetable_month'):
        if callback.data.endswith('left'):
            k = -1
        else:
            k = 1
        timedelta = relativedelta(months=k)
        new_date = date + timedelta
        date = new_date

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = new_date

        await text_message(callback, keyboard=keyboards.group_timetable(callback, lessons, new_date, group=True))
    elif callback.data.startswith('group_timetable_day'):
        if callback.data.endswith('left'):
            k = -1
        else:
            k = 1
        timedelta = datetime.timedelta(days=k)
        new_date = date + timedelta
        date = new_date

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = new_date

        await text_message(callback, keyboard=keyboards.group_timetable(callback, lessons, new_date, group=True))


"""
LESSON CALLBACKS
"""


@dp.callback_query_handler(state=PrivateStates.lesson_create_name)
async def callback_lesson_create_name(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        name = data['lesson_name']
        homework = data['lesson_homework']
        place = data['lesson_place']
        weekly = data['lesson_weekly']
        all_groups = data['lesson_all']
        length = data['lesson_length']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'lesson_name_back':
        if name:
            s = connect()

            group = s.query(Groups).filter(Groups.id == group_id).one()
            clas = s.query(Classes).filter(Classes.id == class_id).one()

            fields = create_button_text(callback, 'group_timetable')

            info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

            if 'lesson_place' in data.keys() and data['lesson_place']:
                info += f"\n📍 {data['lesson_place']}"
            if 'lesson_homework' in data.keys() and data['lesson_homework']:
                info += f"\n📝 {data['lesson_homework']}"

            await PrivateStates.lesson_create.set()
            await text_message(callback, create_text(callback, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(callback, data))
        else:
            await PrivateStates.group_timetable.set()

            lessons = []
            lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
            lessons += lessons_daily
            lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
            for l in lessons_weekly:
                week = (date.date() - l.start.date()).days // 7
                weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
                if weekly_l.count() > 0:
                    weekly_l = weekly_l.one()
                    l.name = weekly_l.name
                    l.homework = weekly_l.homework
                    l.place = weekly_l.place
                lessons.append(l)

            lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

            async with state.proxy() as data:
                data['date'] = date

            await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))


@dp.callback_query_handler(state=PrivateStates.lesson_create)
async def callback_lesson_create(callback: CallbackQuery, state: FSMContext):
    global schedule
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        name = data['lesson_name']
        homework = data['lesson_homework']
        place = data['lesson_place']
        weekly = data['lesson_weekly']
        all_groups = data['lesson_all']
        length = data['lesson_length']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    if callback.data == 'lesson_create_back':
        await PrivateStates.group_timetable.set()

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date
            data['lesson_name'] = False
            data['lesson_homework'] = False
            data['lesson_place'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False
            data['lesson_length'] = False

        await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))
    elif callback.data == 'lesson_create_name':
        await PrivateStates.lesson_create_name.set()
        await text_message(callback, create_text(callback, 'lesson_create_name'), keyboard=keyboards.lesson_name(callback))
    elif callback.data == 'lesson_create_time':
        async with state.proxy() as data:
            await PrivateStates.lesson_create_time.set()
            await text_message(callback, create_text(callback, 'lesson_time'), keyboard=keyboards.lesson_time(callback, data))
    elif callback.data == 'lesson_create_homework':
        await PrivateStates.lesson_create_homework.set()
        await text_message(callback, create_text(callback, 'lesson_homework'), keyboard=keyboards.lesson_homework(callback))
    elif callback.data == 'lesson_create_homework_delete':
        async with state.proxy() as data:
            data['lesson_homework'] = False

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await text_message(callback, create_text(callback, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(callback, data))
    elif callback.data == 'lesson_create_place':
        await PrivateStates.lesson_create_place.set()
        await text_message(callback, create_text(callback, 'lesson_place'), keyboard=keyboards.lesson_place(callback))
    elif callback.data == 'lesson_create_place_delete':
        async with state.proxy() as data:
            data['lesson_place'] = False

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await text_message(callback, create_text(callback, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(callback, data))
    elif callback.data == 'lesson_create_weekly':
        new_weekly = not weekly
        async with state.proxy() as data:
            data['lesson_weekly'] = new_weekly
        await text_message(callback, keyboard=keyboards.lesson_create(callback, data))
    elif callback.data == 'lesson_create_all':
        new_all = not all_groups
        async with state.proxy() as data:
            data['lesson_all'] = new_all
        await text_message(callback, keyboard=keyboards.lesson_create(callback, data))
    elif callback.data == 'lesson_create_add':
        async with state.proxy() as data:
            date = data['date']
            name = data['lesson_name']
            homework = data['lesson_homework']
            place = data['lesson_place']
            weekly = data['lesson_weekly']
            all_groups = data['lesson_all']
            length = data['lesson_length']

        if all_groups:
            groups = s.query(Groups).filter(Groups.class_id == class_id).all()
            for g in groups:
                lesson = Lessons(g.id, name, date, homework if homework else None, place if place else None, length, weekly)
                s.add(lesson)
                s.commit()
                start_date = date.replace(microsecond=0, second=0)
                end = start_date + datetime.timedelta(minutes=1)
                lessons = s.query(Lessons).filter(Lessons.group_id == g.id, Lessons.name == name,
                                                  Lessons.start >= start_date, Lessons.start < end,
                                                  Lessons.homework == (homework if homework else null()), Lessons.place == (place if place else null()),
                                                  Lessons.length == length, Lessons.weekly == weekly).all()
                lesson_ = max(lessons, key=lambda l: l.id)
                schedule = lesson_notify(schedule, lesson_)

        else:
            lesson = Lessons(group_id, name, date, homework if homework else None, place if place else None, length, weekly)
            s.add(lesson)
            s.commit()
            start_date = date.replace(microsecond=0, second=0)
            end = start_date + datetime.timedelta(minutes=1)
            lessons = s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.name == name,
                                              Lessons.start >= start_date, Lessons.start < end,
                                              Lessons.homework == (homework if homework else null()), Lessons.place == (place if place else null()),
                                              Lessons.length == length, Lessons.weekly == weekly).all()
            lesson_ = max(lessons, key=lambda l: l.id)
            schedule = lesson_notify(schedule, lesson_)

        await PrivateStates.group_timetable.set()

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date
            data['lesson_name'] = False
            data['lesson_homework'] = False
            data['lesson_place'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False
            data['lesson_length'] = False

        await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))


@dp.callback_query_handler(state=PrivateStates.lesson_create_homework)
async def callback_lesson_create_homework(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        name = data['lesson_name']
        homework = data['lesson_homework']
        place = data['lesson_place']
        weekly = data['lesson_weekly']
        all_groups = data['lesson_all']
        length = data['lesson_length']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'lesson_homework_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await PrivateStates.lesson_create.set()
        await text_message(callback, create_text(callback, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(callback, data))


@dp.callback_query_handler(state=PrivateStates.lesson_create_place)
async def callback_lesson_create_place(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        name = data['lesson_name']
        homework = data['lesson_homework']
        place = data['lesson_place']
        weekly = data['lesson_weekly']
        all_groups = data['lesson_all']
        length = data['lesson_length']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'lesson_place_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await PrivateStates.lesson_create.set()
        await text_message(callback, create_text(callback, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(callback, data))


@dp.callback_query_handler(state=PrivateStates.lesson_create_time)
async def callback_lesson_create_time(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        name = data['lesson_name']
        homework = data['lesson_homework']
        place = data['lesson_place']
        weekly = data['lesson_weekly']
        all_groups = data['lesson_all']
        length = data['lesson_length']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'lesson_time_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[date.weekday()]]}, {date.day} {fields[months[date.month]]}, {date.year}\n📚 {data['lesson_name']}\n⏰ {data['date'].hour}:{data['date'].minute if data['date'].minute > 9 else '0' + str(data['date'].minute)} — {data['lesson_length']}'"

        if 'lesson_place' in data.keys() and data['lesson_place']:
            info += f"\n📍 {data['lesson_place']}"
        if 'lesson_homework' in data.keys() and data['lesson_homework']:
            info += f"\n📝 {data['lesson_homework']}"

        await PrivateStates.lesson_create.set()
        await text_message(callback, create_text(callback, 'lesson_create', clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson_create(callback, data))
    elif callback.data.startswith('none_lesson_time'):
        await alert(callback)
    elif callback.data.startswith('lesson_time'):
        async with state.proxy() as data:
            if callback.data == 'lesson_time_hrs_left':
                data['date'] = data['date'].replace(hour=(data['date'].hour - 1) % 24)
            elif callback.data == 'lesson_time_hrs_right':
                data['date'] = data['date'].replace(hour=(data['date'].hour + 1) % 24)
            elif callback.data == 'lesson_time_mins_left':
                data['date'] = data['date'].replace(minute=(data['date'].minute - 5) % 60)
            elif callback.data == 'lesson_time_mins_right':
                data['date'] = data['date'].replace(minute=(data['date'].minute + 5) % 60)
            elif callback.data == 'lesson_time_duration_left':
                data['lesson_length'] = max(data['lesson_length'] - 5, 0)
            elif callback.data == 'lesson_time_duration_right':
                data['lesson_length'] = data['lesson_length'] + 5

            await text_message(callback, keyboard=keyboards.lesson_time(callback, data))


@dp.callback_query_handler(state=PrivateStates.lesson)
async def callback_lesson(callback: CallbackQuery, state: FSMContext):
    global schedule
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        lesson = data['lesson']
        week = data['week']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    if callback.data == 'lesson_back':
        await PrivateStates.group_timetable.set()

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date
            data['lesson_name'] = False
            data['lesson_homework'] = False
            data['lesson_place'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False
            data['lesson_length'] = False

        await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))
    elif callback.data == 'lesson_original':
        fields = create_button_text(callback, 'group_timetable')

        week = None
        lesson = s.query(Lessons).filter(Lessons.id == lesson.id).one()
        async with state.proxy() as data:
            data['week'] = week
            data['lesson'] = lesson

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
    elif callback.data == 'lesson_restore':
        lesson = s.query(Lessons).filter(Lessons.id == lesson.id).one()
        async with state.proxy() as data:
            data['lesson'] = lesson

        fields = create_button_text(callback, 'group_timetable')
        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
    elif callback.data == 'lesson_name':
        await PrivateStates.lesson_name.set()
        await text_message(callback, create_text(callback, 'lesson_name', lesson=lesson.name), keyboard=keyboards.lesson_name(callback))
    elif callback.data == 'lesson_time':
        if week is None:
            await PrivateStates.lesson_time.set()
            await text_message(callback, create_text(callback, 'lesson_time'), keyboard=keyboards.lesson_time(callback, {'lesson_length': lesson.length, 'date': lesson.start}))
        else:
            await alert(callback)
    elif callback.data == 'lesson_homework':
        await PrivateStates.lesson_homework.set()
        await text_message(callback, create_text(callback, 'lesson_homework'), keyboard=keyboards.lesson_homework(callback))
    elif callback.data == 'lesson_homework_delete':
        lesson.homework = None
        async with state.proxy() as data:
            data['lesson'] = lesson

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
    elif callback.data == 'lesson_place':
        await PrivateStates.lesson_place.set()
        await text_message(callback, create_text(callback, 'lesson_place'), keyboard=keyboards.lesson_place(callback))
    elif callback.data == 'lesson_place_delete':
        lesson.place = None
        async with state.proxy() as data:
            data['lesson'] = lesson

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
    elif callback.data == 'lesson_weekly':
        if week is None:
            lesson.weekly = not lesson.weekly
            async with state.proxy() as data:
                data['lesson'] = lesson
            await text_message(callback, keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
        else:
            await alert(callback)
    elif callback.data == 'lesson_delete':
        s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == lesson.id).delete(synchronize_session='fetch')
        s.query(Lessons).filter(Lessons.id == lesson.id).delete(synchronize_session='fetch')
        s.commit()
        await PrivateStates.group_timetable.set()

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date
            data['lesson_name'] = False
            data['lesson_homework'] = False
            data['lesson_place'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False
            data['lesson_length'] = False
            data['week'] = None

        await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))
    elif callback.data == 'lesson_save':
        if week is None:
            s.query(Lessons).filter(Lessons.id == lesson.id).update({'name': lesson.name, 'start': lesson.start, 'length': lesson.length, 'homework': lesson.homework, 'place': lesson.place, 'weekly': lesson.weekly})
            if not lesson.weekly:
                s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == lesson.id).delete()
            s.commit()
            schedule = lesson_notify(schedule, lesson)
        else:
            normal_lesson = s.query(Lessons).filter(Lessons.id == lesson.id).one()
            weekly_lesson = WeeklyLessons(lesson.id, week, lesson.name, lesson.homework, lesson.place)
            if normal_lesson.name == weekly_lesson.name and normal_lesson.homework == weekly_lesson.homework and normal_lesson.place == weekly_lesson.place:
                existing_weekly_lesson = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == lesson.id, WeeklyLessons.week == week)
                if existing_weekly_lesson.count() > 0:
                    existing_weekly_lesson.delete()
                    s.commit()
            else:
                existing_weekly_lesson = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == lesson.id, WeeklyLessons.week == week)
                if existing_weekly_lesson.count() > 0:
                    existing_weekly_lesson.update({'name': weekly_lesson.name, 'homework': weekly_lesson.homework, 'place': weekly_lesson.place})
                    s.commit()
                else:
                    s.add(weekly_lesson)
                    s.commit()

        await PrivateStates.group_timetable.set()

        lessons = []
        lessons_daily = list(filter(lambda lesson: lesson.start.date() == date.date(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 0).all()))
        lessons += lessons_daily
        lessons_weekly = list(filter(lambda lesson: lesson.start.weekday() == date.weekday(), s.query(Lessons).filter(Lessons.group_id == group_id, Lessons.weekly == 1).all()))
        for l in lessons_weekly:
            week = (date.date() - l.start.date()).days // 7
            weekly_l = s.query(WeeklyLessons).filter(WeeklyLessons.lesson_id == l.id, WeeklyLessons.week == week)
            if weekly_l.count() > 0:
                weekly_l = weekly_l.one()
                l.name = weekly_l.name
                l.homework = weekly_l.homework
                l.place = weekly_l.place
            lessons.append(l)

        lessons = sorted(lessons, key=lambda lesson: lesson.start.time())

        async with state.proxy() as data:
            data['date'] = date
            data['lesson_name'] = False
            data['lesson_homework'] = False
            data['lesson_place'] = False
            data['lesson_weekly'] = False
            data['lesson_all'] = False
            data['lesson_length'] = False
            data['week'] = None

        await text_message(callback, create_text(callback, 'group_timetable', clas=clas.name, group=group.name), keyboard=keyboards.group_timetable(callback, lessons, date))


@dp.callback_query_handler(state=PrivateStates.lesson_name)
async def callback_lesson_name(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        lesson = data['lesson']
        week = data['week']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'lesson_name_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await PrivateStates.lesson.set()
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))


@dp.callback_query_handler(state=PrivateStates.lesson_homework)
async def callback_lesson_homework(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        lesson = data['lesson']
        week = data['week']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'lesson_homework_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await PrivateStates.lesson.set()
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))


@dp.callback_query_handler(state=PrivateStates.lesson_place)
async def callback_lesson_place(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        lesson = data['lesson']
        week = data['week']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    group = s.query(Groups).filter(Groups.id == group_id).one()
    groups = s.query(Groups).filter(Groups.class_id == class_id).all()
    if callback.data == 'lesson_place_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await PrivateStates.lesson.set()
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))


@dp.callback_query_handler(state=PrivateStates.lesson_time)
async def callback_lesson_time(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        class_id = data['class_id']
        group_id = data['group_id']
        date = data['date']
        lesson = data['lesson']
        week = data['week']

    s = connect()
    clas = s.query(Classes).filter(Classes.id == class_id).one()
    if callback.data == 'lesson_time_back':
        s = connect()

        group = s.query(Groups).filter(Groups.id == group_id).one()
        clas = s.query(Classes).filter(Classes.id == class_id).one()

        fields = create_button_text(callback, 'group_timetable')

        info = f"\n🗓 {fields[weekdays[lesson.start.weekday()]]}, {lesson.start.day} {fields[months[lesson.start.month]]}, {lesson.start.year}\n📚 {lesson.name}\n⏰ {lesson.start.hour}:{lesson.start.minute if lesson.start.minute > 9 else '0' + str(lesson.start.minute)} — {lesson.length}'"

        if lesson.place:
            info += f"\n📍 {lesson.place}"
        if lesson.homework:
            info += f"\n📝 {lesson.homework}"

        await PrivateStates.lesson.set()
        if week is None:
            text = 'lesson'
        else:
            text = 'weekly_lesson'
        await text_message(callback, create_text(callback, text, clas=clas.name, group=group.name) + markdownv2(info), keyboard=keyboards.lesson(callback, {'lesson_weekly': lesson.weekly}, week))
    elif callback.data.startswith('none_lesson_time'):
        await alert(callback)
    elif callback.data.startswith('lesson_time'):
        async with state.proxy() as data:
            if callback.data == 'lesson_time_hrs_left':
                lesson.start = lesson.start.replace(hour=(lesson.start.hour - 1) % 24)
            elif callback.data == 'lesson_time_hrs_right':
                lesson.start = lesson.start.replace(hour=(lesson.start.hour + 1) % 24)
            elif callback.data == 'lesson_time_mins_left':
                lesson.start = lesson.start.replace(minute=(lesson.start.minute - 5) % 60)
            elif callback.data == 'lesson_time_mins_right':
                lesson.start = lesson.start.replace(minute=(lesson.start.minute + 5) % 60)
            elif callback.data == 'lesson_time_duration_left':
                lesson.length = max(lesson.length - 5, 0)
            elif callback.data == 'lesson_time_duration_right':
                lesson.length = lesson.length + 5
            data['lesson'] = lesson
            await text_message(callback, keyboard=keyboards.lesson_time(callback, {'lesson_length': lesson.length, 'date': lesson.start}))