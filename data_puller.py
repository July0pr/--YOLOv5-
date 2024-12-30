import os
import git
import requests
import pandas as pd

class DataPuller:
    """
    该类用于处理数据保存、分析提交历史、从 GitHub 获取数据等任务。
    包含保存 CSV 文件、分析 Git 提交历史、获取 GitHub 数据的方法。
    """
    @staticmethod
    def save_to_csv(data, filename):
        """
        将数据保存为 CSV 文件。
        
        输入：data (list/dict): 要保存的数据
              filename (str): 保存文件的名称
        """
        file_path = os.path.join("./data", filename)
        pd.DataFrame(data).to_csv(file_path, index=False)
        print(f"数据已保存到: {file_path}")

    @staticmethod
    def analyze_commit_history(repo_path):
        """
        分析指定 Git 仓库的提交历史，提取提交信息。
        
        输入：repo_path (str): 本地 Git 仓库的路径
        输出：commits (list): 包含提交信息的列表，每个提交是一个字典
        """
        repo = git.Repo(repo_path)
        commits = []
        for commit in repo.iter_commits():
            commits.append({
                "hash": commit.hexsha,
                "author": commit.author.name,
                "date": commit.committed_date,
                "message": commit.message.strip(),
                "linesChanged": commit.stats.total["lines"]
            })
        DataPuller.save_to_csv(commits, "commitHistory.csv")
        return commits

    @staticmethod
    def fetch_github_data(repo_name, token, data_type="issues", proxies=None):
        """
        从 GitHub 获取指定仓库的数据（issues 或 PRs）。
        
        输入：repo_name (str): GitHub 仓库名称
              token (str): GitHub 访问令牌
              data_type (str): 要获取的数据类型（issues 或 pulls）
              proxies (dict): 代理设置
        输出：results (list): 获取的数据列表
        """
        url = f"https://api.github.com/repos/{repo_name}/{data_type}"
        headers = {"Authorization": f"token {token}"}
        results = []
        page = 1
        while True:
            response = requests.get(url, headers=headers, params={"page": page, "per_page": 100}, proxies=proxies, verify=False)
            if response.status_code != 200:
                print(f"获取数据失败，状态码: {response.status_code}")
                break
            data = response.json()
            if not data:
                break
            results.extend(data)
            page += 1
        DataPuller.save_to_csv(results, f"{data_type}.csv")
        return results

    @staticmethod
    def pull_data(config):
        """
        从 Git 仓库和 GitHub 拉取数据，分别获取提交历史、issues 和 PR 数据。
        
        输入：config (dict): 包含仓库路径、GitHub 仓库名、令牌和代理设置的配置字典
        输出：commits (list), issues (list), prs (list): 返回提交历史、issues 和 PR 数据
        """
        print("开始拉取提交历史...")
        commits = DataPuller.analyze_commit_history(config['repoPath'])

        print("正在获取 GitHub Issue 和 PR 数据...")
        issues = DataPuller.fetch_github_data(config['githubRepo'], config['githubToken'], "issues", config['proxies'])
        prs = DataPuller.fetch_github_data(config['githubRepo'], config['githubToken'], "pulls", config['proxies'])

        return commits, issues, prs
