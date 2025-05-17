from contextlib import nullcontext
from types import new_class

import discord
import asyncio
import os
import json
import random
from collections import defaultdict

d6msg_ids = defaultdict(set)
d10msg_ids = defaultdict(set)
d12msg_ids = defaultdict(set)
md6msg_ids = defaultdict(set)
md10msg_ids = defaultdict(set)
md12msg_ids = defaultdict(set)
resultadoMsg_ids = defaultdict(set)
usado = 0;
musado = 0;
resultado_id = None
msg_user = None

# Carregar o token do arquivo config.json
with open('config.json', 'r') as f:
    config = json.load(f)
COR =0x690FC3
TOKEN = config.get("DISCORD_TOKEN")

# Definindo intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

def interpretar_resultado(valor):
    """Função para interpretar o resultado do dado para assimilação."""
    if valor in [1, 2]:
        return f"{valor} = Nada ❌"
    elif valor == 3:
        return f"{valor} = 1 Pressão 🦉"
    elif valor in [4, 5]:
        return f"{valor} = 1 Pressão 🦉 e 1 Adaptação 🫎"
    elif valor == 6:
        return f"{valor} = 1 Sucesso 🐞"
    elif valor == 7:
        return f"{valor} = 2 Sucessos 🐞🐞"
    elif valor == 8:
        return f"{valor} = 1 Sucesso 🐞 e 1 Adaptação 🫎"
    elif valor == 9:
        return f"{valor} = 1 Sucesso 🐞, 1 Adaptação 🫎 e 1 Pressão 🦉"
    elif valor == 10:
        return f"{valor} = 2 Sucessos 🐞🐞 e 1 Pressão 🦉"
    elif valor == 11:
        return f"{valor} = 1 Sucesso 🐞, 2 Adaptações 🫎🫎 e 1 Pressão 🦉"
    elif valor == 12:
        return f"{valor} = 2 Pressões 🦉🦉"
    else:
        return f"{valor} = Resultado inválido 🚫"


@client.event
async def on_ready():
    print('Bot Online - Olá Mundo! :3')
    print(client.user.name)
    print(client.user.id)
    print('--------------------------')

