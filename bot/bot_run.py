import discord
import os
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()

# debug_guilds=[1214866204309725244]
bot = discord.Bot(debug_guilds=[1214866204309725244])


@bot.event
async def on_ready():
    """
    Эта функция сигнализирует об удачном запуске бота на сервере
    """
    print('Работаю!')


@bot.command()
async def test(ctx: discord.ApplicationContext):
    """
    Эта функция выведет в чат сообщение о том, что бот работает
    если запустить функцию !test
    """
    await ctx.respond('Бот Online')



@bot.command()
async def who_asks(ctx: discord.ApplicationContext):
    """
    Эта функция, при вводе команды who_asks тэгнет
    того, кто вызывает бота с помощью этой функции
    """
    await ctx.respond(f'{ctx.author.mention} вызвал бота!')


class MyView(discord.ui.View):
    """Класс, который является подклассом discord.ui.View"""
    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.blurple)
    # Создаем кнопку с названием "😎 нажми меня!" с цветом blurple
    async def button_callback(self, button, interaction):
        await interaction.response.send_message('You clicked the button!')
        # Отправляем сообщение, когда кнопка была нажата

@bot.slash_command()
# Создаем комманду
async def button(ctx):
    await ctx.respond('This is a button!', view=MyView())
    # Отправляем сообщение с помощью нашего класса View, содержащего кнопку


bot.run(os.getenv('TOKEN'))
