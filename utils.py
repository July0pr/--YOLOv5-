import requests

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