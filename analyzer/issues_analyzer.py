import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import ast
from matplotlib import rcParams

rcParams['font.family'] = ['SimHei']  # 设置为黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class IssuesAnalyzer:
    result_dir = "./result"
    
    def __init__(self):
        self.issues_df = pd.DataFrame()
        self.pulls_df = pd.DataFrame()
        return
        
    # 处理和分析Issues数据
    def analyze_issues(self, file):
        open_issues = self.issues_df[self.issues_df['state'] == 'open']
        closed_issues = self.issues_df[self.issues_df['state'] == 'closed']

        open_issues_count = len(open_issues)
        closed_issues_count = len(closed_issues)

        # 计算每个issue的生命周期（从创建到关闭的时间差）
        closed_issues['created_at'] = pd.to_datetime(closed_issues['created_at'])
        closed_issues['closed_at'] = pd.to_datetime(closed_issues['closed_at'])
        closed_issues['lifecycle_days'] = (closed_issues['closed_at'] - closed_issues['created_at']).dt.days

        # 问题标签分析
        label_counts = Counter()
        for labels in closed_issues['labels']:
            for label in labels.split(','):
                label_counts[label.strip()] += 1

        file.write(f"打开的问题数量: {open_issues_count}\n")
        file.write(f"已关闭的问题数量: {closed_issues_count}\n")
        file.write(f"已关闭问题的平均生命周期（天数）: {closed_issues['lifecycle_days'].mean():.2f}\n")

        # 输出标签频率
        file.write("\n最常见的标签:\n")
        for label, count in label_counts.most_common(10):
            file.write(f"{label}: {count}\n")

    # 处理和分析Pull Requests数据
    def analyze_pull_requests(self, file):
        open_prs = self.pulls_df[self.pulls_df['state'] == 'open']
        closed_prs = self.pulls_df[self.pulls_df['state'] == 'closed']

        closed_prs['created_at'] = pd.to_datetime(closed_prs['created_at'])
        closed_prs['merged_at'] = pd.to_datetime(closed_prs['merged_at'], errors='coerce')
        closed_prs['lifecycle_days'] = (closed_prs['merged_at'] - closed_prs['created_at']).dt.days

        file.write(f"\n打开的PR数量: {len(open_prs)}\n")
        file.write(f"已关闭的PR数量: {len(closed_prs)}\n")
        file.write(f"已合并PR的平均生命周期（天数）: {closed_prs['lifecycle_days'].mean():.2f}\n")

    # 处理关键词分析并绘制图表
    def analyze_keywords_and_plot(self, file):
        self.issues_df['labels'] = self.issues_df['labels'].apply(ast.literal_eval)

        names = [label['name'] for labels in self.issues_df['labels'] for label in labels]
        keywords = ['question', 'bug', 'enhancement', 'detect', 'documentation', 'TODO', 'Stale', 'dependencies', 'help wanted']
        name_counts = {keyword: names.count(keyword) for keyword in keywords}

        file.write("\n关键词统计（name字段）：\n")
        for keyword, count in name_counts.items():
            file.write(f"{keyword}: {count}\n")

        plt.figure(figsize=(10, 6))
        plt.plot(list(name_counts.keys()), list(name_counts.values()), marker='o', linestyle='-', color='b')
        plt.title('name字段关键词统计图')
        plt.xlabel('关键词')
        plt.ylabel('数量')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.savefig(f'{IssuesAnalyzer.result_dir}/keyword_counts_plot.png')
        print("关键词统计图已保存为: keyword_counts_plot.png")
        plt.close()


    def analyze_data(self, config, issues, pulls):
        IssuesAnalyzer.result_dir = config["resultDir"]
        self.issues_df = pd.DataFrame(issues)
        self.pulls_df = pd.DataFrame(pulls)

        with open(f'{IssuesAnalyzer.result_dir}/issuesLifecycle.txt', 'w', encoding='utf-8') as file:
            self.analyze_issues(file)
            self.analyze_pull_requests(file)
            self.analyze_keywords_and_plot(file)
            print("Issues分析结果已保存到: issuesLifecycle.txt")

    
