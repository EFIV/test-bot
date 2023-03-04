langs = {
    'ua': {
        'keyboards': {
            'cancel': "🔙 Відмінити",
            'back': "🔙 Назад",
            'settings': {
                'lang': "🗺 Мова: {lang}"
            },
            'class_choose': {
                'add_class': "📚 Створити групу"
            },
            'class_now': {
                'groups': "Групи 👫",
                'name': "Змінити Ім'я 🔁",
                'settings': "Налаштування ⚙",
                'delete': "Видалити ❌"
            },
            'class_settings': {
                'admins': "Адміністратори 👨‍💻",
                'lang': "🗺 Мова: {lang}",
                'notify': "🔔 Сповіщення: {notify}",
                'time': "⏰ Час сповіщення",
                'tz': "⏳ Часовий пояс: {tz}"
            },
            'class_delete': {
                'yes': "Так",
                'no': "Ні"
            },
            'class_admins': {
                'add_admin': "➕ Add admin"
            },
            'class_settings_tz': {
                '-12': "UTC−12, USA, Baker Island",
                '-9': "UTC−9, France, Gambier Islands",
                '-8': "UTC−8, USA, Washington",
                '-7': "UTC−7, USA, New Mexico",
                '-6': "UTC−6, USA, Minnesota",
                '-5': "UTC−5, USA, New York",
                '-2': "UTC-2, United Kingdom, London",
                '-1': "UTC−1, Portugal, Azores islands",
                '+0': "UTC+0, Ireland",
                '+1': "UTC+1, Germany",
                '+2': "UTC+2, Ukraine",
            },
            'class_settings_time': {
                'day': "🌞 Day before",
                'lesson': "🛎 Before lesson",
                'hrs': "{hrs} hrs",
                'mins': "{mins} mins",
                'gap': "{gap} mins",
                'save': "✅ Save changes"
            },
            'group_choose': {
                'add': "Add group ➕"
            },
            'group_now': {
                'name': "Change name 🗣",
                'timetable': "Edit timetable 🗓",
                'delete': "Delete group ❌"
            },
            'group_delete': {
                'yes': "Yes",
                'no': "No"
            },
            'group_timetable': {
                'add': "➕ Додати пару",
                'jan': "Січень",
                'feb': "Лютий",
                'mar': "Березень",
                'apr': "Квітень",
                'may': "Травень",
                'jun': "Червень",
                'jul': "Липень",
                'aug': "Серпень",
                'sep': "Вересень",
                'oct': "Жовтень",
                'nov': "Листопад",
                'dec': "Грудень",
                'mon': "Понеділок",
                'tue': "Вівторок",
                'wed': "Середа",
                'thi': "Четверг",
                'fri': "П'ятниця",
                'sat': "Субота",
                'sun': "Неділя",
            },
            'lesson': {
                'name': "💁‍♂️ Змінити Ім'я",
                'time': "⏳ Час початку та тривалість",
                'homework': "📚 Домашнє завдання",
                'place': "📍 Кабінет",
                'weekly': "📅 Тиждень? {weekly}",
                'all': "👁‍🗨 Додати для всіх груп? {all}",
                'create': "Створити пару ➕",
                'save': "Зберегти зміни ✅",
                'delete': "❌ Видалити пару",
                'original': "⤴ Повернутися до оригінальної пари",
                'restore': "♻ Відмінити зміни"
            },
            'lesson_time': {
                'start': "⏰ Час початку",
                'hrs': "{hrs} год",
                'mins': "{mins} хв",
                'duration': "⏳ Тривалість",
                'length': "{length} хв",
                'save': "✅ Зберегти зміни"
            }
        },
        'start':
            """
Привіт {name}! 👋

📅 Я @srnmSchoolBot для того, щоб скласти розклад ваших шкільних *уроків* і нагадати про ваші *шкільні завдання*

📝 Мене потрібно додати у ваш Telegram *класний чат*, щоб я міг надсилати вам повідомлення про ваші *уроки*

📌 Для отримання додаткової інформації спробуйте /help
            """,
        'help':
            """
🌎 Перш за все, перейдіть до /settings і виберіть свою мову!

🤔 Щоб використовувати @srnmSchoolBot, вам слід скористатися командою /class

📃 Якщо ви вже створили хоча б один клас, просто виберіть його зі списку (або створіть новий)
➕ В іншому випадку вам буде надана можливість створити його. Введіть назву вашого нового класу

💭 Після цього ви повинні додати @srnmSchoolBot у свій чат класу Telegram
✅ Потім напишіть /verify, щоб підключити ваш клас і бота (зверніть увагу, що ви повинні бути *адміністратором* у цьому чаті)

⏩ Тепер ви готові! Ви можете знову скористатися командою /class і вибрати свій клас
⚙ Спочатку зайдіть в налаштування! Тут виберіть, чи хочете ви отримувати сповіщення про уроки, виберіть часовий пояс вашого класу, щоб отримувати сповіщення в правильний час, а потім вам потрібно встановити час сповіщення
👨‍💻 Ви також можете додати іншого адміністратора, наприклад, якщо хочете, щоб хтось допоміг вам у редагуванні розкладу (зверніть увагу, що нові адміністратори можуть видалити інших адміністраторів)
👉 Щоб вибрати мову для свого класу, просто натисніть кнопку

❌ Ви можете видалити весь клас з усіма групами та уроками, ви можете змінити назву класу

📍 Щоб використовувати функцію планування, створіть принаймні одну групу. Ви також можете видалити його з усіма уроками або змінити назву

🗓 Тепер ви можете редагувати розклад!
👉 Перейдіть до дня, у який ви хочете додати новий урок, і натисніть кнопку, щоб додати урок
📚 Введіть інформацію про свій урок: назва (наприклад, математика), час початку (наприклад, 9 годин 30 хвилин), тривалість (наприклад, 45 хвилин), домашнє завдання (не обов’язково, наприклад, завдання 5, стор. 11), місце (не обов’язково, наприклад кімната 214 або Caroline College Center)
🔜 Вся ця інформація буде відображатися, коли ви будете сповіщені про урок. Ви також можете включити тижневий параметр, якщо ваш урок проводиться щотижня. З таким типом уроків ви не можете змінити їхній час для майбутніх уроків
🌐 Ви також можете додати урок для всіх груп. Для кожної групи у вашому класі буде створено дублікати уроку

↪ Коли ви закінчите з плануванням своїх уроків, ви можете перейти до свого чату класу в Telegram і знову перейти за допомогою команди /class, вибрати потрібну групу та вибрати урок, про який ви хочете дізнатися інформацію
✅ Ви також отримуватимете сповіщення про уроки у вашому чаті, якщо ввімкнете параметр сповіщення в налаштуваннях
            """,
        'support':
            """
📍 Якщо ви бачите, що щось не працює або вам потрібна допомога, ви можете зв’язатися з @maven6666
            """,
        'max_lim':
            """
❗ Ваше повідомлення має бути менше ніж {symbols} символів
            """,
        'settings':
            """
⚙ Це налаштування @srnmSchoolBot! Ви можете змінити мову тут:
            """,
        'class_create_name':
            """
Яку назву слід дати новому класу?
            """,
        'class_verify':
            """
🤔 Тепер вам потрібно підтвердити *{name}*!

👉 Додайте @srnmSchoolBot до свого класного чату, а потім увійдіть у цей чат за допомогою /verify

📌 _Зверніть увагу, що ви повинні бути адміністратором у цьому чаті_
            """,
        'class_exists':
            """
Клас для цього чату вже існує! ❌
            """,
        'not_admin':
            """
❗ Ви повинні бути адміністратором цього чату, щоб створити клас
            """,
        'no_classes':
            """
❗ У вас немає класів для перевірки! Перейдіть до @srnmSchoolBot, щоб створити новий клас
            """,
        'no_class':
            """
❗ У вас немає класу для цього чату! Перейдіть до @srnmSchoolBot, щоб створити новий клас, якщо ви адміністратор цього чату
            """,
        'no_groups':
            """
❗ У вас немає груп для *{name}*! Якщо ви адміністратор цієї групи, перейдіть до @srnmSchoolBot, щоб створити принаймні одну групу. Якщо ні, попросіть свого адміністратора зробити це
            """,
        'lesson_notification':
            """
*{clas} #group\_{group}*
🕰 Ваша пара розпочнеться через {start} хв
            """,
        'daily_notification':
            """
*{clas} #group\_{group}*
Завтра у вас будуть такі пари:
            """,
        'no_lessons':
            """
*{clas} #group\_{group}* у вас завтра пар немає!
            """,
        'class_added':
            """
Групу успішно додано! ✅

Використайте /class
            """,
        'class_choose':
            """
🏫 Ось ваші групи. Виберіть одну для роботи:
            """,
        'class_now':
            """
Це ваша група *{name}* 👈

⚙ Ви можете змінити його назву, видалити його, змінити деякі налаштування та вибрати групу для редагування розкладу
            """,
        'class_change_name':
            """
Яке нове ім'я вашої групи {name} нам взяти? 🤔
            """,
        'class_settings':
            """
Ось налаштування для вашої групи *{name}*:

🔻 Ви можете змінити адміністраторів групи
🔻 Змінити налаштування мови
🔻 Увімкнути/вимкнути сповіщення про уроки
🔻 Відредагуйте час сповіщень
🔻 Змінити часовий пояс
            """,
        'class_delete':
            """
❓ Звичайно, хочете видалити вашу групу {name}? *ВСІ ДАНІ ПРО ВАШІ ЗАНЯТТЯ ТА ГРУПИ БУДУТЬ ВИДАЛЕНІ!!!* ❓
            """,
        'class_deleted':
            """
Групу {name} успішно *видалено*! Спробуйте /class, щоб створити новий або виберіть існуючий
            """,
        'class_settings_tz':
            """
🌏 Виберіть часовий пояс, щоб отримувати сповіщення в правильний час
            """,
        'class_settings_time':
            """
⌚ Вкажіть час, коли ваш клас *{name}* буде повідомлено за день до уроків

🕰 Потім встановіть проміжок часу, коли ви будете сповіщені про наступний урок
            """,
        'class_admins':
            """
Ось усі адміністратори *{name}*! Ви можете видалити цих адміністраторів, окрім себе

Крім того, ви можете додати інших адміністраторів для свого класу
            """,
        'class_add_admin':
            """
Щоб додати адміністратора до *{name}*, надішліть мені Telegram ID користувача

Попросіть цього користувача використати @userinfobot, щоб надати вам свій ID Telegram
            """,
        'group_create_name':
            """
Як має бути назва вашої групи *{name}*?
            """,
        'group_choose':
            """
Ось групи *{name}*! Виберіть один для редагування розкладу 👈 
            """,
        'group_choose_timetable':
            """
Ось групи *{name}*! Виберіть один, щоб переглянути розклад 👈 
            """,
        'group_now':
            """
Це *{clas} {group}*. Виберіть, що ви хочете зробити👇
            """,
        'group_change_name':
            """
Якому імені ви віддаєте перевагу *{clas} {group}*? 🤔 
            """,
        'group_delete':
            """
Ви впевнені, що хочете видалити свій *{group}* з *{clas}*? Ваш розклад для цієї групи також буде видалено! ❌
            """,
        'group_timetable':
            """
🗓 Це розклад для *{clas} {group}*!

🤔 Тут ви можете додавати нові пари або редагувати наявні на певну дату
            """,
        'timetable':
            """
🗓 Це розклад для *{clas} {group}*!

🤔 Тут ви можете переглянути інформацію про свої пари
            """,
        'lesson_create_name':
            """
Як має бути назва вашої нової пари? 📕
            """,
        'lesson_name':
            """
Як має бути названий нова пара? *{lesson}*? 📕
            """,
        'lesson_create':
            """
Тут ви можете відредагувати свою нову пару для *{clas} {group}*! 👈

♻ Ви можете змінити його назву, вибрати час початку та його тривалість, ввести домашнє завдання, змінити місце, встановити, чи проводити цей урок щотижня, вибрати, чи додавати цей урок до всіх груп

І ось яку інформацію про свою пару ви вже заповнили 👇
            """,
        'lesson':
            """
Тут ви можете редагувати свою пару для *{clas} {group}*! 👈

♻ Ви можете змінити його назву, вибрати час початку та його тривалість, ввести домашнє завдання, змінити місце, встановити, чи повинна ця пара проводитись щотижня, і видалити його

І ось яку інформацію про свою пару ви вже заповнили 👇
            """,
        'weekly_lesson':
            """
Тут ви можете редагувати свою пару для *{clas} {group}*! 👈

🤔 Ця пара створюється автоматично, тому що ви встановили параметр Щотижня в оригінальній парі! Тут можна лише змінити назву, домашнє завдання та місце проведення пари
👉 Ви також можете перейти до оригінальної парри, щоб застосувати зміни до всіх майбутніх тижневих запланованих пар, або ви можете відновити зміни для цієї конкретної пари, щоб відповідати оригінальній

І ось яку інформацію про свою пару ви вже заповнили 👇
            """,
        'group_lesson':
            """
Ось інформація про вашу пару у *{clas} {group}* 👇
            """,
        'lesson_time':
            """
Тут ви можете змінити час початку пари та її тривалість ⏰
            """,
        'lesson_homework':
            """
Надішліть мені своє домашнє завдання сюди 📗
            """,
        'lesson_place':
            """
Обери місце для своєї пари! Це може бути номер вашого кабінету або навіть ціла адреса 📍
            """,
    },


'en': {
        'keyboards': {
            'cancel': "🔙 Cancel",
            'back': "🔙 Back",
            'settings': {
                'lang': "🗺 Language: {lang}"
            },
            'class_choose': {
                'add_class': "📚 Create class"
            },
            'class_now': {
                'groups': "Groups 👫",
                'name': "Change name 🔁",
                'settings': "Settings ⚙",
                'delete': "Delete ❌"
            },
            'class_settings': {
                'admins': "Admins 👨‍💻",
                'lang': "🗺 Language: {lang}",
                'notify': "🔔 Notifications: {notify}",
                'time': "⏰ Notification time",
                'tz': "⏳ Timezone: {tz}"
            },
            'class_delete': {
                'yes': "Yes",
                'no': "No"
            },
            'class_admins': {
                'add_admin': "➕ Add admin"
            },
            'class_settings_tz': {
                '-12': "UTC−12, USA, Baker Island",
                '-9': "UTC−9, France, Gambier Islands",
                '-8': "UTC−8, USA, Washington",
                '-7': "UTC−7, USA, New Mexico",
                '-6': "UTC−6, USA, Minnesota",
                '-5': "UTC−5, USA, New York",
                '-2': "UTC-2, United Kingdom, London",
                '-1': "UTC−1, Portugal, Azores islands",
                '+0': "UTC+0, Ireland",
                '+1': "UTC+1, Germany",
                '+2': "UTC+2, Ukraine",
            },
            'class_settings_time': {
                'day': "🌞 Day before",
                'lesson': "🛎 Before lesson",
                'hrs': "{hrs} hrs",
                'mins': "{mins} mins",
                'gap': "{gap} mins",
                'save': "✅ Save changes"
            },
            'group_choose': {
                'add': "Add group ➕"
            },
            'group_now': {
                'name': "Change name 🗣",
                'timetable': "Edit timetable 🗓",
                'delete': "Delete group ❌"
            },
            'group_delete': {
                'yes': "Yes",
                'no': "No"
            },
            'group_timetable': {
                'add': "➕ Add lesson",
                'jan': "Jan",
                'feb': "Feb",
                'mar': "Mar",
                'apr': "Apr",
                'may': "May",
                'jun': "Jun",
                'jul': "Jul",
                'aug': "Aug",
                'sep': "Sep",
                'oct': "Oct",
                'nov': "Nov",
                'dec': "Dec",
                'mon': "Mon",
                'tue': "Tue",
                'wed': "Wed",
                'thi': "Thi",
                'fri': "Fri",
                'sat': "Sat",
                'sun': "Sun",
            },
            'lesson': {
                'name': "💁‍♂️ Change name",
                'time': "⏳ Start time and duration",
                'homework': "📚 Homework",
                'place': "📍 Place",
                'weekly': "📅 Weekly? {weekly}",
                'all': "👁‍🗨 Add for all groups? {all}",
                'create': "Create lesson ➕",
                'save': "Save changes ✅",
                'delete': "❌ Delete lesson",
                'original': "⤴ Back to original lesson",
                'restore': "♻ Restore changes"
            },
            'lesson_time': {
                'start': "⏰ Start time",
                'hrs': "{hrs} hrs",
                'mins': "{mins} mins",
                'duration': "⏳ Duration",
                'length': "{length} mins",
                'save': "✅ Save changes"
            }
        },
        'start':
            """
Hi {name}! 👋
📅 I'm @srnmSchoolBot for scheduling your school *lessons* and reminding you about your *school tasks*
📝 I should be added into your Telegram *class chat* to be able to send you messages about your *lessons*
📌 For more info try /help
            """,
        'help':
            """
🌎 First of all, go to /settings and choose your language if exists!
🤔 To use @srnmSchoolBot you should go with /class command
📃 If you had already created at least one class, just choose it from the list (or create a new one)
➕ Otherwise, you will be given an opportunity to create one. Enter the name of your new class
💭 After that you should add @srnmSchoolBot into your Telegram class chat
✅ Then write /verify to connect your class and the bot (note that you should be an *administrator* in this chat)
⏩ Now you're done! You can go with /class command again and choose your class
⚙ Go to settings at first! Here choose if you want to be notified about the lessons, choose the timezone of your class to be notified in the correct time and then you have to set notification time
👨‍💻 You can also add another administrator, for example, if you want someone to help you in editing the schedule (note that new administrators can delete other admins)
👉 To choose language for your class, just press the button
❌ You can delete whole class with all groups and lessons, you can change class name
📍 To use scheduling feature, create at least one group. You can also delete it with all the lessons or change its name
🗓 Now you can edit timetable!
👉 Go to the day you want your new lesson to be and press the button to add a lesson
📚 Input info about your lesson: name (ex. Math), start time (ex. 9hrs 30mins), duration (ex. 45mins), homework (not necessary, ex. Task 5 p. 11), place (not necessary, ex. Room 214 or Caroline College Center)
🔜 All this info will be displayed, when you would be notified about the lesson. You can also put weekly parameter on if your lesson is held every week. With that type of lessons you can't change their time for future lessons
🌐 You can also add the lesson for all groups. The duplicates of the lesson will be created for each group in your class
↪ When you are done with scheduling your lessons, you can go to your Telegram class chat and go with /class command again, choose the desired group and choose the lesson you want to know info about
✅ You will be also notified about the lessons in your chat if you put notification parameter on in settings
            """,
        'support':
            """
📍 If you see something doesn't work or you need help, you can contact @srnm9
            """,
        'max_lim':
            """
❗ Your message should be less than {symbols} symbols
            """,
        'settings':
            """
⚙ These are @srnmSchoolBot settings! You can change your language here:
            """,
        'class_create_name':
            """
What name should be given for your new class?
            """,
        'class_verify':
            """
🤔 Now you should verify *{name}*!
👉 Add @srnmSchoolBot to your class chat and then go with /verify in this chat
📌 _Notice that you should be an administrator in this chat_
            """,
        'class_exists':
            """
Class for this chat already exists! ❌
            """,
        'not_admin':
            """
❗ You must be an admin of this chat to create a class
            """,
        'no_classes':
            """
❗ You have no classes to verify! Go to @srnmSchoolBot to create a new class
            """,
        'no_class':
            """
❗ You don't have a class for this chat! Go to @srnmSchoolBot to create a new class if you are an admin of this chat
            """,
        'no_groups':
            """
❗ You have no groups for *{name}*! If you are an admin for this class, go to @srnmSchoolBot to create at least one group. If not, ask your admin to do that
            """,
        'lesson_notification':
            """
*{clas} #group\_{group}*
🕰 Your lesson starts in {start} mins
            """,
        'daily_notification':
            """
*{clas} #group\_{group}*
Tomorrow you will have following lessons:
            """,
        'no_lessons':
            """
*{clas} #group\_{group}* you have no lessons tomorrow!
            """,
        'class_added':
            """
Class has been successfully added! ✅
Use /class
            """,
        'class_choose':
            """
🏫 Here are your classes. Choose one to work with:
            """,
        'class_now':
            """
This is your class *{name}* 👈
⚙ You can change its name, delete it, change some settings and choose a group to edit timetable
            """,
        'class_change_name':
            """
What new name of your class {name} should we take? 🤔
            """,
        'class_settings':
            """
Here are the settings for your class *{name}*:
🔻 You can change admins of the class
🔻 Change language settings
🔻 Turn on/off notifications about lessons
🔻 Edit the time of notifications
🔻 Change the timezone
            """,
        'class_delete':
            """
❓ Sure want to delete your class {name}? *ALL DATA ABOUT YOUR LESSONS AND GROUPS WILL BE DELETED!!!* ❓
            """,
        'class_deleted':
            """
Class {name} has been successfully *deleted*! Try /class to create a new one or choose the existing one
            """,
        'class_settings_tz':
            """
🌏 Choose your timezone to be notified in the correct time
            """,
        'class_settings_time':
            """
⌚ Put the time your class *{name}* would be notified the day before lessons
🕰 Then put a time gap when you would be notified about the next lesson 
            """,
        'class_admins':
            """
Here are all admins of *{name}*! You can delete these admins, except for yourself
Also, you can add other admins for your class
            """,
        'class_add_admin':
            """
To add an admin to *{name}*, send me the Telegram ID of the user
Ask this user to use @userinfobot to give you their Telegram ID
            """,
        'group_create_name':
            """
What should be the name of your *{name}* group?
            """,
        'group_choose':
            """
Here are *{name}* groups! Choose one to edit timetable 👈 
            """,
        'group_choose_timetable':
            """
Here are *{name}* groups! Choose one to view timetable 👈 
            """,
        'group_now':
            """
This is *{clas} {group}*. Choose, what you want to do 👇
            """,
        'group_change_name':
            """
Which name do you prefer instead of *{clas} {group}*? 🤔 
            """,
        'group_delete':
            """
Are you sure you want to delete your *{group}* of *{clas}*? Your timetable for this group will be deleted too! ❌
            """,
        'group_timetable':
            """
🗓 This is the timetable for *{clas} {group}*!
🤔 Here you can add new lessons or edit the existing ones on the particular date
            """,
        'timetable':
            """
🗓 This is the timetable for *{clas} {group}*!
🤔 Here you can view info about your lessons
            """,
        'lesson_create_name':
            """
What should be the name of your new lesson? 📕
            """,
        'lesson_name':
            """
What should be a new name of your lesson called *{lesson}*? 📕
            """,
        'lesson_create':
            """
Here you can edit your new lesson for *{clas} {group}*! 👈
♻ You can change the name of it, choose start time and its duration, input the homework, change the place, set if this lesson should be every week, choose if this lesson should be added to all groups
And that is what info about your lesson you have already filled 👇
            """,
        'lesson':
            """
Here you can edit your lesson for *{clas} {group}*! 👈
♻ You can change the name of it, choose start time and its duration, input the homework, change the place, set if this lesson should be every week and delete it
And that is what info about your lesson you have already filled 👇
            """,
        'weekly_lesson':
            """
Here you can edit your lesson for *{clas} {group}*! 👈
🤔 This lesson is automatically created, because you set Weekly parameter in the original lesson! Here you can only change name, homework and place of the lesson
👉 You can also go to the original lesson to apply changes to all future weekly scheduled lessons or you can restore changes for this particular lesson to match with the original one
And that is what info about your lesson you have already filled 👇
            """,
        'group_lesson':
            """
Here is info about your lesson in *{clas} {group}* 👇
            """,
        'lesson_time':
            """
Here you can change when the lesson starts and its duration ⏰
            """,
        'lesson_homework':
            """
Send me your homework here 📗
            """,
        'lesson_place':
            """
Choose a place for your lesson! It can be the number of your classroom or even the whole address 📍
            """,
    },

}