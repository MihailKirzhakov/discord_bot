import discord
import os
from discord.ext import commands


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    """
    Эта функция сигнализирует об удачном запуске бота на сервере
    """
    print('Работаю!')


@bot.event
async def on_message(message):
    """
    Эта функция обрабатывает и реагирует на сообщения в чате.
    Если слова совпадают, то бот отреагирует на это сообщение
    """
    author = message.author.mention
    if 'с переходом в гильдию' in message.content:
        await message.channel.send(
            f'Я снес твоё сообщение, {author}!'
            f' Искать новых соКП иди в мир чат!'
            f' Будешь продолжать спамить, СтопарьВодяры тебя забанит!'
        )
        await message.delete()
    await bot.process_commands(message)


@bot.command()
async def test(ctx):
    """
    Эта функция выведет в чат сообщение о том, что бот работает
    если запустить функцию !test
    """
    await ctx.send('Бот Online')


@bot.command()
async def who_asks(ctx):
    """
    Эта функция, при вводе команды who_asks тэгнет
    того, кто вызывает бота с помощью этой функции
    """
    author = ctx.message.author.mention
    await ctx.send(f'{author} вызвал бота!')


class MyView(discord.ui.View):
    @discord.ui.button(label='Нажми меня', style=discord.ButtonStyle.green)
    async def button_callback(self, interaction, button):
        await interaction.response.send_message('Ты нажал кнопку')

    @discord.ui.button(label='Нажми меня', style=discord.ButtonStyle.blurple)
    async def button_stop_callback(self, interaction, button):
        button.disabled = True
        button.label = 'Конечная'
        await interaction.response.edit_message(view=self)


@bot.command()
async def button(ctx):
    await ctx.send('Нажми меня', view=MyView())


bot.run(os.getenv('TOKEN'))
