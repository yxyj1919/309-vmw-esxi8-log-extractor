from app.processors.vmk.vmk_8_log_1_processor import VMK8LogProcessor
from app.processors.vmk.vmk_8_log_2_filter import VMK8LogFilter
from app.processors.vmk.vmk_8_log_3_refine import VMK8LogRefiner
import os

def main():
    """
    主函数：按顺序执行三个处理步骤
    
    处理流程：
    1. 基础处理：解析日志文件，提取关键字段（时间、标签、级别、CPU、模块等）
    2. 过滤处理：提取包含模块信息的日志，去除无模块信息的记录
    3. 细化处理：按模块类别（STORAGE/NETWORK/SYSTEM等）分类
    
    输出文件：
    - 步骤1：{timestamp}-vmk-basic-1-processed.csv  # 基础处理结果
    - 步骤2：{timestamp}-vmk-basic-2-filtered.csv   # 过滤后结果
    - 步骤3：{timestamp}-vmk-basic-3-refined-{category}.csv  # 各类别结果
    """
    # 输入日志文件路径（需要处理的vmkernel日志文件）
    input_log = "./logs/vmkernel-8-storage-ran.all"
    
    # === 步骤 1: 基础日志处理 ===
    print("\n=== 步骤 1: 基础日志处理 ===")
    processor = VMK8LogProcessor()  # 创建基础处理器实例
    df_processed = processor.process_log_file(input_log)  # 处理原始日志文件
    if df_processed.empty:
        print("基础处理失败，程序终止")
        return
    
    # === 步骤 2: 日志过滤 ===
    print("\n=== 步骤 2: 日志过滤 ===")
    filter = VMK8LogFilter()  # 创建过滤器实例
    df_filtered = filter.filter_logs(input_log)  # 过滤日志，只保留有模块信息的记录
    if df_filtered.empty:
        print("过滤处理失败，程序终止")
        return
    
    # === 步骤 3: 按类别细化 ===
    print("\n=== 步骤 3: 按类别细化 ===")
    refiner = VMK8LogRefiner()  # 创建细化处理器实例
    
    # 在output目录中查找过滤后的文件
    output_dir = 'output'
    # 获取所有以'-vmk-basic-2-filtered.csv'结尾的文件
    filtered_files = [f for f in os.listdir(output_dir) if f.endswith('-vmk-basic-2-filtered.csv')]
    if not filtered_files:
        print("未找到过滤后的文件，程序终止")
        return
    
    # 选择最新的过滤文件作为输入（按文件名排序，取最新的）
    latest_filtered = sorted(filtered_files)[-1]
    input_csv = os.path.join(output_dir, latest_filtered)
    
    # 执行细化处理，按模块类别分类
    category_dfs = refiner.process_by_category(input_csv)
    
    # === 打印最终的处理统计信息 ===
    print("\n=== 处理完成 ===")
    # 显示每个步骤处理的记录数
    print(f"1. 基础处理: {len(df_processed)} 条记录")
    print(f"2. 过滤处理: {len(df_filtered)} 条记录")
    print("\n3. 细化处理结果:")
    # 显示每个类别的记录数
    for category, df in category_dfs.items():
        if not df.empty:
            print(f"  - {category}: {len(df)} 条记录")

if __name__ == "__main__":
    main()