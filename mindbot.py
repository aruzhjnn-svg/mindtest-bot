# mindbot.py
# MindBot — продвинутый тест (30 вопросов, 10 типов), с атмосферным интро и иллюстрациями
# Требует: python-telegram-bot (v22+), pillow, nest_asyncio
# Установка:
# pip install python-telegram-bot==22.3 pillow nest_asyncio

import io
import textwrap
import asyncio
import nest_asyncio
nest_asyncio.apply()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from PIL import Image, ImageDraw, ImageFont

# ---- ВСТАВЬ СВОЙ ТОКЕН (СТРОКОЙ) ----
TOKEN = "8284089177:AAEt9UbfWrXh5BSkRcQIoXLDqMVbkk9Be1c"
# ---------------------------------------

# ----- ОПИСАНИЕ 10 ТИПОВ (длинные описания и советы) -----
TYPES = {
    "Leader": {
        "title": "Лидер",
        "short": "Решительный организатор и вдохновитель команды.",
        "desc": (
            "Ты берёшь инициативу и спокойно ведёшь людей к цели. Ты умеешь брать ответственность, "
            "видишь общую картину и принимаешь тяжёлые решения. Люди тянутся к твоей уверенности, "
            "тебе комфортно управлять процессами и брать на себя ответственность в критические моменты."
        ),
        "advice": (
            "Развивай эмоциональную гибкость: иногда людям нужна не только жесткая структура, "
            "но и мягкость. Практикуй активное слушание — это поможет ещё лучше понимать мотивацию команды. "
            "Учись делегировать постепенно: выделяй людям небольшие зоны ответственности и отслеживай результат, "
            "это освободит твоё время для стратегического планирования."
        ),
        "color": (239, 71, 111)
    },
    "Analyst": {
        "title": "Аналитик",
        "short": "Точный мыслитель, который любит порядок и логику.",
        "desc": (
            "Ты системный и рациональный — любишь данные, аргументы и предсказуемые шаги. "
            "Твоя сила — глубина анализа: ты видишь причинно-следственные связи и умеешь предугадывать последствия. "
            "В сложных задачах тебя ценят за точность и последовательность."
        ),
        "advice": (
            "Работай над передачей своих идей простым языком — иногда сложные идеи теряются в деталях. "
            "Добавляй к аналитике визуальные схемы и короткие выводы: это ускорит принятие решений коллегами. "
            "Не бойся тестировать гипотезы: небольшие эксперименты укрепят уверенность в решениях."
        ),
        "color": (17, 138, 178)
    },
    "Creator": {
        "title": "Креатор",
        "short": "Генератор идей, творец образов и нестандартных решений.",
        "desc": (
            "Тебе близок свободный поток идей и неожиданные ассоциации. Ты легко находишь новые пути, "
            "любишь эксперименты и умеешь вдохновлять других. Внешне ты можешь казаться ветреной, "
            "но в этом потоке рождаются действительно оригинальные решения."
        ),
        "advice": (
            "Структурируй процесс воплощения идей: делай чек-листы и временные рамки для прототипа. "
            "Фокусируйся на одной идее в цикле — так вероятность её реализации выше. "
            "Ищи единомышленников для реализации: команда даёт стабильность твоему творческому огню."
        ),
        "color": (255, 159, 67)
    },
    "Executor": {
        "title": "Исполнитель",
        "short": "Практичный, надёжный, доводит дело до конца.",
        "desc": (
            "Твоя сила — в стабильной работе и аккуратном доведении дел до результата. "
            "Ты видишь шаги для реализации и не боишься рутинных задач — благодаря тебе идеи превращаются в продукт."
        ),
        "advice": (
            "Иногда полезно выделять время на креатив — даже 30 минут в неделю помогут найти оптимизации. "
            "Учись делегировать рутину и пробовать новые методы работы: небольшие эксперименты повысят эффективность."
        ),
        "color": (94, 92, 230)
    },
    "Diplomat": {
        "title": "Дипломат",
        "short": "Тёплый и отзывчивый связующий элемент в команде.",
        "desc": (
            "Ты умеешь слышать других, находить баланс и помогать людям чувствовать себя комфортно. "
            "Часто ты те, кто разрешает конфликты и поддерживает мотивацию коллектива."
        ),
        "advice": (
            "Учись ставить границы: забота о других важна, но не должна выжигать ресурсы. "
            "Развивай навыки ассертивного общения — это позволит выражать свою позицию мягко, но ясно."
        ),
        "color": (72, 201, 176)
    },
    "Explorer": {
        "title": "Исследователь",
        "short": "Любитель нового: любознательный, гибкий, экспериментатор.",
        "desc": (
            "Ты тянешься к неизвестному, легко переключаешься и любишь тестировать гипотезы. "
            "Тебе важен процесс обучения и свобода пробовать альтернативные пути."
        ),
        "advice": (
            "Организуй результаты своих опытов: журнал наблюдений увеличит ценность твоих идей. "
            "Создай мини-цели для экспериментов — так ты сможешь извлечь больше пользы из каждого шага."
        ),
        "color": (142, 68, 173)
    },
    "Organizer": {
        "title": "Организатор",
        "short": "Тот, кто создаёт порядок и помогает системе работать.",
        "desc": (
            "Ты отлично выстраиваешь процессы, знаешь, как организовать людей и ресурсы так, чтобы всё шло гладко. "
            "Тебе важно ощущение контроля и понятные правила."
        ),
        "advice": (
            "Добавь в свою рутину пространство для долгосрочной стратегии — это повысит влияние твоей организаторской работы. "
            "Развивай коммуникативные каналы: простые инструкции и чек-листы сделают процесс ещё лучше."
        ),
        "color": (249, 205, 173)
    },
    "Observer": {
        "title": "Наблюдатель",
        "short": "Вдумчивый, тихий, глубокий мыслитель.",
        "desc": (
            "Ты замечаешь мелочи и анализируешь мир изнутри. Часто предпочитаешь наблюдать, прежде чем действовать. "
            "Это дар: ты видишь то, что упускают другие."
        ),
        "advice": (
            "Пробуй делиться своими наблюдениями по чуть-чуть: даже короткая мысль может вдохновить команду. "
            "Ищи безопасные форматы выражения мыслей — например, короткие заметки или визуальные схемы."
        ),
        "color": (130, 130, 130)
    },
    "Visionary": {
        "title": "Визионер",
        "short": "Смотрите далеко вперёд — стратег с большими идеями.",
        "desc": (
            "Тебе близки долгие горизонты и большие цели. Ты умеешь формулировать амбициозные миссии и видишь будущее в картинках."
        ),
        "advice": (
            "Учи превращать абстрактные видения в первые конкретные шаги: карта дорожной реализации поможет команде следовать за тобой."
        ),
        "color": (255, 204, 102)
    },
    "Realist": {
        "title": "Реалист",
        "short": "Приземлённый практик — смотрит на вещи такими, какие они есть.",
        "desc": (
            "Ты здраво оцениваешь риски и возможности. Тебе легко выбирать наиболее устойчивый путь и отсеивать лишнее."
        ),
        "advice": (
            "Иногда стоит пробовать малые «лирические» эксперименты — это разогреет креативность и расширит варианты решений."
        ),
        "color": (100, 150, 100)
    }
}

