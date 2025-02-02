"""
VMkernel 模块管理器

这个模块负责管理 VMkernel 日志分析中的模块定义。
主要功能：
1. 加载和保存模块定义
2. 添加和删除模块
3. 导出模块定义
4. 验证模块配置

处理流程：
1. 从 JSON 文件加载模块定义
2. 提供模块管理接口
3. 保存更改到文件
4. 支持导出功能
"""

import json
import os
import csv
from pathlib import Path
from datetime import datetime

class VMKModulesManager:
    """
    VMkernel 模块管理器类
    
    主要职责：
    - 管理模块定义文件
    - 提供模块增删改查接口
    - 验证模块配置
    - 支持配置导出
    
    属性：
    - root_dir: 项目根目录
    - module_file: 模块定义文件路径
    - modules: 模块配置字典
    """
    
    def __init__(self):
        """
        初始化模块管理器
        
        功能：
        1. 确定项目根目录
        2. 加载模块定义文件
        3. 初始化模块配置
        """
        # 获取项目根目录
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.module_file = os.path.join(self.root_dir, 'data', 'dicts', 'vmk_8_mod.json')
        self.backup_dir = os.path.join(self.root_dir, 'data', 'dicts', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)

        # 默认的模块类别
        self.default_categories = {
            'STORAGE': [
                'NMP', 'ScsiPath', 'Scsi', 'VMFS', 'LVM', 'StorageDevice',
                'StorageDeviceIO', 'StorageDM', 'UNMAP', 'UNMAP6'
            ],
            'NETWORK': [
                'NetPort', 'NetStack', 'NetPkt', 'NetDev', 'VMXNET3'
            ],
            'SYSTEM': [
                'SystemMem', 'SystemBus', 'SystemCPU', 'SystemIO'
            ],
            'VSAN': [
                'VSAN', 'VSANHealth', 'VSANPerf'
            ],
            'VM': [
                'VMkernel', 'VMkernelBoot', 'VMkernelInit'
            ]
        }

        # 加载模块定义，如果失败则使用默认配置
        self.modules = self._load_modules()
        if not self.modules:
            self.modules = self.default_categories.copy()
            self._save_modules()  # 保存默认配置到文件

    def _load_modules(self):
        """
        从 JSON 文件加载模块定义
        
        返回：
            dict: 模块配置字典，如果加载失败则返回空字典
        """
        try:
            with open(self.module_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模块定义时发生错误: {str(e)}")
            return {}

    def _save_modules(self):
        """
        保存模块定义到 JSON 文件
        
        返回：
            bool: 保存成功返回 True，失败返回 False
        """
        try:
            # 首先备份当前文件
            self._backup_current_file()
            
            # 保存新的定义
            with open(self.module_file, 'w', encoding='utf-8') as f:
                json.dump(self.modules, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存模块定义失败: {str(e)}")
            return False

    def _backup_current_file(self):
        """备份当前的定义文件"""
        try:
            if os.path.exists(self.module_file):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = os.path.join(self.backup_dir, f'vmk_8_mod_{timestamp}.json')
                with open(self.module_file, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                return True
        except Exception as e:
            print(f"备份文件失败: {str(e)}")
            return False

    def get_all_modules(self):
        """
        获取所有模块定义
        
        返回：
            dict: 完整的模块配置字典
        """
        return self.modules

    def add_module(self, category, module_name):
        """
        添加新模块到指定类别
        
        参数：
            category (str): 模块类别
            module_name (str): 模块名称
            
        返回：
            bool: 添加成功返回 True，失败返回 False
        """
        try:
            if category not in self.modules:
                print(f"无效的类别: {category}")
                return False
            
            if module_name in self.modules[category]:
                print(f"模块 {module_name} 已存在于 {category}")
                return False
            
            self.modules[category].append(module_name)
            return self._save_modules()
            
        except Exception as e:
            print(f"添加模块时发生错误: {str(e)}")
            return False

    def remove_module(self, category, module_name):
        """
        从指定类别移除模块
        
        参数：
            category (str): 模块类别
            module_name (str): 模块名称
            
        返回：
            bool: 移除成功返回 True，失败返回 False
        """
        try:
            if category not in self.modules:
                print(f"无效的类别: {category}")
                return False
            
            if module_name not in self.modules[category]:
                print(f"模块 {module_name} 不存在于 {category}")
                return False
            
            self.modules[category].remove(module_name)
            return self._save_modules()
            
        except Exception as e:
            print(f"移除模块时发生错误: {str(e)}")
            return False

    def export_to_csv(self, output_file=None):
        """
        导出模块定义到 CSV 文件
        
        参数：
            output_file (str, optional): 输出文件路径
            
        返回：
            bool: 导出成功返回 True，失败返回 False
        """
        try:
            if not output_file:
                # 生成默认输出文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = os.path.join(self.root_dir, 'data', 'dicts', 'exports')
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f'vmk_modules_{timestamp}.csv')
            
            # 准备导出数据
            export_data = []
            for category, modules in self.modules.items():
                for module in modules:
                    export_data.append([category, module])
            
            # 写入 CSV 文件
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Module'])  # 写入表头
                writer.writerows(export_data)
            
            print(f"模块定义已导出到: {output_file}")
            return True
            
        except Exception as e:
            print(f"导出模块定义时发生错误: {str(e)}")
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
                
            return self._save_modules()
        except Exception as e:
            print(f"从CSV导入失败: {str(e)}")
            return False

    def add_modules_batch(self, category, module_names):
        """
        批量添加模块到指定类别
        
        参数：
            category (str): 模块类别
            module_names (list): 模块名称列表
            
        返回：
            tuple: (成功添加的数量, 总数量)
        """
        try:
            if category not in self.modules:
                print(f"无效的类别: {category}")
                return (0, len(module_names))
            
            success_count = 0
            for module_name in module_names:
                module_name = module_name.strip()
                if module_name and module_name not in self.modules[category]:
                    self.modules[category].append(module_name)
                    success_count += 1
            
            # 对模块列表进行排序
            self.modules[category].sort()
            
            # 只在有变更时保存
            if success_count > 0:
                self._save_modules()
            
            return (success_count, len(module_names))
            
        except Exception as e:
            print(f"批量添加模块时发生错误: {str(e)}")
            return (0, len(module_names)) 