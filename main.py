import json
import os
import time
import urllib
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
import requests
import traceback
import threadpool
from hashlib import new as hashlib_new

# 没有正经学过py,c语言也就学过一周,边查资料边写的,可能有亿堆bug --hong_shi_jun



def getZipDir(dirpath, outFullName, fileFolderName):
    """
    压缩指定文件夹
    :param dirpath: 要压缩的文件夹路径
    :param outFullName: 压缩文件保存路径
    :param fileFolderName: 目标路径中要压缩的文件夹名称(objects)
    :return: 无
    """
    #zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    #for path, dirnames, filenames in os.walk(dirpath):
    #    path_ = os.path.join(dirpath)
    #    #fpath = path.replace(path_)
    #    fpath = str(path_)
    #    for filename in filenames:
    #        zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    #zip.close()
    
    if os.path.exists(outFullName):
       # 如果存在就删除
       os.remove(outFullName)
       
    with zipfile.ZipFile(outFullName, 'w') as zfile:
        for foldername, subfolders, files in os.walk(dirpath):
            #foldername = str(foldername).split(File_Download_Path)[0]
            zfile.write(foldername)
            for i in files:
                zfile.write(os.path.join(foldername, i))
        zfile.close()
    print("文件夹\"{0}\"已压缩为\"{1}\".".format(dirpath, outFullName))

def Sha1(File) -> str:
    """
        文件Sha1值计算
        :param File: 文件路径
        :return: Sha1值(str)
    """
    with open(File, 'rb') as f:
        return hashlib_new('sha1', f.read()).hexdigest()

def getJsonUrl(url):
    """
        JsonURL访问
        :param url: 访问json链接
        :return: 链接中字典类型的数据
    """
    while True:
        try:
            json_url = urllib.request.urlopen(url,timeout=5)
            dict_url = json.loads(json_url.read())
            break
        except urllib.request.socket.timeout:
           print('下载json超时,重试') 
    return dict_url

def DelateFile(Path):
    """删除文件"""
    if os.path.exists(Path):
        os.remove(Path)

def downloadFile(z):
    """
        下载文件并进行哈希校验
        :param z: [文件下载路径,文件下载路径的上级目录,sha1]
        :return: 校验成功返回0
    """

    sha1 = z[2]
    downloadPath = z[0]
    fileUrl = "https://resources.download.minecraft.net/"+ sha1[:2] + "/" + sha1
    #print('Download:' + downloadPath)
    #if not os.path.exists(downloadPath[0:downloadPath.rfind('\\')]):
    #    os.makedirs(downloadPath[0:downloadPath.rfind('\\')])
    if not os.path.exists(downloadPath):
        os.makedirs(z[1],exist_ok=True)
    #fp = urllib.request.urlopen(fileUrl)
    # print(type(fp))  #debug
    #data = fp.read()
    #f = open(downloadPath, 'w+b')
    #f.write(data)
    #f.close()
    while True:
        while True:
            try:
                stream = False
                r = requests.get(fileUrl,stream=stream,timeout=(5,20))
                with open(downloadPath, 'wb') as fb:
                    fb.write(r.content)
                break
            except requests.exceptions.ReadTimeout:
                print('超时重试 ' + downloadPath)
                DelateFile(fileUrl)
            except requests.exceptions.ConnectionError:
                print('ConnectionError重试 ' + downloadPath)
                DelateFile(fileUrl)
            except:
                traceback.print_exc()
                ErrorStop()
        
        if Sha1(downloadPath) == sha1:
            # print("校验通过")
            print('下载完成 ' + downloadPath)
            break
        else:
            print("检验失败, 重新下载"+str([sha1,downloadPath,fileUrl]))
            os.remove(downloadPath)
            print('上次文件删除完成,开始重新下载' + str([sha1,downloadPath,fileUrl]))
            # ErrorStop()
    return 0

def downloadFileList(objects):
    # 下载文件列表
    ii = 0
    data_list = [0 for a in range(len(objects['objects']))]
    
    pool = threadpool.ThreadPool(n_threads)

    
    for items in objects['objects']:  # 将所有文件的名称和哈希值放入数组
        hash = objects['objects'][items]['hash']
        p = os.path.join(Download_Path,hash[:2],hash)
        p_s = os.path.join(Download_Path,hash[:2]) 
        #data_list[ii] = [Download_Path + '\\' + items.replace('/', "\\"),hash]
        data_list[ii] = [p,p_s,hash]
        global size
        size += objects['objects'][items]['size']
        ii += 1
    #print(data_list)
    
    r = threadpool.makeRequests(downloadFile, data_list, callback) # 创建任务
    [pool.putRequest(req) for req in r] # 加入任务
    pool.wait()
    del pool,r
    
    print('需要下载的大小：'+ str(size) + '(' + str(size/1024/1024) + 'MB)')
    #with ThreadPoolExecutor(max_workers=n_threads) as pool:    
    #    pool.map(downloadFile,data_list)
    print("下载结束")
    return 0