# ----- 30 вопросов. Каждый вариант содержит список типов, которым даётся +1 за выбор.
# Варианты: "Согласна" (agree), "Не уверена" (neutral), "Не согласна" (disagree)
QUESTIONS = [
    ("Ты предпочитаешь брать инициативу в проекте или ждать указаний?",
     [(["Leader","Visionary"],), (["Organizer","Analyst"],), (["Executor","Realist"],)]),

    ("Как тебе важнее работать: в команде или в одиночку?",
     [(["Diplomat","Organizer"],), (["Analyst","Observer"],), (["Creator","Explorer"],)]),

    ("Как реагируешь на внезапные изменения плана?",
     [(["Leader","Executor"],), (["Analyst","Explorer"],), (["Diplomat","Organizer"],)]),

    ("Тебя больше вдохновляют идеи или выполнение задач?",
     [(["Creator","Visionary"],), (["Analyst","Observer"],), (["Executor","Realist"],)]),

    ("Комфортнее работать по чёткому плану или спонтанно?",
     [(["Organizer","Analyst"],), (["Leader","Explorer"],), (["Creator","Diplomat"],)]),

    ("Любишь ли ты часто менять направления и пробовать новое?",
     [(["Explorer","Creator"],), (["Visionary","Leader"],), (["Executor","Realist"],)]),

    ("Тебе важнее эмоциональная поддержка команды?",
     [(["Diplomat","Observer"],), (["Leader","Organizer"],), (["Analyst","Realist"],)]),

    ("Ты любишь обсуждать идеи вслух или работать в тишине?",
     [(["Creator","Diplomat"],), (["Explorer","Leader"],), (["Analyst","Observer"],)]),

    ("Как часто ты предлагаешь улучшения в процессе?",
     [(["Analyst","Explorer"],), (["Creator","Leader"],), (["Executor","Organizer"],)]),

    ("Ты быстро принимаешь решения в стрессовой ситуации?",
     [(["Leader","Realist"],), (["Analyst","Diplomat"],), (["Observer","Organizer"],)]),

    ("Нравится ли тебе фокус на деталях?",
     [(["Analyst","Executor"],), (["Observer","Organizer"],), (["Visionary","Creator"],)]),

    ("Тебе комфортно омрачать спор ради компромисса?",
     [(["Diplomat","Organizer"],), (["Observer","Analyst"],), (["Leader","Visionary"],)]),

    ("Хочешь ли ты иметь постоянный распорядок дня?",
     [(["Executor","Organizer"],), (["Analyst","Realist"],), (["Explorer","Creator"],)]),

    ("Ты чувствуешь себя энергично после общения с людьми?",
     [(["Diplomat","Leader"],), (["Creator","Explorer"],), (["Observer","Analyst"],)]),

    ("Ты чаще действуешь по интуиции, чем по плану?",
     [(["Creator","Explorer"],), (["Visionary","Leader"],), (["Analyst","Realist"],)]),

    ("Тебе проще довести дело до конца, чем придумать новое?",
     [(["Executor","Organizer"],), (["Leader","Analyst"],), (["Creator","Explorer"],)]),

    ("Предпочитаешь масштабные проекты или локальные задачи?",
     [(["Visionary","Leader"],), (["Analyst","Organizer"],), (["Executor","Realist"],)]),

    ("Ты охотнее слушаешь других, чем говоришь сама?",
     [(["Diplomat","Observer"],), (["Analyst","Creator"],), (["Leader","Visionary"],)]),

    ("Как относишься к критике?",
     [(["Analyst","Executor"],), (["Diplomat","Observer"],), (["Creator","Leader"],)]),

    ("Важнее ли тебе стабильность, чем риск ради прорыва?",
     [(["Realist","Executor"],), (["Organizer","Analyst"],), (["Explorer","Visionary"],)]),

    ("Ты любишь планировать на 6–12 месяцев вперёд?",
     [(["Visionary","Analyst"],), (["Organizer","Leader"],), (["Creator","Explorer"],)]),

    ("Ты склонна к аккуратной записи наблюдений/идей?",
     [(["Observer","Analyst"],), (["Organizer","Executor"],), (["Creator","Visionary"],)]),

    ("Любишь ли ты вдохновлять людей образами и историями?",
     [(["Creator","Visionary"],), (["Leader","Diplomat"],), (["Analyst","Realist"],)]),

    ("Когда появляется проблема — ты ищешь быстрый практичный выход?",
     [(["Realist","Executor"],), (["Analyst","Leader"],), (["Diplomat","Observer"],)]),

    ("Тебе важно, чтобы работа приносила смысл?",
     [(["Diplomat","Visionary"],), (["Creator","Analyst"],), (["Executor","Realist"],)]),

    ("Ты предпочитаешь сначала протестировать идею, а затем масштабировать?",
     [(["Explorer","Analyst"],), (["Visionary","Creator"],), (["Executor","Organizer"],)]),

    ("Тебе нравится видеть порядок и структурированность вокруг?",
     [(["Organizer","Executor"],), (["Analyst","Realist"],), (["Creator","Explorer"],)]),

    ("Тебя заводят большие цели и мечты?",
     [(["Visionary","Leader"],), (["Creator","Explorer"],), (["Realist","Analyst"],)]),

    ("Тебе легче выражать мысли письменно, чем устно?",
     [(["Observer","Analyst"],), (["Diplomat","Creator"],), (["Leader","Organizer"],)]),

    ("Ты чаще делаешь шаг после долгого размышления, чем сразу?",
     [(["Observer","Analyst"],), (["Organizer","Executor"],), (["Leader","Visionary"],)])
]

