import os
import subprocess
import cProfile
import pstats
import logging
import time
import psutil
import tracemalloc
import threading
from io import StringIO


class DynamicAnalyser():
    @staticmethod
    def setup_logging(result_dir):
        # 设置日志配置
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[logging.FileHandler(f'{result_dir}/dynamic_analysis.log', 'w', 'utf-8'),
                                      logging.StreamHandler()])
        logging.info("日志记录已启用.")

    @staticmethod
    def log_resources():
        # 记录系统资源消耗（CPU、内存等）
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        logging.info(f"CPU 使用率：{cpu_percent}%")
        logging.info(f"内存使用：{memory.percent}%")

    @staticmethod
    def monitor_memory():
        # 使用 tracemalloc 跟踪内存使用
        tracemalloc.start()
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        logging.info("内存使用情况：")
        for stat in top_stats[:5]: 
            logging.info(stat)

    @staticmethod
    def run_cprofile(repoPath, resultDir):
        print("正在使用cProfile进行动态分析...")
        profiler = cProfile.Profile()

        scripts = ['train.py', 'detect.py']
        for script in scripts:
            script_path = os.path.join(repoPath, script)

            start_time = time.time()
            # 每分钟记录一次资源使用情况
            DynamicAnalyser.log_resources()

            print(f"正在分析 {script} ...")
            profiler.enable()
            subprocess.run(['python', script_path])
            profiler.disable()

            # 性能时间统计
            end_time = time.time()
            logging.info(f"{script} 执行时间：{end_time - start_time:.2f} 秒")
            DynamicAnalyser.log_resources()

            # 保存 cProfile 分析报告
            stats = StringIO()
            pstats.Stats(profiler, stream=stats).sort_stats('cumulative').print_stats(20)

            # 写入报告文件
            report_file = f'{resultDir}/cprofile_{script}_report.txt'
            with open(report_file, 'w') as f:
                f.write(stats.getvalue())

            print(f"{script} 的 cProfile 报告已保存为 {report_file}.")
            logging.info(f"{script} 的 cProfile 报告已保存为 {report_file}.")

        print("所有 cProfile 分析报告已完成.")

    @staticmethod
    def periodically_log_resources(interval=60):
        # 每隔指定时间（秒）调用一次log_resources
        def log():
            DynamicAnalyser.log_resources()
            threading.Timer(interval, log).start()  # 定时器会继续调用自己，实现循环

        log()  # 启动定时日志记录

    def run_dynamic_analysis(repo_path, result_dir):
        DynamicAnalyser.setup_logging(result_dir)  # 启用日志记录

        # 启动定时记录资源
        DynamicAnalyser.periodically_log_resources(interval=60)

        print("运行 cProfile 分析...")
        DynamicAnalyser.run_cprofile(repo_path, result_dir)

        print("监控内存...")
        DynamicAnalyser.monitor_memory()

