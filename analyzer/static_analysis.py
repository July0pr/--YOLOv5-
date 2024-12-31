import subprocess
import ast
import os
import graphviz

class StaticAnalyser():
    @staticmethod
    def run_pylint(repoPath, resultDir):
        print("正在使用Pylint进行静态分析...")
        pylint_cmd = f'pylint {repoPath}/**/*.py --output-format=json > {resultDir}/pylint_report.json'
        subprocess.run(pylint_cmd, shell=True)
        print("Pylint报告已保存至pylint_report.json.")

    @staticmethod
    def analyze_classes_and_generate_graph(repoPath, resultDir):
        print("正在分析类和生成类依赖关系图...")
        
        class_info, dependencies = StaticAnalyser.analyze_classes(repoPath)
        StaticAnalyser.generate_class_dependency_graph(class_info, dependencies, resultDir)

    @staticmethod
    def analyze_classes(directory):
        class_info = {}
        dependencies = set()

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'): 
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                class_name = node.name
                                base_classes = [base.id for base in node.bases if isinstance(base, ast.Name)]
                                class_info[class_name] = base_classes
                                
                                # 记录依赖关系
                                for base_class in base_classes:
                                    dependencies.add((base_class, class_name))

                            if isinstance(node, ast.ImportFrom):
                                if node.module:
                                    for alias in node.names:
                                        dependencies.add((file, alias.name))  
                            elif isinstance(node, ast.Import):
                                for alias in node.names:
                                    dependencies.add((file, alias.name)) 

        return class_info, dependencies

    @staticmethod
    def generate_class_dependency_graph(class_info, dependencies, resultDir):
        graph = graphviz.Digraph(format='png', engine='dot')

        # 设置图的整体属性
        graph.attr(
            dpi='300',           
            style='filled',         
            color='lightyellow',   
            fontsize='12',           
            nodesep='1',             
            ranksep='2',            
            rankdir='LR'             
        )

        # 设置节点的大小
        graph.node_attr.update(
            width='2',              
            height='1',             
            fontsize='16',          
            penwidth='2'            
        )

        # 绘制类与父类的继承关系
        for class_name, base_classes in class_info.items():
            for base in base_classes:
                graph.edge(base, class_name, constraint='true')

        # 绘制文件到模块的依赖关系
        for dependency in dependencies:
            graph.edge(dependency[0], dependency[1], constraint='false')

        output_file = os.path.join(resultDir, 'yolov5_class_dependencies')
        graph.render(output_file)
        print(f"类依赖关系图已生成: {output_file}.png")

    def run_staic_analysis(repoPath, resultDir):
        StaticAnalyser.run_pylint(repoPath, resultDir)
        StaticAnalyser.analyze_classes_and_generate_graph(repoPath, resultDir)