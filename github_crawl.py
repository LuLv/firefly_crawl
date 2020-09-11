#!/usr/bin/env python
# coding: utf-8

import re
import requests
import random
import time
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import Request
import json


'''
为了运行以下代码，你应该：
a.在token=""处添加自己的GitHub token
b.如果改变爬虫的请求api，应该在download_from_page函数中修改api，这个函数当时写得快，设计得不算太好，建议改为直接传参数api和指定的页数
c.在GitHub上repo信息爬取完毕之后，如果需要下载，那么就结合csv中的repopURL和函数download_github_repo进行下载
'''


def get_html_json( page_url ):
    '''
    根据api的url，获取网页内容（json字符串），最后的result是网页的json dict
    '''
    random_header = api_headers[random.randint(0,14) ]#如果多进程的时候要注意random是否有mutex
    print("header ok\n")
    response = requests.get(page_url, headers=random_header)
    print("response ok!\n")
    html_str = response.content.decode()
    print("decode ok!\n")
    result = json.loads(html_str)#result是一个dict
    print("load ok !\n")
    return result


# #### repoId,name,fullname,repoHtml,zipUrl,size,starCnt,forksCnt,watchCnt,isForked




def download_from_page(min_page,max_page,csv_path):
    '''
    由于load api的搜索结果时，需要分页，所以此函数可以记录指定页数的search结果
    
    params@min_page:起始页数
    params@max_page:终止页数
    params@csv_path:csv_path,需要保存的csv文件 路径+文件名，如"./github_repo_info.csv"
    '''
    for j in range(min_page,max_page+1):
        print(j,"begin\n")
        
        #目前的api只能查找1000个结果，这是由GitHub爬虫的限制决定的，可能的解决方案在
        # https://stackoverflow.com/questions/37602893/github-search-limit-results#
        api = "https://api.github.com/search/repositories?q=+language:jupyter+notebook&sort=stars&order=desc&page="+str(j)+"&per_page=100"
        
        result=  get_html_json(api)#得到这个网页的json信息
        
        #得到result["items"]是这一页repo的信息的list，list中每一个元素为一个repo
        items = result["items"]
        f = open(csv_path,"a+",encoding="utf-8")#打开文件，使用的是追加写的方式

        for i in range(0,len(items)):#获取这一页所有repo的信息
            #存储格式为：repoId,name,fullname,repoHtml,zipUrl,size,starCnt,forksCnt,watchCnt,isForked
            
            item = items[i]
            repo_id = str(item['id'])
            repo_name = item['name']
            repo_fullname = item["full_name"]
            repo_html = item['html_url']
            zip_url = repo_html+"/archive/master.zip"
            size = str(item['size'])
            star_cnt = str(item["stargazers_count"])
            fork_cnt = str(item["forks"])
            watch_cnt = str(item["watchers_count"])
            if(item["fork"]):#存储是否为fork，便于后期筛选非fork的repo
                isForked = '1'
            else:
                isForked = '0'
            repo_info = repo_id+","+repo_name+","+repo_fullname+","+repo_html+","+zip_url+","+size+","+star_cnt+","+fork_cnt+","+watch_cnt+","+isForked+"\n"
            f.write(repo_info)
        print(j," page has done!")
        f.close()
        time.sleep(15)
    return


# In[71]:


def generate_zip_url(repo_url):
    '''
    params@url:一个repo的url，如：https://github.com/zjc666/Simplex_Algorithm
    
    这个函数根据一个repo的url得到其zip的网页地址
    如果后期的下载链接规则有变，可以改这个函数
    '''
    zip_url = url + "/archive/master.zip"

    return zip_url




def download_github_repo(url, save_path):
    """
    
    下载给定的repo，保存在本地
    params@url:给定repo的网址
    params@save_path:本地保存目录
    
    """
    print('processing:%s' % url)
    file_name = url.split('/')[-1]
    random_header = download_headers[randomint]
    response = requests.get(url, headers=random_header )
    content = response.text
    #通过url生成zip文件链接
    zip_url = generate_zip_url(url)
    #本地保存文件名,由于不考虑fork的repo，所以没考虑重名情况
    to_file = os.path.join(save_path, file_name) + '.zip'
    print('file to %s' % to_file)
    #调用request，获取内容，并写入文件
    try:
        requests.urlretrieve(zip_url, to_file)##将远程数据下载到本地。
    except:
        try:
            with open(to_file, 'wb') as code:
                code.write(requests.get(zip_url).content)
        except:
            try:
                http = urllib3.PoolManager()
                req = http.request('GET', zip_url)
                with open(to_file, 'wb') as code:
                    code.write(req.data)
            except:
                print(file_name + ' failed!!!!!!')
    print(file_name + ' done!')
    
    return
	

#search api需要的header,具体信息见https://developer.github.com/v3/search/
api_headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763', 'Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json' },
     {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
            {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
             {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'}
]

#下载repo时需要的头部
download_headers = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763' },
    {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3314.0 Safari/537.36 SE 2.X MetaSr 1.0' },
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50','Authorization':'token '+token, 'Content-Type':'application/json', 'method':'GET', 'Accept':'application/json'},
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201' },
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)' },
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)' },
    {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)' },
    {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)' },
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)' },
    {'User-Agent':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201' },
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50' },
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201' }
]

token = "" #填写GitHub的token



#一个使用GitHub api下载repo信息并且保存到csv的示例
#api = "https://api.github.com/search/repositories?q=+language:jupyter+notebook&sort=stars&order=desc&page="+str(2)+"&per_page=100"
#download_from_page(1,10,"./firefly_github_repo_info.csv")


#一个使用repo网页链接下载文件的示例：
#download_github_repo("https://github.com/zjc666/Simplex_Algorithm","./")







