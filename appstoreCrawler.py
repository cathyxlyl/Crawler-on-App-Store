# -*- coding: utf-8-*-

import urllib
import re
import MySQLdb
import traceback
import chardet
import bs4
from bs4 import BeautifulSoup
import datetime

#初始地址  
ini_page="https://itunes.apple.com/cn/genre/ios/id36?mt=8"

#连接数据库
db=MySQLdb.connect(host='localhost',user='root',passwd='123456',db='appstore')
cur=db.cursor()

#打开写入app网页地址和应用信息的文件
f1=open(r'G:\crawl\applist.txt','a')
f2=open(r'G:\crawl\app_data.txt','a')
f3=open(r'G:\crawl\parsepage_error.txt','a')
f4=open(r'G:\crawl\database_error.txt','a')
f5=open(r'G:\crawl\pagelog.txt','a')
f6=open(r'G:\crawl\screen.txt','a')

#初始化applist0
applist0=set()


#载入已爬取过的页面列表
def applist_pre(text=r'G:\crawl\applist\applist1.txt',applist_p=applist0):
    f=open(text,'r')
    for line in f:
        applist_p.add(line[0:-1])
    return applist_p

#applist0=applist_pre(text=r'G:\crawl\applist0.txt',applist_p=applist0)

       
#爬虫函数，只爬取app页面
def crawler(page=ini_page,depth=2,applist=applist0):
    #pagelist为所有页面的链接集，crawledpages为已爬过的页面网址集，applist为app页面网址集
    pagelist=set([page])
    crawledpages=set()
    for i in range(depth):
        newpages=pagelist-crawledpages-applist
        record=str(i)+','+str(datetime.datetime.now())+','+str(len(newpages))
        print(record)
        f6.write(record+'\n')
        if newpages:
            #读入网页html，用BeautifulSoup分析结构
            for page in newpages:
                try:
                    webpage=urllib.urlopen(page)
                except:
                    print('Could not open %s' % page)
                    f6.write('Could not open %s\n' % page)
                    continue
                text=BeautifulSoup(webpage.read())

                #获取html里的链接信息
                links=text('a')
                for link in links:
                    if 'href' in str(link):
                        try:
                            url=str(link['href'].split('#')[0])
                        except:
                            print('Error url for '+url)
                            print(traceback.format_exc())
                            f6.write('Error url for %s\n' % url)
                            f6.write(traceback.format_exc()+'\n')
                        #判断是否为网页,且不在pagelist中
                        if (url[0:4]=='http') and (url not in pagelist):
                            pagelist.add(url)
                            f5.write('new:     '+url+'\n')
                            #判断是否为app页面
                            if url[0:32]=='https://itunes.apple.com/cn/app/':
                                #解析页面
                                if url not in applist:
                                    #print url
                                    applist.add(url)
                                    pageparse(url)
                                    f1.write(url+'\n')
                                    crawledpages.add(url)
                                    f5.write('crawled: '+url+'\n')

                crawledpages.add(page)
                f5.write('crawled: '+page+'\n')


