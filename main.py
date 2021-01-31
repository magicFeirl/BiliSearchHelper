import re
import time

from bsh import SearchHelper


def format_result(result, only_one=False):
    """完全为了检索 sm 号而准备"""
    sus = [] # 疑似相关视频列表
    certain = []
    repeated = [] # 重复视频列表

    # 记录所有关键字和完全匹配的关键字
    # 有些关键字可能只是因为有视频提到了而被误认为被找到了，然而实际上可能因为各种原因并没有被搬运
    all_keyword = set()
    certain_keyword = set()

    found, not_found = result

    found.sort(key=lambda x:x['keyword'])

    print()
    print()
    for item in found:
        content = ' '.join([item['keyword'], str(item['aid']), '(' + item['title'] + ')', item['author'] + '(uid:' + str(item['mid']) + ')'])

        all_keyword.add(item['keyword'])

        # 提取简介中的 sm 号
        parsed_kw = re.findall('sm\d+', item['description'])

        # 如果没有 sm 号 或 首个 sm 号和 keyword 不同，加入疑似列表
        # 第二个条件判断第一个 sm 号是否和关键字对应是基于搬运的格式，如果搬运给出的第一个 sm 号不是视频原地址就可能出错，
        # 不过 B 站搬运格式貌似是固定的，间接第一行就是 original link
        if (not parsed_kw) or (parsed_kw[0] != item['keyword']):
            sus.append((content + '\n简介:\n' + item['description']))
        else: # 否则这里输出的内容都是确定的 sm -> av
            if item['keyword'] not in certain_keyword: # sm 号已经出现过，表明检索结果有重复
                certain_keyword.add(item['keyword'])
                certain.append(content)
            else:
                if only_one:
                    repeated.append(content)
                else:
                    certain.append(content)

    return certain, repeated, sus, list(not_found), list(all_keyword - certain_keyword)


def read_data_from_textfile(filename):
    data = ''

    try:
        with open(filename, encoding='utf-8') as f:
            data = f.read()
    except OSError as e:
        print('读取文件出错:', e)

    return re.findall('sm\d+', data)


def main():
    filename = input('输入含 SM 号的文本文件名:\n')
    kw_list = read_data_from_textfile(filename)

    if not kw_list:
        return

    sh = SearchHelper()

    st = time.time()

    print()

    # baidu=False 不开启百度搜索
    r = sh.search(kw_list, desc_regex='sm\d+', doge=True, baidu=False)

    certain, repeated, sus, not_found, uncertain = format_result(r, only_one=True)

    output_filename = filename[:filename.rfind('.')] + '_out.txt'
    with open(output_filename, 'w', encoding='utf-8') as f:
        print(' 检索结果 '.center(40, '='), file=f)
        print('\n'.join(certain), file=f)
        print(file=f)
        print('未找到的数据:', file=f)
        print(' '.join(not_found), file=f)
        print(file=f)
        if uncertain:
            print('可能没找到的数据:', file=f)
            print(' '.join(uncertain), file=f)
            print(file=f)
        print('重复出现过的数据:', file=f)
        print('\n'.join(repeated), file=f)
        print(file=f)
        if sus:
            print('相关数据:', file=f)
            print('\n'.join(sus), file=f)

    print('结果已输出到: {}'.format(output_filename))

    print()
    print('耗时 {}s'.format(round(time.time() - st, 2)))


def display_help():
    print(' B站视频批量检索助手 '.center(60, '='))
    print('简介: ')
    print('用于批量检索 SM 号并找到对应的 AV 号并输出，支持检索被屏蔽的视频；')
    print('可用于N站的 mylist/series/video 同步、各种N站期刊视频等需要大量搜索 SM 号的情况；')
    print('代码开源在 Github: https://github.com/magicFeirl/BiliSearchHelper')
    print('=' * 69)
    print()


if __name__ == '__main__':
    display_help()
    main()

    input('按回车键退出...')
