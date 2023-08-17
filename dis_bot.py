import discord, string, time, json, sqlite3, os
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')

censura = {'мат'}

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
    global db, cursor
    print("Бот запущен")
    db = sqlite3.connect('DataBase.db')
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS warning(
                        user_id INT,
                        count INT,
                        role TEXT
                    )''')
    db.commit()
    if db:
        print('DataBase connected .... OK')


@bot.command()
async def stop(ctx):
    global db
    db.close()
    print('DataBase disconnected .... OK')


@bot.command()
async def HB(ctx):
    author = ctx.message.author
    await ctx.send(f"{author}!\nС днем рождения!!!")
    time.sleep(60)
    await HB(ctx)

@bot.command()
async def test(ctx):
    await ctx.send(f"Здравствуйте! \n Это тест!")

@bot.command()
async def info(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def dialog(ctx, *, arg):
    await ctx.send(arg)


@bot.command()
async def dialog2(ctx, arg=None):
    author = ctx.message.author
    if arg == None:
        await ctx.send(f"{author}, Здравствуйте!")
    elif arg == "команды":
        await ctx.send(f"{author.mention}, у меня есть следующие команды:\n- !dialog\n- !info\n- !test")


@bot.event
async def on_message(message):
    global cursor, db
    # if "дела" in message.content.lower():
    #     await message.channel.send('хорошо')
    text = {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')}
    bad_words = text.intersection(set(json.load(open('censorship.json'))))
    if bad_words != set():
        number = message.author.id
        warnings = cursor.execute('''SELECT count FROM warning
                                            WHERE user_id == ?''', (number,)).fetchone()
        if warnings is None:
            cursor.execute(f"INSERT INTO warning VALUES ({number}, 1, 'talk')")
            warnings = 1
        else:
            cursor.execute(f"UPDATE warning SET count = count + 1 WHERE user_id = {number}")
            warnings = warnings[0] + 1
        # cursor.execute('SELECT * FROM warning')
        # print(cursor.fetchall())
        db.commit()
        await message.channel.send(f'{message.author.mention}, ругаться нельзя! Это ваше {warnings} предупреждение!')
        if warnings == 3:
            await message.author.ban(reason='Нецензурная лексика')
        await message.delete()
    await bot.process_commands(message)


@bot.command()
async def clear_db(ctx):
    global db, cursor
    cursor.execute("DELETE FROM warning")
    cursor.execute('SELECT * FROM warning')
    print(cursor.fetchall())
    db.commit()


@bot.command()
async def status(ctx):
    user_id = ctx.message.author.id
    warnings = cursor.execute(f'SELECT count FROM warning WHERE user_id = {user_id}').fetchone()
    if warnings is None:
        await ctx.send(f'{ctx.message.author}, у вас нет предупреждений, вы молодец!')
    else:
        warnings = warnings[0]
        await ctx.send(f'{ctx.message.author}, у вас {warnings} предупреждений!')


@bot.command()
async def mstatus(ctx, member: discord.Member):
    warnings = cursor.execute(f'SELECT count FROM warning WHERE user_id = {member.id}').fetchone()
    if warnings is None:
        await ctx.send(f'{ctx.message.author.mention}, у вас нет предупреждений, вы молодец!')
    else:
        warnings = warnings[0]
        await ctx.send(f'{ctx.message.author.mention}, у вас {warnings} предупреждений!')


@bot.command()
async def test3(ctx):
    await ctx.author.send("Hello word!")


@bot.command()
async def test4(ctx, member: discord.Member):
    await member.send(f"{member.name}, привет от {ctx.author.name}")


@bot.command()
@commands.has_permissions(administrator=True)
async def test5(ctx, amount=1):
    await ctx.channel.purge(limit=amount)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member):
    mute = discord.utils.get(member.guild.roles, name='Mute')
    talk = discord.utils.get(member.guild.roles, name='Talk')
    await member.add_roles(mute)
    await member.remove_roles(talk)
    await ctx.send(f'{member.mention}, бан в виде потери речи')
    await member.send(f'Вы заблокированы на сервере {ctx.guild.name} для разговора')


@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mute = discord.utils.get(member.guild.roles, name='Mute')
    talk = discord.utils.get(member.guild.roles, name='Talk')
    await member.add_roles(talk)
    await member.remove_roles(mute)
    await ctx.send(f'{member.mention}, вы снова в сердце сервера!')
    await member.send(f'Вы разблокированы на сервере {ctx.guild.name} для разговора')


@bot.command()
async def test55(ctx, amount=1):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.channel.purge(limit=amount)


@bot.command()
async def test6(ctx):
    await ctx.channel.purge(limit=1)
    await ctx.send(f'{ctx.message.author}, привет )))')


# Приветствие пользователя в ЛС при присоединении к серверу
@bot.event
async def on_member_join(member):
    await member.send("Добро пожаловать на наш сервер!")
    user_id = member.id
    check = cursor.execute(f'SELECT check FROM warning WHERE user_id = {user_id}').fetchone()
    if check is None:
        cursor.execute(f"INSERT INTO warning VALUES ({user_id}, 0, 'talk')")
        talk = discord.utils.get(member.guild.roles, name='Talk')
        await member.add_roles(talk)
    elif check[2] == "talk":
        talk = discord.utils.get(member.guild.roles, name='Talk')
        await member.add_roles(talk)
    elif check[2] == 'mute':
        mute = discord.utils.get(member.guild.roles, name='Mute')
        await member.add_roles(mute)


# Приветствие пользователя в общем чате при присоединении к серверу
@bot.event
async def on_member_join(member):
    for channel in bot.get_guild(member.guild.id).channels:
        if channel.name == 'основной':
            await bot.get_channel(channel.id).send(f'{member.name}, приветствуем тебя на канале!')


# Прощание с пользователем в общем чате при удалении от сервера
@bot.event
async def on_member_remove(member):
    for channel in bot.get_guild(member.guild.id).channels:
        if channel.name == 'основной':
            await bot.get_channel(channel.id).send(f'{member.name}, будем ждать твоего возвращения!')


bot.run(TOKEN)