# Приведём к удобному виду: каждый вариант — список типов (а не кортежи)
for i, (q, opts) in enumerate(QUESTIONS):
    normalized = []
    for opt in opts:
        # в нашем формате opt может быть (["TypeA","TypeB"],) поэтому берем первый элемент если это кортеж
        if isinstance(opt, tuple) or isinstance(opt, list):
            if len(opt) > 0 and isinstance(opt[0], list):
                normalized.append(opt[0])
            else:
                # fallback
                normalized.append(list(opt))
        else:
            normalized.append(list(opt))
    QUESTIONS[i] = (q, normalized)

# ----- Хранилище данных (в памяти) -----
user_data = {}  # user_id -> {"q": int, "scores": {type: int}, "answers": []}

# ----- Шаблоны шрифтов для PIL (попытайся использовать системный шрифт, иначе default) -----
def load_fonts():
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_body = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_body = ImageFont.load_default()
    return font_title, font_sub, font_body

# ----- Функция по созданию иллюстрации под тип -----
def create_result_image(type_key, title, subtitle):
    info = TYPES[type_key]
    color = info["color"]
    img = Image.new("RGB", (900, 500), color)
    draw = ImageDraw.Draw(img)
    font_title, font_sub, font_body = load_fonts()

    # фон: легкий градиент (простейший)
    for i in range(100):
        overlay = Image.new("RGBA", (900, 5), (255, 255, 255, int(8 - i * 0.05)))
        img.paste(overlay, (0, i * 5), overlay)

    # заголовок
    draw.text((40, 30), title, font=font_title, fill="white")
    draw.text((40, 80), subtitle, font=font_sub, fill="white")

    # простая декоративная "иллюстрация": круг + волна
    cx, cy = 700, 220
    draw.ellipse((cx-120, cy-120, cx+120, cy+120), outline="white", width=6)
    # внутренняя волнистая линия
    for j in range(10):
        offset = j * 6
        draw.arc((cx-90-offset, cy-90+offset, cx+90-offset, cy+90+offset), start=0, end=180, fill="white")

    # короткая метка типа
    draw.text((40, 420), f"Тип: {info['title']}", font=font_sub, fill="white")
    draw.text((240, 420), f"Кратко: {info['short']}", font=font_sub, fill="white")

    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

