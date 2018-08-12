# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 19:39:40 2018

@author: Zorbin
"""
import urllib
import json
import re
import jieba    #分词包
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy    #numpy计算包
from urllib import request
from bs4 import BeautifulSoup as bs

def inputName():
	print('请输入电影名称：')
	name = input()
	print('正在搜索...')
	url = 'http://api.douban.com//v2/movie/search?q=' + urllib.parse.quote(name)
	resp = request.urlopen(url)
	html_data = resp.read().decode('utf-8')

	soup = bs(html_data, 'html.parser').prettify()
	soupObj = json.loads(soup)
	if not soupObj['subjects']:
		print('没有找到相关电影，请重新搜索')
		return inputName()
	serchReslutList = soupObj['subjects']
	

	resultList = []
	for item in serchReslutList:
		resultList_dict = {}
		resultList_dict['url'] = item['alt']
		resultList_dict['name'] = item['title'] + "(" + item['year'] + ")"
		resultList.append(resultList_dict)

	return resultList

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def inputNum(len):
    choose = input()
    if is_number(choose) == False or int(choose) > len or int(choose) < 1:
        print('输入有误，请重新输入')
        return inputNum(len)

    return choose

def chooseMovie():
    resultList = inputName()
    i = 0
    for value in resultList:
        i += 1
        print(str(i) + "、" + value['name'])
    
    print('请选择电影序号：')
    choose = inputNum(len(resultList))
    print('正在处理...')
    return resultList[int(choose) - 1]

def getComment():
    nowplaying_list = chooseMovie()
    i = 0
    cleaned_comments = ''
    while i < 1000:
    	requrl = nowplaying_list['url'] + '/comments' +'?' +'start='+ str(i) + '&limit=20'
    	try:
    		resp = request.urlopen(requrl) 
    		html_data = resp.read().decode('utf-8') 
    		soup = bs(html_data, 'html.parser') 
    		comment_div_lits = soup.find_all('div', class_='comment')
    
    		eachCommentList = [];
    		for item in comment_div_lits:
    			if item.find_all('span', class_='short')[0].string is not None:
    				eachCommentList.append(item.find_all('span', class_='short')[0].string)
    
    		comments = ''
    		for k in range(len(eachCommentList)):
    			comments = comments + (str(eachCommentList[k])).strip()

    		pattern = re.compile(r'[\u4e00-\u9fa5]+')
    		filterdata = re.findall(pattern, comments)
    		cleaned_comment = ''.join(filterdata)
    
    		cleaned_comments = cleaned_comment + cleaned_comment
    
    		i += 20
    
    	except:
    		break
        
    return cleaned_comments

def segComment():
    cleaned_comments = getComment()
    
    segment = jieba.lcut(cleaned_comments)
    words_df=pd.DataFrame({'segment':segment})
    
    stopwords=pd.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='gb18030')#quoting=3全不引用
    words_df=words_df[~words_df.segment.isin(stopwords.stopword)]
    
    words_stat=words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
    words_stat=words_stat.reset_index().sort_values(by=["计数"],ascending=False)
    
    return words_stat

def wordCloud():
    words_stat = segComment()
    
    matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
    from wordcloud import WordCloud#词云包
    
    #bg_img = plt.imread(**.jpg)
    bg_img = None
    
    wordcloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=80,mask=bg_img) #指定字体类型、字体大小和字体颜色
    word_frequence = {x[0]:x[1] for x in words_stat.head(1000).values}
    
    word_frequence_list = []
    for key in word_frequence:
        temp = (key,word_frequence[key])
        word_frequence_list.append(temp)
    
    wordcloud=wordcloud.fit_words(dict(word_frequence_list))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    wordcloud.to_file('result.png')
    
wordCloud()
