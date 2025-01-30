from processors.vobd.vobd_8_log_2_filter import VOBD8LogFilter
from app.processors.vobd.vobd_8_log_1_processor import VOBD8LogProcessor
import os
from datetime import datetime

def main():
    start_time = datetime.now()
    
    # 获取项目根目录的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置输入输出目录
    logs_dir = os.path.join(base_dir, 'logs')
    output_dir = os.path.join(base_dir, 'output')
    
    # 确保目录存在
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建日志处理器实例
    processor = VOBD8LogProcessor(base_dir)
    
    # 设置日志文件路径
    #log_file = os.path.join(logs_dir, 'vobd.all')
    log_file = os.path.join(logs_dir, 'vobd-8.log')
    
    # 检查文件是否存在
    if not os.path.exists(log_file):
        print(f"错误: 找不到日志文件 {log_file}")
        print(f"请确保日志文件 'vobd.all' 位于 {logs_dir} 目录下")
        return

    # 检查文件是否为空
    if os.path.getsize(log_file) == 0:
        print(f"错误: 日志文件为空 {log_file}")
        return
        
    print(f"使用日志文件: {log_file}")
    
    # 处理日志文件
    df = processor.process_log_file(log_file)
    
    if df is not None:
        # 创建过滤器实例并过滤问题日志
        filter = VOBD8LogFilter()
        filtered_df = filter.filter_problems(df)
        
        if len(filtered_df) == 0:
            print("警告: 没有找到任何问题日志")
            return

        print("\n" + "="*50)
        print("日志处理报告")
        print("="*50)
        print(f"原始日志总数: {len(df):,} 条")
        print(f"过滤后的问题日志总数: {len(filtered_df):,} 条")
        print(f"过滤率: {len(filtered_df)/len(df)*100:.2f}%")
        print("="*50 + "\n")
        
        print("\n原始日志示例:")
        print(df.head())
        
        print("\n过滤后的问题日志示例:")
        print(filtered_df.head())
        
        # 修改这里的列名检查
        if 'CompleteLog' not in filtered_df.columns:
            print("错误: 找不到 'CompleteLog' 列")
            print("可用的列:", filtered_df.columns.tolist())
            return
        
        # 创建输出目录
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n输出目录已创建/确认: {output_dir}")
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f'{timestamp}_vobd'
        csv_file = os.path.join(output_dir, f'{base_name}_problems.csv')
        log_file = os.path.join(output_dir, f'{base_name}_problems.log')
        
        print(f"将创建的文件:")
        print(f"CSV文件: {csv_file}")
        print(f"LOG文件: {log_file}")
        
        # 保存过滤后的结果到CSV
        filtered_df.to_csv(csv_file, index=False)
        print(f"\nCSV文件已保存: {csv_file}")
        
        # 保存完整日志内容到LOG文件
        try:
            print(f"\n开始写入日志文件: {log_file}")
            print(f"要写入的日志条数: {len(filtered_df)}")
            
            # 修改这里的列名引用
            first_log = filtered_df['CompleteLog'].iloc[0]
            print(f"第一条日志内容示例: {first_log}")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                # 修改这里的列名引用
                for index, log_entry in enumerate(filtered_df['CompleteLog'], 1):
                    f.write(f"{log_entry}\n")
                    if index % 100 == 0:
                        print(f"已写入 {index} 条日志...")
                        
            # 验证文件是否创建成功
            if os.path.exists(log_file):
                print(f"日志文件创建成功: {log_file}")
                print(f"文件大小: {os.path.getsize(log_file)} 字节")
            else:
                print(f"错误: 日志文件未能创建: {log_file}")
                
            print(f"日志写入完成，共写入 {len(filtered_df)} 条记录")
        except Exception as e:
            print(f"写入日志文件时出错: {str(e)}")
            import traceback
            print("详细错误信息:")
            print(traceback.format_exc())

    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n程序执行完成，总耗时: {duration}")

if __name__ == "__main__":
    main()