@client.event
async def on_message(message):

    #global resultado_id
    if message.content == '?help':
        embedhelp = discord.Embed(
            title="Comandos",
            color=COR,
            description="- ?dados = Uso padrão para jogadores, \n"
                        "   disponibiliza 3 mensagens aonde o jogador\n"
                        "   pode interagir reagindo para rodar dados\n"
                        "   escolhendo a quantidade e o tipo de dado \n"
                        "   a ser rolado, recebendo então o resultado\n\n"
                        "- ?mestre = Uso do mestre, mostra uma mensagem\n"
                        "   aonde o mestre pode interagir para controlar\n"
                        "   conflito. pode alterar a quantidade de dados\n"
                        "   assim como rodar eles. tambem pode usar os\n"
                        "   Sucessos, Aptidões e Pressões obtidos\n\n"
                        "- ?help = Lista os comandos do bot\n\n"
                        "- ?clear = Apaga os IDs das mensagens do chat em\n"
                        "   que foi usado, para limpar espaço na memória\n",)

        await message.channel.send(embed=embedhelp)

    if message.content == '?test':
        await message.channel.send('Bot Funcionando')

    if message.content == '?reset':
        print(message.author.name)
        if message.author.name == 'mas_sam':
            await message.channel.send('Excluindo IDs das mensagens...')
            d6msg_ids.clear()
            d10msg_ids.clear()
            d12msg_ids.clear()
            resultadoMsg_ids.clear()
            await message.channel.send("Todos os IDs foram resetados!")
        else:
            await message.channel.send("Você não tem permissão para isso")

    if message.content == '?clear':
        await message.channel.send('Excluindo IDs das mensagens desse canal...')
        guild_id = message.guild.id
        d6msg_ids[guild_id].clear()
        d10msg_ids[guild_id].clear()
        d12msg_ids[guild_id].clear()
        await message.channel.send("Todos os IDs desse canal foram resetados!")

    if message.content == '?mestre':
        global musado
        musado += 1
        print(f"?mestre foi usado {musado} vezes após a inicialização")

        embedM4 = discord.Embed(
            title="Area do Mestre",
            color=COR,
            description=
            ":game_die: = Rodar dados selecionados\n"
            ":six: = Acrescentar 1 d6\n"
            ":keycap_ten: = Acrescentar 1 d10\n"
            ":two: = Acrescentar 1 d12\n"
            ":x: = Zerar dados\n"
            "----------------------------------------------\n"
            ":lady_beetle: = Gastar um uso de sucesso\n"
            ":moose: = Gastar um uso de adaptação\n"
            ":owl: = Gastar um uso de Pressão\n"
            ":heart: = Aumentar 1 sucesso dos jogadores"
        )
        embedM4.add_field(name="D12 a rolar", value=0, inline=True)
        embedM4.add_field(name="D10 a rolar", value=0, inline=True)
        embedM4.add_field(name="D6 a rolar", value=0, inline=True)
        embedM4.add_field(name="Adaptações :moose:", value=0, inline=True)
        embedM4.add_field(name="Sucessos :lady_beetle:", value=0, inline=True)
        embedM4.add_field(name="Pressões :owl:", value=0, inline=True)
        embedM4.add_field(name="Sucesso obtido pelos players  :heart:", value=0, inline=False)

        resultadoMsg = await message.channel.send(embed=embedM4)

        guild_id = message.guild.id
        resultadoMsg_ids[guild_id].add(resultadoMsg.id)

        for emojim in ['🎲', '🫎', '🐞', '🦉', '❤️','6️⃣','🔟','🔢','❌']:
            await resultadoMsg.add_reaction(emojim)

           # ////////////////////              ? dados

    if message.content == '?dados':
        global usado
        usado +=1
        print(f"?dados foi usado {usado} vezes após a inicialização")

        embed1 = discord.Embed(
            title="Dados D6",
            color=COR,
            description="- 1d6 = :one: \n"
                        "- 2d6  = :two: \n"
                        "- 3d6  = :three:\n"
                        "- 4d6  = :four: \n"
                        "- 5d6  = :five: \n", )

        embed2 = discord.Embed(
            title="Dados d10",
            color=COR,
            description="- 1d10 = :one: \n"
                        "- 2d10  = :two: \n"
                        "- 3d10  = :three:\n"
                        "- 4d10  = :four: \n"
                        "- 5d10  = :five: ", )

        embed3 = discord.Embed(
            title="Dados d12",
            color=COR,
            description="- 1d12 = :one: \n"
                        "- 2d12  = :two: \n"
                        "- 3d12  = :three:\n"
                        "- 4d12  = :four: \n"
                        "- 5d12  = :five: ", )

        d12msg = await message.channel.send(embed=embed3)
        d6msg = await message.channel.send(embed=embed1)
        d10msg = await message.channel.send(embed=embed2)

        guild_id = message.guild.id
        d6msg_ids[guild_id].add(d6msg.id)
        d10msg_ids[guild_id].add(d10msg.id)
        d12msg_ids[guild_id].add(d12msg.id)

        for emoji in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']:
            await d6msg.add_reaction(emoji)
            await d10msg.add_reaction(emoji)
            await d12msg.add_reaction(emoji)

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user or not reaction.message.guild:
        return

    guild_id = reaction.message.guild.id
    emoji_map = {
        '1️⃣': 1,
        '2️⃣': 2,
        '3️⃣': 3,
        '4️⃣': 4,
        '5️⃣': 5
    }
    emojim_map = {
        '🎲': 1,
        '🫎': 2,
        '🐞': 3,
        '🦉': 4,
        '❤️': 5,
        '6️⃣': 6,
        '🔟': 7,
        '🔢': 8,
        '❌': 9
    }

    if reaction.emoji not in emoji_map:
        if reaction.emoji not in emojim_map:
            return
        else: # emoji ta no emoji de mestre
            if reaction.message.id in resultadoMsg_ids[guild_id]:
                opc = emojim_map[reaction.emoji]
                canal = reaction.message.channel
                mensagem = await canal.fetch_message(reaction.message.id)
                embed = mensagem.embeds[0]  #define a embed

                # pega as info do campo e joga nas variavel
                d12_valor = int(embed.fields[0].value)
                d10_valor = int(embed.fields[1].value)
                d6_valor = int(embed.fields[2].value)
                adp_valor = int(embed.fields[3].value)
                suc_valor = int(embed.fields[4].value)
                pre_valor = int(embed.fields[5].value)
                playerSuc_valor = int(embed.fields[6].value)

                match opc:
                    case 1: # rodar os dados
                        rolagem = [[], [], []]
                        if d6_valor > 0: rolagem[0] = [random.randint(1, 6) for _ in range(d6_valor)]
                        if d10_valor > 0:rolagem[1] = [random.randint(1, 10) for _ in range(d10_valor)]
                        if d12_valor > 0:rolagem[2] = [random.randint(1, 12) for _ in range(d12_valor)]
                        for lista in rolagem:
                            for valor in lista:
                                if valor in [1, 2]:
                                    adp_valor += 0
                                elif valor == 3:
                                    pre_valor += 1
                                elif valor in [4, 5]:
                                    pre_valor += 1
                                    adp_valor += 1
                                elif valor == 6:
                                    suc_valor += 1
                                elif valor == 7:
                                    suc_valor += 2
                                elif valor == 8:
                                    suc_valor += 1
                                    adp_valor += 1
                                elif valor == 9:
                                    suc_valor += 1
                                    adp_valor += 1
                                    pre_valor += 1
                                elif valor == 10:
                                    suc_valor += 2
                                    pre_valor += 1
                                elif valor == 11:
                                    suc_valor += 1
                                    adp_valor += 2
                                    pre_valor += 1
                                elif valor == 12:
                                    pre_valor += 2
                                else:
                                    return

                    case 2: # -1 adaptacao
                        if adp_valor > 0: adp_valor -= 1
                    case 3: # -1 sucesso
                        if suc_valor > 0: suc_valor -= 1
                    case 4: # -1 pressao
                        if pre_valor > 0: pre_valor -= 1
                    case 5: # +1 de vida do bixo
                        playerSuc_valor += 1
                    case 6:  # +1d6
                        d6_valor +=1
                    case 7:  # +1d10
                        d10_valor += 1
                    case 8:  # +1d12
                        d12_valor +=1
                    case 9:  # apaga todos os dados
                        d6_valor = 0
                        d10_valor = 0
                        d12_valor = 0
                    case _: # erro
                        print("Valor invalido na rolagem do mestre")

                embed_editada = discord.Embed(
                    title="Área do Mestre",
                    color=COR,
                    description=
                    ":game_die: = Rodar dados selecionados\n"
                    ":six: = Acrescentar 1 d6\n"
                    ":keycap_ten: = Acrescentar 1 d10\n"
                    ":two: = Acrescentar 1 d12\n"
                    ":x: = Zerar dados\n"
                    "----------------------------------------------\n"
                    ":lady_beetle: = Gastar um uso de sucesso\n"
                    ":moose: = Gastar um uso de adaptação\n"
                    ":owl: = Gastar um uso de Pressão\n"
                    ":heart: = Aumentar 1 sucesso dos jogadores"
                )
                embed_editada.add_field(name="D12 a rolar", value=d12_valor, inline=True)
                embed_editada.add_field(name="D10 a rolar", value=d10_valor, inline=True)
                embed_editada.add_field(name="D6 a rolar", value=d6_valor, inline=True)
                embed_editada.add_field(name="Adaptações :moose:", value=adp_valor, inline=True)
                embed_editada.add_field(name="Sucessos :lady_beetle:", value=suc_valor, inline=True)
                embed_editada.add_field(name="Pressões :owl:", value=pre_valor, inline=True)
                embed_editada.add_field(name="Sucesso obtido pelos players   :heart:", value=playerSuc_valor, inline=False)

                await reaction.message.edit(embed=embed_editada)
                await reaction.message.remove_reaction(reaction.emoji, user)

    else: # emoji ta no emoji de dados
        qtd_dados = emoji_map[reaction.emoji]

        if reaction.message.id in d6msg_ids[guild_id]:
            resultados = [random.randint(1, 6) for _ in range(qtd_dados)]
            titulo = "Dados D6"

        elif reaction.message.id in d10msg_ids[guild_id]:
            resultados = [random.randint(1, 10) for _ in range(qtd_dados)]
            titulo = "Dados D10"

        elif reaction.message.id in d12msg_ids[guild_id]:
            resultados = [random.randint(1, 12) for _ in range(qtd_dados)]
            titulo = "Dados D12"

        else:
            return  # Não é uma mensagem reconhecida

        resultados_interpretados = [interpretar_resultado(valor) for valor in resultados]
        resultado_final = "\n".join(resultados_interpretados)

        embed_editada = discord.Embed(
            title=titulo,
            color=discord.Color.green(),
            description=(
                "- 1 = :one:\n"
                "- 2 = :two:\n"
                "- 3 = :three:\n"
                "- 4 = :four:\n"
                "- 5 = :five:\n\n"
                f"**{user.mention} rodou {qtd_dados} dados e tirou:**\n{resultado_final}"
            )
        )
        await reaction.message.edit(embed=embed_editada)
        await reaction.message.remove_reaction(reaction.emoji, user)

client.run(TOKEN)
