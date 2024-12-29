import requests
import os 
import shutil

def reqTest(proxyPort='7897'):
    '''
    代理测试方法
    '''
    proxies = {
        'http': f'http://localhost:{proxyPort}',
        'https': f'https://localhost:{proxyPort}',
    }
    try:
        response = requests.get('https://api.github.com', proxies=proxies, verify=False)
        print(f"代理测试成功，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"代理测试失败: {e}")

#reqTest()

def clone_yolov5Repo():
    os.system(f'git clone https://github.com/ultralytics/yolov5.git')

def rm_yolov5Repo():
    #删除YOLOv5仓库
    if os.path.exists('yolov5'):
        shutil.rmtree('yolov5', onerror=lambda func, path, excinfo: (os.chmod(path, 0o777), func(path)))
        print(f"YOLOv5仓库已删除")
    else:
        print(f"YOLOv5仓库不存在")