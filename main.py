import requests
from bs4 import BeautifulSoup
import telebot

API_KEY = '6029491691:AAFchAuoZT3OVTy4aSI_6ntVSnI7JxVaGWk'
bot = telebot.TeleBot(API_KEY)


def is_start(message):
  return message.text == '/start'


@bot.message_handler(func=is_start)
def welcome(message):
  bot.send_message(
    message.chat.id,
    "Welcome to GitHub bot.\nUse /info command to get general information about user\nUse /repo command to get repositories of the user"
  )


def is_info(message):
  request = message.text.split()
  if len(request) < 2 or request[0] != "/info":
    return False
  else:
    return True


@bot.message_handler(func=is_info)
def send_info(message):
  user = message.text.split()
  url = 'https://github.com/' + user[1]
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'lxml')
  name = soup.find('span', itemprop='name')
  if name is None:
    bot.send_message(message.chat.id, 'No user with provided name exist')
  else:
    name = name.text.strip()
    if (len(name) == 0):
      name = "Name is not available"
    nick = soup.find('span', itemprop='additionalName').text.strip()
    repos = soup.find('span', class_='Counter').text.strip()
    follows = soup.find_all('span', class_='text-bold color-fg-default')
    if (len(follows) == 0):
      followers = '0'
      following = '0'
    else:
      followers = follows[0].text.strip()
      following = follows[1].text.strip()
    about = soup.find(
      'div',
      class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").text.strip(
      )
    if (len(about) == 0):
      about = 'Bioghraphy is not available'
    mes = 'Name: ' + name + '\nUser name: ' + nick + '\nRepositories amount: ' + repos + '\nFollowers: ' + followers + '\nFollowing: ' + following + '\nBio: ' + about + '\nLink: ' + url
    bot.send_message(message.chat.id, mes)


def is_repos(message):
  request = message.text.split()
  if len(request) < 2 or request[0] != "/repo":
    return False
  else:
    return True


@bot.message_handler(func=is_repos)
def get_repos(message):
  user = message.text.split()
  url = 'https://github.com/' + user[1] + '?tab=repositories'

  def send_repos(url, i):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    repos = soup.find_all('a', itemprop="name codeRepository")
    for repo in repos:
      i = i + 1
      mes = str(i) + ': ' + repo.text.strip(
      ) + "- " + 'https://github.com' + repo.get('href')
      bot.send_message(message.chat.id, mes)

    if i == 0:
      bot.send_message(message.chat.id,
                       'No repositories or the given URL is incorrect')

    next = soup.find_all('a', class_='next_page')
    if len(next) > 0:
      send_repos('https://github.com/' + next[0].get('href'), i)

  send_repos(url, 0)


bot.polling()
