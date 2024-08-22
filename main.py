import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
#API AREA
import time
import requests
import urllib.request
import json
import datetime
import asyncio


TESTING_MODE = True





intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')



@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# !hello
@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")

#/help
@bot.slash_command(name="help", description="顯示指令列表")
async def help(ctx):
    embed=discord.Embed(title="指令列表", description="可用指令:", color=0x00ff00)
    embed.add_field(name="**!hello**", value="跟機器人打招呼", inline=False)
    embed.add_field(name="**/help**", value="顯示此訊息", inline=False)
    embed.add_field(name="**/ping**", value="顯示機器人延遲", inline=False)
    embed.add_field(name="**/invite**", value="獲取機器人邀請連結", inline=False)
    embed.add_field(name="**/hello**", value="跟機器人打招呼", inline=False)
    embed.add_field(name="**/crops [農作物]**", value="查詢指定作物的種類及編號", inline=False)
    embed.add_field(name="**/price [農作物]**", value="查詢指定作物的當日價格", inline=False)
    await ctx.respond(embed=embed)

#/hello
@bot.slash_command(name="hello", description="跟機器人打招呼")
async def hello_slash(ctx):
    await ctx.respond("Hello, world!")

#/invite
@bot.slash_command(name="invite", description="獲取邀請連結")
async def invite_slash(ctx):
    embed=discord.Embed(title="邀請連結", url="https://discord.com/oauth2/authorize?client_id=1275683698754457631&permissions=1759218602344439&integration_type=0&scope=bot", description="Click the title to get link")
    await ctx.respond(embed=embed)
    
#/ping
@bot.slash_command(name="ping", description="檢查機器人延遲")
async def ping_slash(ctx):
    embed=discord.Embed(title="Pong!", description=f"延遲: **{round(bot.latency * 1000)}ms**", color=random.randint(0, 0xffffff))
    await ctx.respond(embed=embed)

#/crops
@bot.slash_command(name="crops", description="顯示指定作物的資訊")
async def crop_slash(ctx, item: str):
    url = f'https://data.moa.gov.tw/api/v1/CropType/?CropName={item}'
    response = requests.get(url)
    data = response.json()
    datas = data['Data']
    if len(data["Data"]) == 0:
        embed=discord.Embed(title="查無此資料", description=f"無法查詢有關**{item}**的資料",color=0xff0000)
        await ctx.respond(embed=embed)
    else:
        embed=discord.Embed(title="查詢結果",description=f"關於**{item}**的查尋結果",color=random.randint(0, 0xffffff))
        for crop in datas:
            embed.add_field(name=f"{crop['CropCode']} - {crop['CropName']}\n", value="",inline=False)
        await ctx.respond(embed=embed)

@bot.slash_command(name="price", description="查詢指定作物的今日價格")
async def price_slash(ctx, item: str):
    now = datetime.datetime.now()
    n_year = now.year - 1911 
    roc_date = now.strftime(f"{n_year}.%m.%d")
    print(f"Date: {roc_date}")
    url = f"https://data.moa.gov.tw/api/v1/AgriProductsTransType/?Start_time={roc_date}&End_time={roc_date}&CropName={item}"
    response = requests.get(url)
    data = response.json()
    datas = data['Data']
    if len(data["Data"]) == 0:
        embed = discord.Embed(title="查無此資料", description=f"無法查詢有關**{item}**的資料",color=0xff0000)
        await ctx.respond(embed=embed)
    else:
        page = 1
        max_page = len(datas) // 5 + (len(datas) % 5 != 0)
        embed = discord.Embed(title=f"**{item}** 價格查詢結果 📊",description=f"關於**{item}**的查尋結果",color=random.randint(0, 0xffffff))
        for i in range((page - 1) * 5, min(page * 5, len(datas))):
            crop = datas[i]
            embed.add_field(
                name=f"**{crop['CropCode']}** - {crop['CropName']}",
                value=f"""
                **市場** [ {crop['MarketCode']} - {crop['MarketName']} ]
                **- 最高價** **{crop['Upper_Price']}** 元 / 公斤
                **- 中間價** **{crop['Middle_Price']}** 元 / 公斤
                **- 最低價** **{crop['Lower_Price']}** 元 / 公斤
                **- 平均價** **{crop['Avg_Price']}** 元 / 公斤
                **- 交易量** **{crop['Trans_Quantity']}** 公斤
                """,
                inline=True
            )
        message = await ctx.respond(embed=embed)
        
        # Add buttons
        view = discord.ui.View(
            discord.ui.Button(label="上一頁", style=discord.ButtonStyle.blurple, emoji="⬅️", disabled=page == 1, custom_id="previous_page"),
            discord.ui.Button(label="下一頁", style=discord.ButtonStyle.blurple, emoji="➡️", disabled=page == max_page, custom_id="next_page")
        )
        await message.edit(view=view)
        
        async def button_callback(interaction):
            nonlocal page
            if interaction.data['custom_id'] == 'previous_page':
                page -= 1
            elif interaction.data['custom_id'] == 'next_page':
                page += 1
            embed = discord.Embed(title=f"**{item}** 價格查詢結果 📊",description=f"關於**{item}**的查尋結果",color=random.randint(0, 0xffffff))
            for i in range((page - 1) * 5, min(page * 5, len(datas))):
                crop = datas[i]
                embed.add_field(
                    name=f"**{crop['CropCode']}** - {crop['CropName']}",
                    value=f"""
                    **- 市場** [ {crop['MarketCode']} - {crop['MarketName']}]
                    **- 最高價** **{crop['Upper_Price']}** 元 / 公斤
                    **- 中間價** **{crop['Middle_Price']}** 元 / 公斤
                    **- 最低價** **{crop['Lower_Price']}** 元 / 公斤
                    **- 平均價** **{crop['Avg_Price']}** 元 / 公斤
                    **- 交易量** **{crop['Trans_Quantity']}** 公斤
                    """,
                    inline=True
                )
            if page == max_page:
                embed.set_footer(text="This is end")
                view.children[1].disabled = True
            await interaction.response.edit_message(embed=embed, view=view)
        
        async def delete_button_callback(interaction):
            await interaction.response.edit_message(embed=None, view=None)
        
        # Add button click listeners
        view.children[0].callback = button_callback
        view.children[1].callback = button_callback
    
            
            
        
    
    






bot.run(os.getenv('token'))