def callback(request, result): # 线程池回调函数，用于取回结果
    pass

def assetIndexURL(assetIndexURL):
    """返回版本页中assetIndex中的url"""
    while True:
        try:
            dict_url = getJsonUrl(assetIndexURL)
            return dict_url['assetIndex']['url']
            break
        except urllib.error.URLError:
            print('json文件下载超时')

def ErrorStop():
    exit('-1')

if __name__ == '__main__':
    File_Download_Path = os.path.join('')  # 下载路径
    File_Zip_Path = os.path.join('FileZip')  # 压缩路径
    n_threads = 120  # 开设线程数

    url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
    Download_Path = os.path.join(File_Download_Path,'objects')
    
    if File_Download_Path != '':
        try:
            os.mkdir(File_Download_Path)
        except FileExistsError:
            shutil.rmtree(File_Download_Path)
            os.mkdir(File_Download_Path)
    if File_Zip_Path != '':
        try:
            os.mkdir(File_Zip_Path)
        except FileExistsError:
            shutil.rmtree(File_Zip_Path)
            os.mkdir(File_Zip_Path)
            
    ii = 0
    iii = 0
    version = 0
    global size
    size = 0
    Zip_Json = {}


    version_list = getJsonUrl(url)['versions']  # 下载版本列表
    A_URL_List = []
    print('开始运行\n正在执行Json配置去重操作')
    for l_1 in version_list:
        if l_1['type'] == 'release':    #判断是否为正式版
            id = l_1['id']
            A_URL = assetIndexURL(l_1['url'])
            if A_URL not in A_URL_List:
                A_URL_List.append(A_URL)
                print('添加资源文件URL: ' + str(A_URL))
    print('资源文件去重完成, 一共需要运行' + str(len(A_URL_List)) + '个配置文件')
    print('去重后资源文件URL列表: ' + str(A_URL_List))
    print('开始下载文件')
    
    for URL_1 in A_URL_List:
        id = str(URL_1).split('/')[-1]
        id = id.split('.json')[0]
        print('开始处理资源文件(ID: ' + str(id) + ',URL: ' + URL_1 + ')')
        while True:
                try:
                    objects = getJsonUrl(URL_1) # 下载资源文件JSON
                    break
                except urllib.error.URLError:
                    print('json文件下载超时')
        print('资源文件JSON下载完成: ' + URL_1 + '\n开始下载资源文件')
        downloadFileList(objects) # 下载资源文件
        print('资源文件下载完成\n开始压缩')
        file = os.path.join(File_Zip_Path,File_Download_Path,id + '.zip')
        getZipDir(Download_Path,file,"objects")  # 压缩
        ZipSha1 = Sha1(file)
        Zip_Json[file] = {
            'URL':URL_1,
            'Sha1':ZipSha1,
            'Path':file
        }
        print('开始删除下载文件')
        try:
            shutil.rmtree(Download_Path) # 删除objects文件夹
        except FileNotFoundError:
            os.mkdir(Download_Path)  # 新建objects文件夹
        print('删除下载文件完成')
    print('生成的版本Json' + str(Zip_Json))
    JsonFile_ = os.path.join('ShaAndPath.json')
    with open(JsonFile_, 'w+', encoding='utf_8') as f:
        json.dump(Zip_Json, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
            
    """
    while i < len(version_list["versions"]):
        if version_list['versions'][i]['type'] == 'release':    #判断是否为正式版
            print(version_list['versions'][i]['id'])  # 输出版本
            #time.sleep(2)
            version = version_list["versions"][i]
            while True:
                try:
                    objects = getJsonUrl(assetIndexURL(version['url'])) # 下载版本的文件列表
                    break
                except urllib.error.URLError:
                    print('json文件下载超时')
            
            downloadFileList(objects) #下载文件
            print('下载完成')
            file = os.path.join(File_Download_Path,version['id'] + '.zip')
            getZipDir(Download_Path,file,"objects")  # 压缩
        #time.sleep(1)
        try:
            shutil.rmtree(Download_Path) # 删除objects文件夹
        except FileNotFoundError:
            os.mkdir(Download_Path)  # 新建objects文件夹
        i += 1
        size = 0
    """
