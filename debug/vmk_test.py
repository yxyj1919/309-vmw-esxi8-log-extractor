from app.processors.vmk.vmk_8_log_1_processor import VMK8LogProcessor

def main():
    """主函数：用于测试日志处理"""
    # 测试样例
    test_logs = [
        "2025-01-20T01:44:25.919Z Al(177) vmkalert: cpu66:2097709)ALERT: <NMLX_ERR> nmlx5_coreQueryTir:268 command failed: IO was aborted",
        "2025-01-20T16:36:19.937Z Wa(180) vmkwarning: cpu68:2098009)WARNING: HBX: 2723: Failed to cleanup registration key on volume655e5791-756c32d5-6a9f-1423f230bfe0: Failure",
        "2025-01-23T22:10:20Z In(182) vmkernel: 9127.5:D:Disable PCIe VDM on PF0",
        "2025-01-20T16:36:35.796Z In(182) vmkernel: cpu63:2099984 opID=be121f44)SchedVsi: 2208: Group: host/user/pool4(3449396): min=64382 max=130475 minLimit=64382 shares=34847, units: mb"
    ]
    
    processor = VMK8LogProcessor()
    
    # 测试单行处理
    print("测试单行日志处理：")
    print("-" * 80)
    for i, log in enumerate(test_logs, 1):
        print(f"\n测试用例 {i}:")
        print(f"原始日志: {log}")
        result = processor.process_log_line(log)
        if result:  # 只处理非None的结果
            print("解析结果:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("该日志被过滤掉（不符合过滤条件）")
        print("-" * 80)
    
    # 测试文件处理
    print("\n测试日志文件处理：")
    print("-" * 80)
    try:
        # df = processor.process_log_file("vmkernel-8-test.log")
        df = processor.process_log_file("./logs/vmkernel-8-storage-ran.all")
        if not df.empty:
            print("\n处理结果预览（已过滤）：")
            print(df.head())
            print(f"\n总共保留了 {len(df)} 条日志记录")
        else:
            print("没有找到符合条件的日志记录")
    except FileNotFoundError:
        print("警告：测试文件不存在")

if __name__ == "__main__":
    main()
