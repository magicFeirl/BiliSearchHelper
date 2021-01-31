import re
import time

from .net import Net


class SearchHelper(object):
    """
    搜索方法返回一个列表，内含如下格式的字典:

    {
        'author': '幻想乡的新月',
        'mid': 149592,
        'aid': 'av2600096',
        'title': '【东方MMD】暗黑炼狱火☆',
        'description': 'sm26747660 这个简直wwww~作者FSM'
    }
  """
    def __init__(self, SESSDATA='', BILI_JCT=''):
        self.found_aid = set() # 找到的视频 av/bv 号集合
        self.not_found_kw = set() # 没有找的的关键字集合
        self.result_list = []

        self.net = Net()

        self.cookie = {}

        self.bili_headers= {
            'origin': 'https://search.bilibili.com',
            'referer': 'https://search.bilibili.com/',
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'),
            'cookie': 'SESSDATA={}; BILI_JCT={};'.format(SESSDATA, BILI_JCT)
        }

    def _find_key(self, dict_obj, kw_set, kw_map=None, default_value=None):
        """提取出字典中指定的 keyword 组成一个一维的字典，并根据可选的 keyword map 将原字典的指定键映射到给出的键"""
        def dfs(dict_obj, result_dict):
            """简单的 DFS，把 dict 中 key in kw_set 的键值对 update 到 result_dict 里面"""
            for k, v in dict_obj.items():
                if k in kw_set:
                    result_dict.update({k: v})
                else:
                    if isinstance(v, list):
                        for i in v:
                            if isinstance(i, dict):
                                dfs(i, result_dict)

                    if isinstance(v, dict):
                        dfs(v, result_dict)

        result_dict = {}
        dfs(dict_obj, result_dict)

        for key in list(kw_set):
            if key not in result_dict:
                result_dict.update({key: default_value})

        if kw_map is None:
            return result_dict

        mapped_dict = {}
        for key in kw_set:
            if key in kw_map: # 如果关键字在映射表中，改键名
                mapped_dict.update({kw_map[key]: result_dict[key]})
            else: # 不在就不修改
                mapped_dict.update({key: result_dict[key]})

        return mapped_dict

    def search(self, kw_list, desc_regex='', doge=True, baidu=False):
        """聚合站内检索和站外检索方法，先站内检索，后站外检索
        返回一个元组，第一个元素值为视频信息 dict（格式见类的注释），第二个元素值为未找到的关键字列表
        ([{...}], [...])"""
        import traceback

        try:
            self.not_found_kw = set(kw_list) # 初始假设所有关键字都没有找到

            kw_list = list(self.not_found_kw) # 去重然后还原

            print('*** 开始站内检索，预计耗时 {}s'.format(2 * len(kw_list)))

            found, not_found = self.search_from_bili(kw_list, desc_regex=desc_regex)
            print('找到 {} 个数据'.format(len(found)))

            if doge:
                print()
                print('*** 开始站外检索(Dogedoge)，预计耗时 {}s'.format(2 * len(not_found)))

                found, not_found = self.search_from_doge(list(self.not_found_kw), desc_regex=desc_regex)
                print('找到 {} 个数据'.format(len(found)))
            if baidu:
                print()
                print('*** 开始站外检索(Baidu)，预计耗时 {}s'.format(2 * len(not_found)))

                found, not_found = self.search_from_baidu(list(self.not_found_kw), desc_regex=desc_regex)
                print('找到 {} 个数据'.format(len(found)))
        except Exception:
            print('#' * 30)
            print('ERROR:')
            traceback.print_exc()

        print()

        return self.result_list, list(self.not_found_kw)

    # 站内检索
    def search_from_bili(self, kw_list, desc_regex=''):
        """站内检索
        提供一个 desc_regex 正则表达式提取简介中符合条件的 keyword list => desc_words，如果 desc_words[0] == keyword，确定该视频
        是要找的视频，否则该视频可能只是和 keyword 关键字相关而被检索到，不移除 not_found_kw 中对应的值"""

        headers =self.bili_headers

        kw_list = list(set(kw_list))
        kw_count = len(kw_list)

        # 根据数据量动态设置休眠时间。不知道有没有用
        if kw_count < 40:
            delay = 0.5
        elif kw_count >= 40 and kw_count <= 80:
            delay = 1.5
        else:
            delay = 2.5

        for kw in kw_list:
            api = 'https://api.bilibili.com/x/web-interface/search/type'
            print('Searching {} ...'.format(kw))

            for page in range(1, 6): # 最多取 5 页数据
                params = {
                    'keyword': kw,
                    'search_type': 'video',
                    'page': page
                }

                dict_kw_set = {'aid', 'author', 'mid', 'title', 'description'}
                jsoup = self.net.get(api, headers=headers, params=params).json()

                if jsoup['code'] == 0:
                    data = jsoup['data']

                    if 'result' in data:
                        for item in data['result']:
                            dict_item = {'keyword': kw}
                            aid = 'av' + str(item['aid'])

                            if aid not in self.found_aid:
                                self.found_aid.add(aid)

                                dict_item.update(self._find_key(item, dict_kw_set))
                                dict_item.update({'aid': aid})

                                for k, v in dict_item.items(): # 转 str
                                    dict_item[k] = str(v)

                                self.result_list.append(dict_item)

                                if kw in self.not_found_kw:
                                    if desc_regex:
                                        desc_words = re.findall(desc_regex, dict_item['description'])
                                        if desc_words and (desc_words[0] == dict_item['keyword']): # 如果关键字存在且为第一个项，认为找到了
                                            self.not_found_kw.remove(kw)
                                    else:
                                        self.not_found_kw.remove(kw)

                        print('休眠 {}s'.format(delay))
                        time.sleep(delay)

                        # 一页数据全部获取到后就退出
                        break
                    else:
                        self.not_found_kw.add(kw)
                        print(kw, '无数据，可能是因为被屏蔽或被删除')
                        break
                # 被 ban，似乎其他接口没受到影响
                # 恢复时间大概 30min ?
                # {'code': -412, 'message': '请求被拦截', 'ttl': 1, 'data': None}
                # elif jsoup['code'] == -412:
                else:
                    print('接口调用过于频繁，请稍后再试')
                    print(jsoup)
                    break

        # 考虑到单独使用方法可能
        return self.result_list, list(self.not_found_kw)

    # 剩下的全是站外检索相关方法
    def get_video_info(self, vid):
        """获取视频信息 json"""
        if vid.startswith('BV'):
            bapi = 'https://api.bilibili.com/x/web-interface/view?bvid={}'
            video_info = self.net.get(bapi.format(vid), headers=self.bili_headers).json()
        else: # 以 AV 号为参数的视频信息接口， dogedoge 返回的基本都是 BV 号，不过还加上以防万一
            aapi = 'https://api.bilibili.com/x/web-interface/view?aid={}'
            video_info = self.net.get(aapi.format(vid[2:]), headers=self.bili_headers).json()

        return video_info

    # 站外检索专用
    def add_to_resultlist(self, video_info, vid, kw):
        """把结果添加到列表"""
        dict_item = {}
        if video_info['code'] == -403: # 这种稿件是登录可见的 {'code': -403, 'message': '访问权限不足', 'ttl': 1}
            if vid.startswith('BV'): # 如果是 BV 号，转成 AV 号
                stat = 'https://api.bilibili.com/x/web-interface/archive/stat?bvid={}'
                vid = 'av' + str(self.net.get(stat.format(vid)).json()['data']['aid'])

            print(kw, vid, '需要登录查看')

            dict_item = {
                    'keyword': kw, 'aid': vid,
                    'author': 'unknown', 'mid': -1,
                    'description': '视频需要登录查看', 'title': '视频需要登录查看'
            }

            self.result_list.append(dict_item)
        elif video_info['code'] == 0: # 正常
            data = video_info['data']
            dict_item = {'keyword': kw}
            dict_kw_set = {'aid', 'name', 'mid', 'desc', 'title'}
            dict_item.update(self._find_key(data, dict_kw_set, {'name': 'author', 'desc': 'description'}))
            dict_item['aid'] = 'av' + str(dict_item['aid'])

            for k, v in dict_item.items(): # 全部转为 str
                dict_item[k] = str(v)

            if dict_item['aid'] not in self.found_aid:
                self.found_aid.add(dict_item['aid'])

                self.result_list.append(dict_item)
        else: # 到这里说明稿件已经被删除
            if video_info['code'] == -404:
                print(kw, '已被削除')
            else:
                print('检索 {} 失败，MSG: {} CODE:{}'.format(kw, video_info['message'], video_info['code']))

            self.not_found_kw.add(kw)

        return dict_item

    # dogedoge
    def search_from_doge(self, kw_list, desc_regex=''):
        from lxml.html import fromstring

        url = 'https://www.dogedoge.com/results'

        headers = {
            'referer': 'https://www.dogedoge.com/',
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66')
        }

        kw_list = list(set(kw_list)) # 去重
        kw_count = len(kw_list)

        if kw_count <= 20: # 数据量在 20 个以内时最多休眠 2s
            max_delay = 2
        else:
            max_delay = 3 # 数据量超过 20 最多休眠 3s

        for kw in kw_list:
            params = {
                'q': kw,
                'lang': 'cn'
            }

            html = self.net.get(url, headers=headers, params=params).text
            elements = fromstring(html)
            element_a = elements.xpath('//a[@class="result__url js-result-extras-url"]')

            print('Searching {} ...'.format(kw))

            if not element_a:
                self.not_found_kw.add(kw)

            for a in element_a[:5]: # 取前五个数据
                domain = a.xpath('string(./span[@class="result__url__domain"])')

                if domain and domain.find('www.bilibili.com') != -1: # 是 B 站的内容
                    redirect_url = 'https://www.dogedoge.com/' + a.get('href')
                    dist = self.net.get(redirect_url, headers=headers, allow_redirects=False).headers['location']

                    vid = re.findall('BV\w+|av\d+', dist)

                    if vid:
                        vid = vid[0]

                        video_info = self.get_video_info(vid)
                        dict_item = self.add_to_resultlist(video_info, vid, kw)
                        if not dict_item: # 检索失败，break
                            break

                        if kw in self.not_found_kw:
                            if desc_regex:
                                desc_words = re.findall(desc_regex, dict_item['description'])
                                if desc_words and desc_words[0] == dict_item['keyword']: # 如果关键字存在且为第一个项，认为找到了
                                    self.not_found_kw.remove(kw)
                            else:
                                self.not_found_kw.remove(kw)

                        # 取所有相关的数据，每次休眠 0.3s
                        time.sleep(0.3)

            from random import randint

            delay = randint(1, max_delay) # 随机暂停 1-max_delay s
            print('休眠 {}s.'.format(delay))
            time.sleep(delay)

        # 考虑到单独使用方法可能
        return self.result_list, list(self.not_found_kw)

    # baidu
    def search_from_baidu(self, kw_list, desc_regex=''):
        from lxml.html import fromstring

        url = 'https://www.baidu.com/s?si=bilibili.com&ie=utf-8' # 指定只搜索B站内容

        headers = {
            'host': 'www.baidu.com',
            'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                           ' Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'),
            'Cookie': '''BAIDUID=FB53574E47F87681AD5EE4D4E393F31F:FG=1; BIDUPSID=AEA4E6FE6B39C2300FDE0F7C39633B1A;'''
       }

        kw_list = list(set(kw_list)) # 去重
        kw_count = len(kw_list)

        if kw_count <= 20: # 数据量在 20 个以内时最多休眠 2s
            max_delay = 1
        else:
            max_delay = 3 # 数据量超过 20 最多休眠 3s

        for kw in kw_list:
            params = {
                'wd': kw
            }

            print('Searching {} ...'.format(kw))

            html = self.net.get(url, headers=headers, params=params).text

            try:
                elements = fromstring(html)
                result_div = elements.xpath('//div[@class="result c-container new-pmd"]')
            except Exception as e:
                self.not_found_kw.add(kw)
                continue

            if not result_div:
                self.not_found_kw.add(kw)

            for elem in result_div[:5]: # 取前 5 个数据
                # show_url = elem.xpath('.//span[@class="c-showurl"]/text()')
                location = elem.xpath('.//h3[@class="t"]/a/@href')

                if location: # and show_url and show_url[0].find('www.bilibili.com') != -1: 这里已经限制了是B站检索，所以不用判断是否是B站内容
                    ua_header = {'user-agent': headers['user-agent']}
                    vid = self.net.get(location[0], ua_header, allow_redirects=False).headers['location'] # 没有 headers（用默认headers）
                    vid = re.findall('BV\w+|av\d+', vid)

                    if vid:
                        vid = vid[0]

                        video_info = self.get_video_info(vid)

                        dict_item = self.add_to_resultlist(video_info, vid, kw)
                        if not dict_item: # 检索失败，break
                            break

                        if kw in self.not_found_kw:
                            if desc_regex:
                                desc_words = re.findall(desc_regex, dict_item['description'])
                                if desc_words and desc_words[0] == dict_item['keyword']: # 如果关键字存在且为第一个项，认为找到了
                                    self.not_found_kw.remove(kw)
                            else:
                                self.not_found_kw.remove(kw)

                        time.sleep(0.3)

            from random import randint

            delay = randint(1, max_delay) # 随机暂停 1-max_delay s
            print('休眠 {}s.'.format(delay))
            time.sleep(delay)

        return self.result_list, list(self.not_found_kw)
