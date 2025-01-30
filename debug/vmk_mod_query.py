import json

def load_vmk_data():
    with open('vmk_mod.json', 'r') as file:
        return json.load(file)

def query_vmk_mod():
    data = load_vmk_data()
    
    # 显示所有可用的 KEY
    print("可用的类别：")
    for key in data.keys():
        print(f"- {key}")
    
    while True:
        # 获取用户输入
        key = input("\n请输入要查询的类别 (输入 'q' 退出): ").strip().upper()
        
        if key.lower() == 'q':
            print("程序已退出")
            break
            
        if key in data:
            print(f"\n{key} 类别下的模块：")
            for index, item in enumerate(data[key], 1):
                print(f"{index}. {item}")
        else:
            print(f"未找到类别 '{key}'，请检查输入是否正确")

if __name__ == "__main__":
    try:
        query_vmk_mod()
    except FileNotFoundError:
        print("错误：找不到 vmk_mod.json 文件，请确保文件在正确的位置")
    except json.JSONDecodeError:
        print("错误：vmk_mod.json 文件格式不正确")
    except Exception as e:
        print(f"发生错误：{str(e)}") 