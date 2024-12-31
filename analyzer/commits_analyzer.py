import libcst as cst
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei']  # 设置为黑体
rcParams['axes.unicode_minus'] = False   # 解决负号显示问题

class CommitsAnalyzer:
    """
    该类用于代码分析、模糊测试数据生成以及提交历史的可视化。
    包含分析代码中的函数和类数量、生成模糊测试输入数据和可视化提交历史数据的方法。
    """
    result_dir = "./result"

    def __init__(self):
        self.function_count = 0
        self.class_count = 0

    def analyze_code_structure(self, file_path):
        """
        分析指定Python文件中的函数和类数量。
        
        输入：file_path (str): 要分析的Python文件路径
        输出：dict: 包含'functions'和'classes'键的字典，分别表示函数和类的数量
        """
        with open(file_path, "r", encoding="utf-8") as f:
            tree = cst.parse_module(f.read())
        self.function_count = 0
        self.class_count = 0

        def visit_FunctionDef(node: cst.FunctionDef):
            self.function_count += 1

        def visit_ClassDef(node: cst.ClassDef):
            self.class_count += 1

        tree.visit(cst.CSTVisitor())
        return {
            "functions": self.function_count,
            "classes": self.class_count
        }


    @staticmethod
    def visualize_commit_history(commits):
        """
        根据提交记录可视化提交历史趋势。
        
        输入：commits (list): 包含提交信息的列表，每个提交是一个字典，包含'date'字段
        """
        df = pd.DataFrame(commits)
        df["date"] = pd.to_datetime(df["date"], unit="s")
        df["date"] = df["date"].dt.date
        commits_per_day = df.groupby("date").size()
        commits_per_day.plot(kind="line", title="提交历史趋势", xlabel="日期", ylabel="提交次数")
        plt.savefig(f"{CommitsAnalyzer.result_dir}/commitsOverTime.png")
        print("提交历史可视化图已保存为 'commitsOverTime.png'")

    @staticmethod
    def visualize_author(commits):
        df = pd.DataFrame(commits)
        commitsCount = df["author"].value_counts()

        # 忽略提交次数在 5 和以下的作者
        commitsCount = commitsCount[commitsCount > 5]

        plt.figure(figsize=(10, 6))
        commitsCount.plot(kind="barh", title="不同作者的提交次数", xlabel="提交次数", ylabel="作者")
        plt.tight_layout()
        plt.savefig(f"{CommitsAnalyzer.result_dir}/commitsByAuthor.png")
        print("提交历史可视化图已保存为 'commitsByAuthor.png'")

    @staticmethod
    def visualize_linescommite(commits):
        df = pd.DataFrame(commits)

        linesChangedByAuthor = df.groupby("author")["linesChanged"].sum()
        linesChangedByAuthor = linesChangedByAuthor.sort_values(ascending=False)

        threshold = linesChangedByAuthor.sum() * 0.01
        linesChangedByAuthor["其他"] = linesChangedByAuthor[linesChangedByAuthor < threshold].sum()
        linesChangedByAuthor = linesChangedByAuthor[linesChangedByAuthor >= threshold]

        plt.figure(figsize=(8, 8))
        linesChangedByAuthor.plot(kind="pie", autopct="%.1f%%", title="作者的代码提交行数占比")
        plt.ylabel("") 
        plt.savefig(f"{CommitsAnalyzer.result_dir}/linesChangedByAuthor.png")
        print("作者的代码提交行数占比饼图已保存为 'linesChangedByAuthor.png'")


    def analyze_data(self, config, commits):
        CommitsAnalyzer.result_dir = config["resultDir"]

        print("开始分析代码结构...")
        code_analysis = self.analyze_code_structure(f"{config['repoPath']}/models/yolo.py")
        print("代码分析结果:", code_analysis)

        print("正在可视化提交历史...")
        self.visualize_commit_history(commits)
        self.visualize_author(commits)
        self.visualize_linescommite(commits)