#app页面解析函数,并将数据插入数据库
def pageparse(url):
    iosapp={'ID':[],
            'name':'null',
            'seller':'null',
            'price':'null',
            'category':'null',
            'updated':'null',
            'version':'null',
            'size':'"0"',
            'language':'null',
            'seller_spec':'null',
            'copy_right':'null',
            'limit_grade':'null',
            'compatibility':'null',
            'rating_all':'"0"',
            'ra_amount':'"0"',
            'rating_current':'"0"',
            'rc_amount':'"0"',
            'in_app_purchase':'null',
            'more_app':'null',
            'comment_1':'null',
            'rate_1':'"0"',
            'comment_2':'null',
            'rate_2':'"0"',
            'comment_3':'null',
            'rate_3':'"0"',
            'purchase_also_1':'null',
            'purchase_also_2':'null',
            'purchase_also_3':'null',
            'purchase_also_4':'null',
            'purchase_also_5':'null',
            'content':'null'}
    
    try:
        webpage=urllib.urlopen(url)
    except:
        print('Could not open %s' % url)
        return 0
    text=BeautifulSoup(webpage.read(),from_encoding='utf-8')
  
    try:
        #ID
        url=url[0:url.find('?mt=')]
        ID=url[-9:]
        iosapp['ID']='"'+ID+'"'

        #name
        try:
            name=text.findAll('div',{'class':'left'})[1]('h1')[0].string
            iosapp['name']='"'+str_trans(name)+'"'
        except:
            f3.write(ID+' name:\n'+str(traceback.format_exc())+'\n')

        #seller
        try:
            seller_temp=text.findAll('div',{'class':'left'})[1]('h2')[0].string
            if 'by' in unicode(seller_temp):
                seller=seller_temp[3:]
            elif '开发商'.decode('utf-8') in unicode(seller_temp):
                seller=seller_temp.split('：'.decode('utf-8'))[1]
            else:
                seller=seller_temp
                print('seller error for ID='+ID)
                f3.write(ID+'seller error\n')
            iosapp['seller']='"'+str_trans(seller)+'"'
        except:
            f3.write(ID+' seller:\n'+str(traceback.format_exc())+'\n')
        
        #price
        try:
            price=text.findAll('div',{'class':'price'})[0].string
            iosapp['price']='"'+price+'"'
        except:
            f3.write(ID+' price:\n'+str(traceback.format_exc())+'\n')

        #category
        try:
            category=text.findAll('li',{'class':'genre'})[0]('a')[0].string
            iosapp['category']='"'+category+'"'
        except:
            f3.write(ID+' category:\n'+str(traceback.format_exc())+'\n')

        #updated
        try:
            updated_pri=text.findAll('li',{'class':'release-date'})[0].contents[1]
            updated=str(updated_pri[0:4]+'-'+updated_pri[5:7]+'-'+updated_pri[8:10])
            iosapp['updated']='"'+updated+'"'
        except:
            f3.write(ID+' updated:\n'+str(traceback.format_exc())+'\n')

        #version
        try:
            for item in text('li'):
                if ('版本:'.decode('utf-8') or 'Version:') in unicode(item):
                    version=item.contents[1]
            iosapp['version']='"'+version+'"'
        except:
            f3.write(ID+' version:\n'+str(traceback.format_exc())+'\n')
                
        #size
        try:
            for item in text('li'):
                if ('大小'.decode('utf-8') or 'Size:') in unicode(item):
                    size=float(item.contents[1][0:-2])
            iosapp['size']='"'+str(size)+'"'
        except:
            f3.write(ID+' size:\n'+str(traceback.format_exc())+'\n')

        #language
        try:
            language=text.findAll('li',{'class':'language'})[0].contents[1]
            language=str_trans(language)
            iosapp['language']='"'+language+'"'
        except:
            f3.write(ID+' language:\n'+str(traceback.format_exc())+'\n')
    
        #seller_spec
        try:
            for item in text('li'):
                if ('开发商:'.decode('utf-8') or 'Seller:') in unicode(item):
                    seller_spec=item.contents[1]
            iosapp['seller_spec']='"'+str_trans(seller_spec)+'"'
        except:
            f3.write(ID+' seller_spec:\n'+str(traceback.format_exc())+'\n')

        #copy_right
        try:
            copy_right=text.findAll('li',{'class':'copyright'})[0].string
            iosapp['copy_right']='"'+str_trans(copy_right)+'"'
        except:
            f3.write(ID+' copy_right:\n'+str(traceback.format_exc())+'\n')

        #limit_grade
        try:
            limit_grade=text.findAll('div',{'class':'app-rating'})[0]('a')[0].string
            iosapp['limit_grade']='"'+limit_grade+'"'
        except:
            f3.write(ID+' limit_grade:\n'+str(traceback.format_exc())+'\n')

        #compatibility
        try:
            compatibility=text('p')[-1].contents[1]
            iosapp['compatibility']='"'+str_trans(compatibility)+'"'
        except:
            f3.write(ID+' compatibility:\n'+str(traceback.format_exc())+'\n')

        #rating
        try:  
            rating=text.findAll('div',{'class':'extra-list customer-ratings'})[0].findAll('div',{'class':'rating','role':'img'})
            if len(rating)>=1:
                rating_al=rating[-1]['aria-label']
                iosapp['rating_all']='"'+str(float(rating_al.split(',')[0][0:-1]))+'"' #rating_all
                iosapp['ra_amount']='"'+str(int(rating_al.split(',')[1][1:-4]))+'"' #ra_amount
                if len(rating)==2:
                    rating_curr=rating[-2]['aria-label']
                    iosapp['rating_current']='"'+str(float(rating_curr.split(',')[0][0:-1]))+'"'    #rating_current
                    iosapp['rc_amount']='"'+str(int(rating_curr.split(',')[1][1:-4]))+'"' #rc_amount
        except:
            f3.write(ID+' rating:\n'+str(traceback.format_exc())+'\n')
        
        #in_app_purchase
        try:
            in_app_purchase=text.findAll('div',{'class':'extra-list in-app-purchases'})
            inpur_all=''
            if in_app_purchase:
                for i in range(len(in_app_purchase[0].contents[3].contents)):
                    item=in_app_purchase[0].contents[3].contents[i].contents
                    num=str(i+1)
                    inpur_all+=num+'.'+item[0].string+': '+item[1].string+'; '
                inpur_all=str_trans(inpur_all)
                iosapp['in_app_purchase']='"'+inpur_all+'"'   
            else:
                iosapp['in_app_purchase']='"no in-app-purchases"'
        except:
            f3.write(ID+' in_app_purchase:\n'+str(traceback.format_exc())+'\n')

        #more_app
        try:
            more_app=text.findAll('div',{'class':'extra-list more-by'})
            mapp_all=''
            if more_app:
                for i in range(len(more_app[0].contents[3].contents)):
                    item=more_app[0].contents[3].contents[i].contents
                    num=str(i+1)
                    mapp_all+=num+'.'+item[1]['aria-label']+': '+item[-2].contents[1]['href']+'; '
                iosapp['more_app']='"'+str_trans(mapp_all)+'"'
            else:
                iosapp['more_app']='"no other apps for the seller"'
        except:
            f3.write(ID+' in_app_purchase:\n'+str(traceback.format_exc())+'\n')

        #comment
        try:
            comment=text.findAll('div',{'class':'customer-review'})
            if comment:
                num='0'
                for i in range(min(len(comment),3)):
                    num=str(int(num)+1)
                    title=comment[i].findAll('span',{'class':'customerReviewTitle'})[0].string
                    title=str_trans(title)
                    content_temp=comment[i].findAll('p',{'class':'content'})
                    try:
                        content=content_temp[0].string[5:-3]
                        content=str_trans(content)
                    #处理评论有多行的情况
                    except:
                        content=''.join([item.encode('utf-8') for item in content_temp[0].contents]).strip().strip('\n').decode('utf-8')
                        content=str_trans(content)
                    iosapp['comment_%s' % num]='"'+title+': '+content+'"'
                    rate=float(comment[i].findAll('div',{'class':'rating'})[0]['aria-label'][0:-1])
                    iosapp['rate_%s' % num]='"'+str(rate)+'"'
        except:
            f3.write(ID+' comment:\n'+str(traceback.format_exc())+'\n')


        #purchase_also
        try:
            pur_also=text.findAll('div',{'parental-rating':'1','role':'group'})
            if pur_also:
                num='0'
                for i in range(len(pur_also)):
                    if pur_also[i].parent in text('div'):
                        num=str(int(num)+1)
                        pur_also_id=pur_also[i]['adam-id']
                        pur_also_name=pur_also[i]['aria-label']
                        pur_also_name=str_trans(pur_also_name)
                        iosapp['purchase_also_%s' % num]='"'+pur_also_id+':'+pur_also_name+'"'
        except:
            f3.write(ID+' purchase_also:\n'+str(traceback.format_exc())+'\n')

        value=iosapp['ID']+','+iosapp['name']+','+iosapp['seller']\
               +','+iosapp['price']+','+iosapp['category']+','+iosapp['updated']\
               +','+iosapp['version']+','+iosapp['size']+','+iosapp['language']\
               +','+iosapp['seller_spec']+','+iosapp['copy_right']+','+iosapp['limit_grade']\
               +','+iosapp['compatibility']+','+iosapp['rating_all']+','+iosapp['ra_amount']\
               +','+iosapp['rating_current']+','+iosapp['rc_amount']+','+iosapp['in_app_purchase']\
               +','+iosapp['more_app']+','+iosapp['comment_1']+','+iosapp['rate_1']\
               +','+iosapp['comment_2']+','+iosapp['rate_2']+','+iosapp['comment_3']\
               +','+iosapp['rate_3']+','+iosapp['purchase_also_1']+','+iosapp['purchase_also_2']\
               +','+iosapp['purchase_also_3']+','+iosapp['purchase_also_4']+','+iosapp['purchase_also_5']\
               +','+iosapp['content']
        #print(value)
        f2.write(value.encode('utf-8')+'\n')

    except:
        #print('Parse error for ID='+ID)
        #print(traceback.format_exc())
        f3.write(ID+' unknown:\n'+str(traceback.format_exc())+'\n')

    #写入数据库
    try:
        cur.execute('set names utf8')
        query='insert into iosapp values(%s)' % value
        query=query.encode('utf-8')
        cur.execute(query)
        db.commit()
    except:
        db.rollback()
        tb=traceback.format_exc()
        #若出'Duplicate entry'的错误，跳过该记录
        if ('Duplicate entry' in tb):
            tb=''
            #print('Duplicate data for ID='+ID) 
        else:
            #print('Invalid data for ID='+ID) 
            #print(traceback.format_exc())
            f4.write(ID+': database error level 1\n')
            f4.write(str(traceback.format_exc())+'\n')
            #若出'Incorrect string value'的错误，将出错的字段值设为null
            if ('Incorrect string value' in tb) and (tb.rfind('column')>=0):
                while 'Incorrect string value' in tb:
                    try:
                        attr=tb[tb.rfind('column')+8:tb.rfind('\'')]
                        iosapp[attr]='null'
                        value=iosapp['ID']+','+iosapp['name']+','+iosapp['seller']\
                               +','+iosapp['price']+','+iosapp['category']+','+iosapp['updated']\
                               +','+iosapp['version']+','+iosapp['size']+','+iosapp['language']\
                               +','+iosapp['seller_spec']+','+iosapp['copy_right']+','+iosapp['limit_grade']\
                               +','+iosapp['compatibility']+','+iosapp['rating_all']+','+iosapp['ra_amount']\
                               +','+iosapp['rating_current']+','+iosapp['rc_amount']+','+iosapp['in_app_purchase']\
                               +','+iosapp['more_app']+','+iosapp['comment_1']+','+iosapp['rate_1']\
                               +','+iosapp['comment_2']+','+iosapp['rate_2']+','+iosapp['comment_3']\
                               +','+iosapp['rate_3']+','+iosapp['purchase_also_1']+','+iosapp['purchase_also_2']\
                               +','+iosapp['purchase_also_3']+','+iosapp['purchase_also_4']+','+iosapp['purchase_also_5']\
                               +','+iosapp['content']
                        cur.execute('set names utf8')
                        query='insert into iosapp values(%s)' % value
                        query=query.encode('utf-8')
                        cur.execute(query)
                        db.commit()
                        tb=''
                    except:
                        db.rollback()
                        #print('Invalid data for ID='+ID)
                        #print(traceback.format_exc())
                        f4.write(ID+': database error level 1\n')
                        f4.write(str(traceback.format_exc())+'\n')
                        tb=traceback.format_exc()
                if tb!='':
                    #print('Inserting unsuccessfully for ID='+ID)
                    #print(traceback.format_exc())
                    f4.write(ID+': database error level 2\n')
                    f4.write(str(traceback.format_exc())+'\n')
            else:
                #print('Inserting unsuccessfully for ID='+ID)
                #print(traceback.format_exc())
                f4.write(ID+': database error level 2\n')
                f4.write(str(traceback.format_exc())+'\n')


