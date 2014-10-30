#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs4,Tag
import time
import requests
import traceback

def get_html(url):
    #res = client.get(url)
    res=  requests.get(url)
    if res.status_code != 200:
        return None
    else:
        return res.content

def get_yy_href(tag):
    url = ''
    if tag.get('thunderhref'):
        url = tag.get('thunderhref')
    elif tag.get('qhref'):
        url = tag.get('qhref')
    elif tag.get('href'):
        url = tag.get('href')

    site_name = tag.string
    return site_name,url


def get_yy_download_url(html,url):
    print 'url:',url
    yyid = url.split('/')[-1]
    soup = bs4(html)
    season_list = soup.find_all('ul',class_='resod_list')
    info = soup.find_all('ul',class_='r_d_info')[0]
    cover_img = soup.find_all('div',class_='f_l_img')[0].find_all('img')[0]['src']
    album_name = soup.find_all('strong')[0].contents[0]
    album= {}
    album['yyid'] = yyid
    album['cover_img'] =cover_img
    album['info'] =repr(info)
    album['season'] =len(season_list)
    album['create_time'] = time.time()
    album['name'] = album_name
    #可以把剧集信息(album)插入数据库 
    for season in season_list:
        video_list=season.find_all('li')
        season_id = season['season']
        #每一季的所有视频列表
        video_data = {'season':season_id,'video':[]}
        for video in video_list:
            data={'link':[]}
            video_format = video['format']
            video_id = video['itemid']
            data['item_id'] = video_id
            data['yyid'] = yyid
            data['format'] = video_format
            data['album_name'] = album_name
            lks = video.find_all('div',class_="lks")[0]
            pks = video.find_all('div',class_="pks")
            #每个视频的所有下载地址
            download_links = pks[0].find_all('a')
            title = lks.find_all('a')[0]['title']
            data['title'] = title
            data['season'] = season_id
            for link in download_links:
                site_name,url = get_yy_href(link)
                data['link'].append({'name':site_name,'url':url})
            #把data插入数据库,data是单集里一个格式的所有下载地址
            #print data

def run_yy():
    """
    """
    root = "http://www.yyets.com/resource/%s"
    for i in range(24000):
        try:
            url = root%(10010+i)
            html = get_html(url)
            if not html:
                print '请求页面失败:',url
                html = get_html(url)
                if not html:
                    print '第二次请求页面失败:',url
                    continue
            elif '3*1000' in str(html):
                print '剧集不存在:',url
                continue
            get_yy_download_url(html,url)
            print '剧集存在:',url
            #time.sleep(0.1)
        except Exception,e:
            print('\n'*9)
            traceback.print_exc()
            continue
            print('\n'*9)


if __name__ == '__main__':
    run_yy()
