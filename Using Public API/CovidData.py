import requests
import json
import re
from pytz import timezone
from typing import Any, MutableSequence
from urllib.parse import urlencode, quote_plus, unquote
from urllib.request import Request, urlopen
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from lxml import html, etree
import xml.etree.ElementTree as et
from xml.dom import minidom 

class openDataAPICall(object):
    def __init__(self,apiKey) -> None:
        self.apiKey = apiKey
        self.apiURL = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'
    
    def buildRequests(self) -> bool: 
        # 코드 실행한 시점
        executedPoint = datetime.now(timezone('Asia/Seoul'))
        endDate = executedPoint + timedelta(days = 1)# 하루뒤의 시간을 의미한다.
        executedPoint = executedPoint + timedelta(days = -1)
        #시작범위
        searchStart = executedPoint.strftime("%Y%m%d") # strftime으로 포맷을 맞추어준다."%Y%m%d" : YYYYMMDD형태로 출력
        #끝범위
        searchEnd = endDate.strftime("%Y%m%d") # 끝범위를 다음날로 해줘야 오늘 날짜에 대한 값만 나온다.

        #Request Query를 만든다.
        queryParameter = '?' + urlencode({
            quote_plus('serviceKey') : self.apiKey,
            quote_plus('pageNo') : 1,
            quote_plus('numOfRows') : 10,
            quote_plus('startCreateDt') : searchStart,
            quote_plus('endCreateDt') : searchEnd
        })
        response = requests.get(self.apiURL + queryParameter) # 기본적으로 requests를 인코딩한 반환값은 Byte String이 나오게 된다.
        responseXML = response.text
        responseCode = response.status_code
        if 200 <= responseCode < 300:
            res = BeautifulSoup(responseXML, 'lxml-xml')
            return self.reProcessXML(res)
        else:
            return False
    def addMainNews(self) -> MutableSequence:
        covidSite = "http://ncov.mohw.go.kr/index.jsp"
        covidNotice = "http://ncov.mohw.go.kr"
        html = urlopen(covidSite)
        bs = BeautifulSoup(html, 'html.parser')
        # Bug fix 2021 03 02 : 파싱 구역 지정을 조금 더 구체화하였습니다 -> 카드 뉴스로 인한 방해
        bs = bs.find('div',{'class' : 'm_news'})
        sounds = []
        briefTasks = dict()
        hotIssues = dict()
        mainbrief = bs.findAll('a',{'href' : re.compile('\/tcmBoardView\.do\?contSeq=[0-9]*')})
        for brf in mainbrief:
            briefTasks[brf.text] = covidNotice + brf['href']
        sounds.append(briefTasks)
        hotIssue = bs.findAll('a',{'href' : re.compile('https\:\/\/www\.korea\.kr\/[\w?=]+')})
        for u in hotIssue:
            hotIssues[u.text] = u['href']
        sounds.append(hotIssues)
        return sounds
    
    def reProcessXML(self,BSXML : BeautifulSoup) -> bool:
        # 만약 XML파싱 시에 오류가 나는 경우 -> API점검 혹은 아직 불러오지 못한 경우
        try:
            res = BSXML# lxml-xml 매우빠르고 유일하게 지원되는 XML파서이다.
            item = res.findAll('item')
            dayBefore = item[1]
            today = item[0]
            news = self.addMainNews()
        except BaseException:
            return False
    
        # 브리핑 관련 데이터
        briefings = news[0]
        briefTopics = list(briefings.keys())
        #주요 이슈관련 데이터
        hotIssues = news[1]
        issueTopics = list(hotIssues.keys())
        
        dataDictionary = {
            'dataDate' : datetime.strptime(today.find('stateDt').text,"%Y%m%d").date().strftime("%Y-%m-%d"),
            'data' : {
                'totalDecidedPatient' : today.find('decideCnt').text,
                'todayDecidedPatient' : str(int(today.find('decideCnt').text) - int(dayBefore.find('decideCnt').text)),
                'clearedPatient' : today.find('clearCnt').text,
                'totalDeath' : today.find('deathCnt').text,
                'increasedDeath' : str(int(today.find('deathCnt').text) - int(dayBefore.find('deathCnt').text)),
                'CumulatedConfirmPercentage' : today.find('accDefRate').text 
            },
            'briefing' : {},
            'hotIssue' : {}
        }
        for i,o in enumerate(briefTopics, start = 1):
            dataDictionary['briefing']['briefTopics{}'.format(i)] = [o , briefings[o]]
        for i,o in enumerate(issueTopics, start = 1):
            dataDictionary['hotIssue']['issueTopics{}'.format(i)] = [o , hotIssues[o]]
        return dataDictionary

if __name__=="__main__":
    p = openDataAPICall()
    print(p.buildRequests())
