import json
import os
from pathlib import Path
from datetime import datetime

class VOBDProblemModulesManager:
    """VOBD问题模块定义管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.json_path = os.path.join(self.root_dir, 'data', 'dicts', 'vobd_8_problem_modules.json')
        self.backup_dir = os.path.join(self.root_dir, 'data', 'dicts', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)

    def load_modules(self):
        """加载问题模块定义"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载问题模块定义失败: {str(e)}")
            return {}

    def save_modules(self, modules):
        """保存问题模块定义"""
        try:
            # 首先备份当前文件
            self._backup_current_file()
            
            # 保存新的定义
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(modules, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存问题模块定义失败: {str(e)}")
            return False

    def _backup_current_file(self):
        """备份当前的定义文件"""
        try:
            if os.path.exists(self.json_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(self.backup_dir, f'vobd_8_problem_modules_{timestamp}.json')
                with open(self.json_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False

    def add_module(self, module_id, description):
        """添加新的问题模块定义"""
        modules = self.load_modules()
        modules[module_id] = description
        return self.save_modules(modules)

    def remove_module(self, module_id):
        """删除问题模块定义"""
        modules = self.load_modules()
        if module_id in modules:
            del modules[module_id]
            return self.save_modules(modules)
        return False

    def update_module(self, module_id, new_description):
        """更新问题模块描述"""
        modules = self.load_modules()
        if module_id in modules:
            modules[module_id] = new_description
            return self.save_modules(modules)
        return False

    def get_all_modules(self):
        """获取所有问题模块定义"""
        return self.load_modules()

    def export_to_csv(self, output_path):
        """导出为CSV格式"""
        try:
            modules = self.load_modules()
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Module ID,Description\n")
                for module_id, desc in modules.items():
                    f.write(f'"{module_id}","{desc}"\n')
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
                    module_id, description = line.strip().split(',', 1)
                    modules[module_id.strip('"')] = description.strip('"')
            return self.save_modules(modules)
        except Exception as e:
            print(f"从CSV导入失败: {str(e)}")
            return False 