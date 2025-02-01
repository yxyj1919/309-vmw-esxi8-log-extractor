import json
import os
from pathlib import Path
from datetime import datetime

class VMKModulesManager:
    """VMKernel模块定义管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.json_path = os.path.join(self.root_dir, 'data', 'dicts', 'vmk_8_mod.json')
        self.backup_dir = os.path.join(self.root_dir, 'data', 'dicts', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)

        self.modules = {
            'STORAGE': [
                'UNMAP',  # 需要确保这个存在
                'UNMAP6',  # 可能需要添加这个
                # ... 其他存储模块
            ],
            # ... 其他类别
        }

    def load_modules(self):
        """加载模块定义"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模块定义失败: {str(e)}")
            return {}

    def save_modules(self, modules):
        """保存模块定义"""
        try:
            # 首先备份当前文件
            self._backup_current_file()
            
            # 保存新的定义
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(modules, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存模块定义失败: {str(e)}")
            return False

    def _backup_current_file(self):
        """备份当前的定义文件"""
        try:
            if os.path.exists(self.json_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(self.backup_dir, f'vmk_8_mod_{timestamp}.json')
                with open(self.json_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False

    def add_module(self, category, module_name):
        """添加新的模块"""
        modules = self.load_modules()
        if category in modules:
            # 转换为大写以保持一致性
            module_name = module_name.upper()
            if module_name not in modules[category]:
                modules[category].append(module_name)
                modules[category].sort()  # 保持列表有序
                return self.save_modules(modules)
        return False

    def remove_module(self, category, module_name):
        """删除模块"""
        modules = self.load_modules()
        if category in modules and module_name in modules[category]:
            modules[category].remove(module_name)
            return self.save_modules(modules)
        return False

    def get_all_modules(self):
        """获取所有模块定义"""
        return self.load_modules()

    def export_to_csv(self, output_path):
        """导出为CSV格式"""
        try:
            modules = self.load_modules()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Category,Module\n")
                for category, module_list in modules.items():
                    for module in module_list:
                        f.write(f'"{category}","{module}"\n')
            return True
        except Exception as e:
            print(f"导出CSV失败: {str(e)}")
            return False

    def import_from_csv(self, csv_path):
        """从CSV导入"""
        try:
            modules = {}
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]  # 跳过标题行
                for line in lines:
                    category, module = line.strip().split(',', 1)
                    category = category.strip('"')
                    module = module.strip('"')
                    if category not in modules:
                        modules[category] = []
                    if module not in modules[category]:
                        modules[category].append(module)
            
            # 对每个类别的模块列表进行排序
            for category in modules:
                modules[category].sort()
                
            return self.save_modules(modules)
        except Exception as e:
            print(f"从CSV导入失败: {str(e)}")
            return False 