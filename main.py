import argparse
import os
import json
from data_puller import DataPuller
from data_analyzer import DataAnalyzer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='YOLOv5 仓库分析配置')
    parser.add_argument('-p', '--proxyPort', type=str, default='7897', help='代理端口')
    parser.add_argument('-r', '--repoPath', type=str, default='./yolov5', help='仓库路径')
    parser.add_argument('-g', '--repoName', type=str, default='ultralytics/yolov5', help='GitHub 仓库名')
    parser.add_argument('-d', '--dataDir', type=str, default='./data', help='数据目录')
    parser.add_argument('-a', '--resultDir', type=str, default='./result', help='分析结果目录')
    parser.add_argument('-u', '--update', action='store_true', help='更新数据')
    args = parser.parse_args()

    #请在config.json文件中配置你的token
    with open('./githubToken.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        if not config_data['token']:
            print('请在config.json文件中配置你的token')
            exit(1)

    config = {
        'proxyPort': args.proxyPort,
        'proxies': {
            'http': f'http://localhost:{args.proxyPort}',
            'https': f'http://localhost:{args.proxyPort}',
        },
        'resultDir': args.resultDir,
        'repoPath': args.repoPath,
        'githubRepo': args.repoName,
        'githubToken': config_data['token'],
        'dataDir': args.dataDir,
    }
    os.makedirs(args.dataDir, exist_ok=True)
    os.makedirs(args.resultDir, exist_ok=True)

    analyzer = DataAnalyzer()
    commits, issues, prs = DataPuller.pull_data(config, args.update)
    analyzer.analyze_data(config, commits)

    