from app.processors.vmkw.vmkw_8_log_processor import VMKWLogProcessor

def main():
    """
    主函数：用于测试日志处理器
    """
    processor = VMKWLogProcessor()
    
    # 测试单行日志处理
    print("测试单行日志处理：")
    print("-" * 80)
    test_logs = [
        "2025-01-19T19:12:20.060Z Wa(180) vmkwarning: cpu32:2098009)WARNING: Vol3: 4678: Error closing the volume: . Eviction fails: Failure",
        "2025-01-19T19:12:20.894Z Al(177) vmkalert: cpu66:2097709)ALERT: <NMLX_ERR> nmlx5_coreQueryTir:268 command failed: IO was aborted"
    ]
    
    for i, log in enumerate(test_logs, 1):
        print(f"\n测试用例 {i}:")
        print(f"原始日志: {log}")
        result = processor.process_log_line(log)
        print("解析结果:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print("-" * 80)
    
    # 测试文件处理
    # 注意：需要确保test.log文件存在
    print("\n测试日志文件处理：")
    print("-" * 80)
    try:
        #df = processor.process_log_file("./logs/vmkwarning-8-storage-ran.all")
        df = processor.process_log_file("./logs/vmkernel-8.storage-ran.all")
        print("\n处理结果预览：")
        print(df.head())
    except FileNotFoundError:
        print("警告：测试文件 'test.log' 不存在")

if __name__ == "__main__":
    main()