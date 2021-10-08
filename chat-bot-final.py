import random
import nltk
import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

with open(r'BOT_CONFIG.json', 'r', encoding='UTF8') as f:
  BOT_CONFIG = json.load(f)


  def clean(text):
    text = text.lower()
    cleaned_text = ''
    for ch in text:
      if ch in r'абвгдеёжзийклмнопрстуфхцчшщъыьэюя ':
        cleaned_text = cleaned_text + ch
    return cleaned_text


  def get_intent(text):
    for intent in BOT_CONFIG['intents'].keys():
      for example in BOT_CONFIG['intents'][intent]['examples']:
        w1 = clean(example)
        w2 = clean(text)
        if nltk.edit_distance(w1, w2) / max(len(w1), len(w2)) < 0.4:
          return intent
    return 'интент не найден'


  X = []
  y = []

  for intent in BOT_CONFIG['intents'].keys():
    try:
      for example in BOT_CONFIG['intents'][intent]['examples']:
        X.append(example)
        y.append(intent)
    except:
      pass

  len(X), len(y), len(set(y))

  X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)
  len(X_train), len(X_test)

  vectorizer = CountVectorizer(preprocessor=clean, analyzer='char', ngram_range=(2, 3))
  X_train_vect = vectorizer.fit_transform(X_train)
  X_test_vect = vectorizer.transform(X_test)

  len(vectorizer.get_feature_names())

  log_reg = LogisticRegression(C=0.2)
  log_reg.fit(X_train_vect, y_train)
  log_reg.score(X_train_vect, y_train)


  log_reg.score(X_test_vect, y_test)


  def get_intent_by_model(text):
    return log_reg.predict(vectorizer.transform([text]))[0]


  def bot(question):
    intent = get_intent_by_model(question)
    return random.choice(BOT_CONFIG['intents'][intent]['responses'])


  logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
  )

  logger = logging.getLogger(__name__)


  def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
      fr'Hi {user.mention_markdown_v2()}\!',
      reply_markup=ForceReply(selective=True),
    )


  def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


  def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    question = update.message.text
    try:
      answer = bot(question)
    except:
      answer = 'Извините, что-то сломалось =('

    update.message.reply_text(answer)


  def main():
    """Start the bot."""
    updater = Updater("1970459957:AAErtM8pgtUeWetFt6S9BJQmX4sdff6eQfY")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()
  main()