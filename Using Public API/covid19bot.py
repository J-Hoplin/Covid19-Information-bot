import discord
import asyncio
import os
import yaml
from discord.ext import commands
import urllib
from urllib.request import URLError, HTTPError, urlopen, Request
from bs4 import BeautifulSoup
from urllib.parse import quote
import re # Regex for youtube link
import warnings
import requests
import time
from CovidData import openDataAPICall

with open('config.yml') as f:
    keys = yaml.load(f, Loader=yaml.FullLoader)

client = discord.Client() # Create Instance of Client. This Client is discord server's connection to Discord Room
bottoken = keys['Keys']['discordAPIToken']
getCovidData = openDataAPICall(keys['Keys']['publickey'])

@client.event # Use these decorator to register an event.
async def on_ready(): # on_ready() event : when the bot has finised logging in and setting things up
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Type !help or !도움말 for help"))
    print("New log in as {0.user}".format(client))

@client.event
async def on_message(message): # on_message() event : when the bot has recieved a message
    #To user who sent message
    # await message.author.send(msg)
    if message.author == client.user:
        return
    if message.content.startswith("!코로나"):
        APIResult = getCovidData.buildRequests()
        if not APIResult:
            embed = discord.Embed(title="Covid-19 Virus Korea Status : 아직 업데이트 되지 않음", description="",color=0x5CD1E5)
            embed.add_field(name="Data source : 공공데이터 포털(data.go.kr) API", value="API정보 : 공공데이터활용지원센터_보건복지부 코로나19 감염 현황", inline=False)
            embed.add_field(name="금일 정보가 아직 업데이트 되지 않았습니다!", value="아직 최신정보를 불러오지 못하였습니다. 평균 업데이트 시간은 오전 10시에서 11시사이입니다.", inline=False)
            embed.add_field(name="다음과 같은 이유로 불러오지 못할 수 도 있습니다", value="1. API 점검 기간\n2. 로직 내 버그\n3. API 일일호출 초과\n* 이러한 경우 운영자에게 문의해주시기 바랍니다.", inline=False)
            embed.add_field(name="중앙방역대책본부 코로나감염증 홈페이지 접속하기",value="http://ncov.mohw.go.kr/index.jsp",inline=False)
            embed.set_thumbnail(url="https://wikis.krsocsci.org/images/7/79/%EB%8C%80%ED%95%9C%EC%99%95%EA%B5%AD_%ED%83%9C%EA%B7%B9%EA%B8%B0.jpg")
            embed.set_footer(text='Service provided by Hoplin.',icon_url='https://avatars2.githubusercontent.com/u/45956041?s=460&u=1caf3b112111cbd9849a2b95a88c3a8f3a15ecfa&v=4')
            
        else:
            embed = discord.Embed(title="Covid-19 Virus Korea Status", description="",color=0x5CD1E5)
            embed.add_field(name="Data source : 공공데이터 포털(data.go.kr) API", value="API정보 : 공공데이터활용지원센터_보건복지부 코로나19 감염 현황", inline=False)
            embed.add_field(name="Latest data refred time",value= f"해당 자료는 {APIResult['dataDate'].split('-')[0]}년 {APIResult['dataDate'].split('-')[1]}월 {APIResult['dataDate'].split('-')[2]}일 자료입니다", inline=False)
            embed.add_field(name="전체 확진환자", value=f"{APIResult['data']['totalDecidedPatient']}명",inline=True)
            embed.add_field(name="신규 확진자", value=f"{APIResult['data']['todayDecidedPatient']}명",inline=True)
            embed.add_field(name="완치환자(격리해제)", value=f"{APIResult['data']['clearedPatient']}명", inline=True)
            embed.add_field(name="전체 사망자", value=f"{APIResult['data']['totalDeath']}명", inline=True)
            embed.add_field(name="신규 사망자", value=f"{APIResult['data']['increasedDeath']}명", inline=True)
            embed.add_field(name="누적확진률", value=f"{APIResult['data']['CumulatedConfirmPercentage']}", inline=True)
            briefKeys = list(APIResult['briefing'].keys())
            newsKeys = list(APIResult['hotIssue'].keys())
            for i in range(len(briefKeys)):
                embed.add_field(name=f"- 최신 브리핑 {i + 1} : {APIResult['briefing'][briefKeys[i]][0]}",value = f"Link : {APIResult['briefing'][briefKeys[i]][1]}",inline=False)
            for i in range(len(newsKeys)):
                embed.add_field(name=f"- 메인 뉴스 {i + 1} : {APIResult['hotIssue'][newsKeys[i]][0]}",value = f"Link : {APIResult['hotIssue'][newsKeys[i]][1]}",inline=False)
            embed.set_thumbnail(url="https://wikis.krsocsci.org/images/7/79/%EB%8C%80%ED%95%9C%EC%99%95%EA%B5%AD_%ED%83%9C%EA%B7%B9%EA%B8%B0.jpg")
            embed.set_footer(text='Service provided by Hoplin.',
                         icon_url='https://avatars2.githubusercontent.com/u/45956041?s=460&u=1caf3b112111cbd9849a2b95a88c3a8f3a15ecfa&v=4')
        await message.channel.send("Covid-19 Virus Korea Status", embed=embed)
client.run(bottoken)