def after_handle(text=r'G:\crawl\screen.txt'):
    f=open(text,'r')
    


#处理字符'"',将其转化为'^'
def str_trans(string):
    if string.find('"')<0:
        string=str_coding(string)
        return string
    else:
        trans=''
        while string.find('"')>=0:
             n=string.find('"')
             trans+=string[0:n]+'^'
             string=string[n+1:]
        trans+=string
        trans=str_coding(trans)
        return trans


#处理编码问题
def str_coding(string):
    if chardet.detect(string.encode('utf-8'))['encoding'] not in ['utf-8','ascii']:
        test=list(string)
        for item in test:
            if chardet.detect(item.encode('utf-8'))['encoding'] not in ['utf-8','ascii']:
                test.remove(item)
        string=''.join(test)
    return string
                        

#获得在Applist中但没有成功插入数据库的应用数据的应用ID，即出现database error level 2
def error_ID():
    #获得applist.txt中记录的应用ID号
    f=open(r'G:\crawl\applist0.txt','r')
    applist_txt=set()
    for line in f:
        line=line[0:url.find('?mt=')]
        applist_txt.add(line[-10:-1])

    #获得数据库中记录的ID号   
    applist_db=set()
    query='select ID from iosapp'
    cur.execute(query)
    for row in cur.fetchall():
        applist_db.add(row[0])

    #处理没有插入成功的ID号
    applist_error=applist_txt-applist_db
    return applist_error
    
    
#处理在Applist中但没有成功插入数据库的应用数据，即出现database error level 2
def error_handle(IDset):
    for ID in IDset:
        try:
            url='https://itunes.apple.com/cn/app/id%s?mt=8' % ID
            pageparse(url)
        except:
            print('Still Unsecessfully Inserting for ID='+ID)
            print(traceback.format_exc())


def close():
    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
    cur.close()
    db.close()