# ----- Старт и навигация -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    # инициализация пользователя
    user_data[user_id] = {"q": 0, "scores": {k: 0 for k in TYPES.keys()}, "answers": []}
    text = (
        f"🌿 Привет, {user.first_name or 'путешественник'}!\n\n"
        "Я — MindBot. Я помогу тебе понять, как ты работаешь, думаешь и принимаешь решения.\n"
        "Это спокойный, но живой психологический тест: 30 коротких вопросов.\n\n"
        "Готова начать небольшое исследование себя? →"
    )
    buttons = [
        [InlineKeyboardButton("🚀 Поехали", callback_data="start_test")],
        [InlineKeyboardButton("🤔 Сначала подробнее", callback_data="explain")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def explain_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📝 Формат:\n"
        "- 30 вопросов; на каждый — 3 варианта: «Согласна», «Не уверена», «Не согласна».\n"
        "- После теста — подробный анализ: твой тип, развёрнутое описание, детальные советы и иллюстрация.\n\n"
        "Готова начать?"
    )
    buttons = [[InlineKeyboardButton("Да, начать", callback_data="start_test")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# ----- Отправка вопроса -----
async def send_question(update_obj, context, user_id):
    # update_obj может быть update.callback_query или update.message
    data = user_data[user_id]
    q_index = data["q"]

    # Если вопросов больше нет — показать результат
    if q_index >= len(QUESTIONS):
        return await show_result(update_obj, context, user_id)

    question, options = QUESTIONS[q_index]
    # Кнопки: три варианта
    kb = [
        [InlineKeyboardButton("✅ Согласна", callback_data=f"ans|{q_index}|0")],
        [InlineKeyboardButton("➖ Не уверена", callback_data=f"ans|{q_index}|1")],
        [InlineKeyboardButton("❌ Не согласна", callback_data=f"ans|{q_index}|2")],
    ]
    progress = f"Вопрос {q_index+1} из {len(QUESTIONS)}"
    text = f"🔎 {question}\n\n{progress}"
    if isinstance(update_obj, type(context.application.bot)):
        # unlikely
        pass

    if hasattr(update_obj, "callback_query") and update_obj.callback_query:
        await update_obj.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update_obj.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))

# ----- Обработка кнопок ответов -----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user_id = query.from_user.id
    if user_id not in user_data:
        # инициализируем, если вдруг
        user_data[user_id] = {"q": 0, "scores": {k: 0 for k in TYPES.keys()}, "answers": []}

    # Навигация: старт теста или объяснение
    if data == "start_test":
        await send_question(update, context, user_id)
        return
    if data == "explain":
        await explain_intro(update, context)
        return
    if data == "retake":
        # сброс и старт заново
        user_data[user_id] = {"q": 0, "scores": {k: 0 for k in TYPES.keys()}, "answers": []}
        await send_question(update, context, user_id)
        return

    # Ответы формата ans|{q_index}|{option_index}
    if data.startswith("ans|"):
        try:
            _, q_str, opt_str = data.split("|")
            q_index = int(q_str)
            opt_index = int(opt_str)
        except Exception:
            await query.edit_message_text("Произошла ошибка в обработке ответа. Попробуй ещё раз.")
            return

        # Если q_index не совпадает с ожидаемым — игнорируем или синхронизируем
        user_state = user_data[user_id]
        if q_index != user_state["q"]:
            # синхронизируем: установим q = q_index (без штрафов)
            user_state["q"] = q_index

        # Зарегистрируем ответ: добавим голоса для типов, соответствующих варианту
        _, options = QUESTIONS[q_index]
        selected_types = options[opt_index]  # список типов
        for t in selected_types:
            if t in user_state["scores"]:
                user_state["scores"][t] += 1

        user_state["answers"].append((q_index, opt_index, selected_types))
        user_state["q"] += 1

        # отправим следующий вопрос или результат
        if user_state["q"] < len(QUESTIONS):
            await send_question(update, context, user_id)
        else:
            await show_result(update, context, user_id)
        return

    # Доп. кнопки: подробнее по типу / поделиться
    if data.startswith("more|"):
        _, type_key = data.split("|")
        if type_key in TYPES:
            info = TYPES[type_key]
            text = f"✨ *{info['title']}*\n\n{info['desc']}\n\n💡 *Совет*: {info['advice']}\n\nПродолжение следует..."
            await query.edit_message_text(text, parse_mode="Markdown")
        else:
            await query.edit_message_text("Инфо недоступно.")
        return

# ----- Формирование и отправка результата -----
async def show_result(update_obj, context, user_id):
    state = user_data[user_id]
    scores = state["scores"]

    # Найдём топ-2 типа для более богатого анализа
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_type = sorted_types[0][0]
    second_type = sorted_types[1][0] if len(sorted_types) > 1 else None

    info = TYPES[top_type]

    # Составляем развёрнутый анализ (подробно)
    desc = info["desc"]
    advice = info["advice"]

    # Дополняем анализ контекстом второго типа (если он близок)
    analysis_text = f"*{info['title']}* — {info['short']}\n\n{desc}\n\n"
    if second_type and scores[second_type] > 0:
        sec = TYPES[second_type]
        analysis_text += (
            f"— В твоём профиле также заметны элементы *{sec['title']}*. "
            f"Это значит, что вместе с основными чертами ты иногда проявляешься как {sec['short'].lower()}.\n\n"
        )

    # Более персонализованные советы: разбиваем по тематике
    analysis_text += "*Детальные рекомендации:*\n"
    # общие советы
    analysis_text += f"• {advice}\n\n"

    # Призыв к действию и "Продолжение следует..."
    analysis_text += "Хочешь подробнее погрузиться в свой тип — практики, упражнения и план развития? Нажми «Подробнее» или пройди тест заново."

    # Создаем картинку результата
    title = f"Ты — {info['title']}"
    subtitle = info['short']
    img_bio = create_result_image(top_type, title, subtitle)

    # формируем кнопки: подробнее по типу, пройти заново
    kb = [
        [InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"more|{top_type}"),
         InlineKeyboardButton("🔄 Пройти заново", callback_data="retake")],
    ]

    # Отправляем: если вызов был из callback_query — используем edit_message / reply_photo
    if hasattr(update_obj, "callback_query") and update_obj.callback_query:
        # удалим старое сообщение с последнего вопроса и отправим картинку с подписью
        try:
            # отправляем фото с подписью
            await update_obj.callback_query.message.reply_photo(
                photo=img_bio,
                caption=analysis_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(kb)
            )
            # и удалим старое сообщение с последним вопросом (если хочется) — опционально
            try:
                await update_obj.callback_query.delete_message()
            except Exception:
                pass
        except Exception as e:
            # fallback: просто отправим текст
            await update_obj.callback_query.edit_message_text(analysis_text)
    else:
        # если вызвано из message
        await update_obj.message.reply_photo(photo=img_bio, caption=analysis_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# ----- Основная функция запуска -----
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ MindBot запущен. Нажми Ctrl+C, чтобы остановить.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
