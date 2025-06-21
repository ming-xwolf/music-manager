#!/usr/bin/env python3
"""
音频文件管理器核心逻辑
处理音频文件的识别、分析和重命名
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from pypinyin import lazy_pinyin, Style

# GenAI相关导入
try:
    from genai.config import ConfigManager
    from genai.deepseek_provider import DeepseekProvider
    from genai.ollama_provider import OllamaProvider
    from genai.filename_analyzer import FilenameAnalyzer
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    ConfigManager = None
    DeepseekProvider = None
    OllamaProvider = None
    FilenameAnalyzer = None


class AudioFileManager:
    """音频文件管理器核心逻辑类"""
    
    AUDIO_EXTENSIONS = {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', 
        '.wma', '.opus', '.aiff', '.au', '.ra', '.mp2'
    }
    
    def __init__(self):
        self.current_folder = ""
        self.audio_files = []
        
        # 初始化GenAI组件
        self.config_manager = None
        self.filename_analyzer = None
        self._init_genai()
        
    def _init_genai(self):
        """初始化GenAI功能"""
        if not GENAI_AVAILABLE:
            return
            
        try:
            self.config_manager = ConfigManager()
            
            # 如果GenAI启用，初始化文件名分析器
            if self.config_manager.is_enabled():
                provider_info = self.config_manager.get_active_provider_config()
                if provider_info:
                    provider_type = provider_info["provider"]
                    config = provider_info["config"]
                    
                    # 创建对应的LLM提供者
                    if provider_type == "deepseek":
                        llm_provider = DeepseekProvider(
                            api_key=config.api_key,
                            api_base=config.api_base,
                            model=config.model,
                            config_manager=self.config_manager
                        )
                    elif provider_type == "ollama":
                        llm_provider = OllamaProvider(
                            api_base=config.api_base,
                            model=config.model,
                            config_manager=self.config_manager
                        )
                    else:
                        return
                        
                    self.filename_analyzer = FilenameAnalyzer(llm_provider, self.config_manager)
                    
        except Exception as e:
            # GenAI初始化失败，继续使用基本功能
            self.config_manager = None
            self.filename_analyzer = None
            
    def is_genai_enabled(self) -> bool:
        """检查GenAI功能是否可用"""
        return (GENAI_AVAILABLE and 
                self.config_manager is not None and 
                self.config_manager.is_enabled() and
                self.filename_analyzer is not None)
                
    def get_genai_status(self) -> Dict[str, str]:
        """获取GenAI状态信息"""
        if not GENAI_AVAILABLE:
            return {
                "status": "unavailable",
                "message": "GenAI模块不可用"
            }
            
        if self.config_manager is None:
            return {
                "status": "not_configured",
                "message": "GenAI未配置"
            }
            
        if not self.config_manager.is_enabled():
            return {
                "status": "disabled",
                "message": "GenAI功能已禁用"
            }
            
        if self.filename_analyzer is None:
            return {
                "status": "no_provider",
                "message": "没有可用的LLM提供者"
            }
            
        # 检查提供者是否可用
        try:
            provider_available = self.filename_analyzer.llm_provider.is_available()
            if provider_available:
                provider_name = self.filename_analyzer.llm_provider.get_provider_name()
                return {
                    "status": "available",
                    "message": f"GenAI可用 ({provider_name})"
                }
            else:
                provider_name = self.filename_analyzer.llm_provider.get_provider_name()
                return {
                    "status": "provider_unavailable",
                    "message": f"{provider_name} 服务不可用"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"检查服务状态时出错: {str(e)}"
            }

    def is_audio_file(self, filename: str) -> bool:
        """检查文件是否为音频文件"""
        ext = Path(filename).suffix.lower()
        return ext in self.AUDIO_EXTENSIONS
    
    def has_number_prefix(self, filename: str) -> bool:
        """检查文件名是否已有数字前缀"""
        pattern = r'^\d+-'
        return bool(re.match(pattern, filename))
    
    def extract_number_from_prefix(self, filename: str) -> int:
        """从文件名前缀提取数字"""
        match = re.match(r'^(\d+)-', filename)
        return int(match.group(1)) if match else None
    
    def get_clean_filename(self, filename: str) -> str:
        """获取去除序号前缀的文件名，用于排序"""
        if self.has_number_prefix(filename):
            # 移除序号前缀
            return re.sub(r'^\d+-', '', filename)
        return filename
    
    def get_pinyin_sort_key(self, filename: str) -> str:
        """获取用于拼音排序的键值"""
        clean_name = self.get_clean_filename(filename)
        # 去除扩展名进行拼音转换
        name_without_ext = Path(clean_name).stem
        
        # 将汉字转换为拼音，用于排序
        pinyin_list = lazy_pinyin(name_without_ext, style=Style.NORMAL)
        # 将拼音列表转换为字符串，用空格连接
        pinyin_str = ' '.join(pinyin_list)
        return pinyin_str.lower()
    
    def _get_llm_suggestion_sort_key(self, file_info: Dict) -> str:
        """
        获取LLM建议的排序键
        
        Args:
            file_info: 文件信息字典
            
        Returns:
            LLM建议的排序键
        """
        genai_analysis = file_info.get('genai_analysis')
        
        # 如果没有GenAI分析结果，使用原文件名
        if not genai_analysis:
            return self.get_pinyin_sort_key(file_info['original_name'])
        
        # 如果已经是标准格式，使用原文件名
        if genai_analysis.get('is_standard_format', False):
            return self.get_pinyin_sort_key(file_info['original_name'])
        
        # 如果有错误，将错误的文件排在最后
        if 'error' in genai_analysis:
            return 'zzz_error_' + self.get_pinyin_sort_key(file_info['original_name'])
        
        # 使用LLM建议的文件名
        suggested_name = genai_analysis.get('suggested_name', '')
        if suggested_name:
            try:
                # 使用拼音排序
                pinyin_list = lazy_pinyin(suggested_name, style=Style.NORMAL)
                return ' '.join(pinyin_list).lower()
            except:
                return suggested_name.lower()
        
        # 如果没有建议，使用原文件名
        return self.get_pinyin_sort_key(file_info['original_name'])
    
    def get_audio_files(self, folder_path: str) -> List[str]:
        """获取文件夹中的所有音频文件"""
        try:
            audio_files = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path) and self.is_audio_file(item):
                    audio_files.append(item)
            return audio_files
        except Exception as e:
            return []
    
    def get_file_info(self, folder_path: str, filename: str) -> Dict:
        """获取文件的详细信息"""
        file_path = os.path.join(folder_path, filename)
        try:
            stat = os.stat(file_path)
            return {
                'name': filename,
                'size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'path': file_path
            }
        except Exception as e:
            return {
                'name': filename,
                'size': 0,
                'created_time': 0,
                'modified_time': 0,
                'path': file_path
            }
    
    def sort_files(self, folder_path: str, filenames: List[str], sort_method: str) -> List[str]:
        """根据指定方法对文件进行排序"""
        if not filenames:
            return []
        
        # 获取所有文件的详细信息
        file_infos = []
        for filename in filenames:
            info = self.get_file_info(folder_path, filename)
            # 添加去除序号前缀的文件名，用于文件名排序
            info['clean_name'] = self.get_clean_filename(filename)
            file_infos.append(info)
        
        # 根据排序方法进行排序
        sort_key_map = {
            "文件名称 (A-Z)": lambda x: self.get_pinyin_sort_key(x['name']),  # 使用拼音排序
            "文件名称 (Z-A)": lambda x: self.get_pinyin_sort_key(x['name']),  # 使用拼音排序
            "文件大小 (小到大)": lambda x: x['size'],
            "文件大小 (大到小)": lambda x: x['size']
        }
        
        reverse_methods = {
            "文件名称 (Z-A)", 
            "文件大小 (大到小)"
        }
        
        sort_key = sort_key_map.get(sort_method, lambda x: x['clean_name'].lower())
        reverse = sort_method in reverse_methods
        
        file_infos.sort(key=sort_key, reverse=reverse)
        return [info['name'] for info in file_infos]
    
    def analyze_files(self, folder_path: str, sort_method: str = "文件名称 (A-Z)", progress_callback=None) -> Dict:
        """分析文件夹中的音频文件状态"""
        if progress_callback:
            progress_callback(0, "开始分析...")
            
        audio_files = self.get_audio_files(folder_path)
        
        if progress_callback:
            progress_callback(10, f"发现 {len(audio_files)} 个音频文件")
            
        # 根据用户选择的方法排序
        audio_files = self.sort_files(folder_path, audio_files, sort_method)
        
        if progress_callback:
            progress_callback(20, "文件排序完成")
        
        result = {
            'total_files': len(audio_files),
            'files': [],
            'needs_renaming': False,
            'has_gaps': False,
            'duplicate_numbers': False,
            'folder_path': folder_path,
            'needs_rename_count': 0,
            'sort_method': sort_method  # 保存排序方式，用于生成建议文件名
        }
        
        used_numbers = set()
        total_files = len(audio_files)
        
        for i, filename in enumerate(audio_files):
            if progress_callback:
                progress = 20 + int((i / total_files) * 30)  # 20-50%
                progress_callback(progress, f"分析文件: {filename}")
                
            # 获取文件的详细信息
            file_details = self.get_file_info(folder_path, filename)
            
            file_info = {
                'original_name': filename,
                'has_prefix': self.has_number_prefix(filename),
                'suggested_name': '',
                'status': 'ok',
                'size': file_details['size'],
                'created_time': file_details['created_time'],
                'modified_time': file_details['modified_time'],
                # GenAI相关字段
                'genai_analysis': None,
                'llm_suggested_name': None,
                'needs_genai_analysis': False
            }
            
            if file_info['has_prefix']:
                number = self.extract_number_from_prefix(filename)
                if number in used_numbers:
                    file_info['status'] = 'duplicate_number'
                    result['duplicate_numbers'] = True
                else:
                    used_numbers.add(number)
            else:
                file_info['status'] = 'no_prefix'
                result['needs_renaming'] = True
            
            result['files'].append(file_info)
        
        if progress_callback:
            progress_callback(50, "检查编号连续性...")
            
        # 检查编号是否连续
        if used_numbers:
            expected_numbers = set(range(1, max(used_numbers) + 1))
            if used_numbers != expected_numbers:
                result['has_gaps'] = True
        
        # 如果GenAI启用，先进行文件名分析
        if self.is_genai_enabled():
            if progress_callback:
                progress_callback(60, "使用AI分析文件名...")
            self._analyze_filenames_with_genai(result, progress_callback)
        
        if progress_callback:
            progress_callback(80, "生成建议文件名...")
            
        # 生成建议的文件名（根据排序方式）
        self._generate_suggested_names(result, folder_path)
        
        if progress_callback:
            progress_callback(90, "统计需要重命名的文件...")
            
        # 统计实际需要重命名的文件数量
        result['needs_rename_count'] = self._count_files_needing_rename(result)
        
        if progress_callback:
            progress_callback(100, "分析完成！")
        
        return result
    
    def _analyze_filenames_with_genai(self, result: Dict, progress_callback=None):
        """使用GenAI分析文件名"""
        if not self.filename_analyzer:
            return
            
        total_files = len(result['files'])
        
        for i, file_info in enumerate(result['files']):
            filename = file_info['original_name']
            
            if progress_callback:
                progress = 60 + int((i / total_files) * 20)  # 60-80%
                progress_callback(progress, f"AI分析文件名: {filename}")
            
            try:
                # 使用GenAI分析文件名
                analysis = self.filename_analyzer.analyze_filename(filename)
                file_info['genai_analysis'] = analysis
                
                # 如果分析成功且不是标准格式，记录LLM建议的文件名
                if analysis.get('needs_analysis', False) and not analysis.get('is_standard_format', False):
                    file_info['needs_genai_analysis'] = True
                    file_info['llm_suggested_name'] = analysis.get('suggested_name', '')
                elif analysis.get('is_standard_format', False):
                    # 已经是标准格式，不需要分析
                    file_info['needs_genai_analysis'] = False
                    
            except Exception as e:
                # 分析失败，记录错误
                file_info['genai_analysis'] = {
                    'error': f'分析失败: {str(e)}',
                    'needs_analysis': True,
                    'is_standard_format': False
                }
                file_info['needs_genai_analysis'] = True
    
    def _generate_suggested_names(self, result: Dict, folder_path: str):
        """为文件生成建议的文件名"""
        # 总是根据当前排序方式重新生成建议的文件名
        # 这样当用户改变排序方式时，序号会相应调整
        
        # 获取排序方式，按照用户选择的方式重新排序所有文件
        sort_method = result.get('sort_method', '文件名称 (A-Z)')
        
        # 创建文件信息列表，包含原文件名和去除前缀的文件名
        file_items = []
        for file_info in result['files']:
            clean_name = self.get_clean_filename(file_info['original_name'])
            file_items.append({
                'file_info': file_info,
                'clean_name': clean_name,
                'size': file_info['size'],
                'created_time': file_info['created_time'],
                'modified_time': file_info['modified_time']
            })
        
        # 根据排序方式对文件进行排序
        sort_key_map = {
            "LLM建议 (A-Z)": lambda x: self._get_llm_suggestion_sort_key(x['file_info']),
            "LLM建议 (Z-A)": lambda x: self._get_llm_suggestion_sort_key(x['file_info']),
            "文件名称 (A-Z)": lambda x: self.get_pinyin_sort_key(x['file_info']['original_name']),
            "文件名称 (Z-A)": lambda x: self.get_pinyin_sort_key(x['file_info']['original_name']),
            "文件大小 (小到大)": lambda x: x['size'],
            "文件大小 (大到小)": lambda x: x['size']
        }
        
        reverse_methods = {
            "LLM建议 (Z-A)",
            "文件名称 (Z-A)", 
            "文件大小 (大到小)"
        }
        
        sort_key = sort_key_map.get(sort_method, lambda x: x['clean_name'].lower())
        reverse = sort_method in reverse_methods
        
        # 按照用户选择的方式排序
        file_items.sort(key=sort_key, reverse=reverse)
        
        # 按照新的排序顺序分配序号
        for index, item in enumerate(file_items, 1):
            file_info = item['file_info']
            clean_name = item['clean_name']
            
            # 根据是否有GenAI建议来生成文件名
            if (self.is_genai_enabled() and 
                file_info.get('llm_suggested_name') and 
                file_info.get('needs_genai_analysis', False)):
                # 使用GenAI建议的文件名
                base_name = file_info['llm_suggested_name']
                # 保持原文件扩展名
                original_ext = Path(file_info['original_name']).suffix
                file_info['suggested_name'] = f"{index:02d}-{base_name}{original_ext}"
            else:
                # 使用传统方式：序号 + 去除前缀的原文件名
                file_info['suggested_name'] = f"{index:02d}-{clean_name}"
    
    def _count_files_needing_rename(self, result: Dict) -> int:
        """统计实际需要重命名的文件数量"""
        count = 0
        for file_info in result['files']:
            if file_info['original_name'] != file_info['suggested_name']:
                count += 1
        return count
    
    def rename_files(self, folder_path: str, file_mappings: Dict[str, str], progress_callback=None) -> Tuple[int, List[str]]:
        """重命名文件"""
        success_count = 0
        errors = []
        total_files = len(file_mappings)
        
        if progress_callback:
            progress_callback(0, "开始重命名文件...")
        
        # 两阶段重命名以避免文件名冲突
        temp_mappings = {}
        
        try:
            # 第一阶段：重命名为临时文件名
            for i, (original_name, new_name) in enumerate(file_mappings.items()):
                if progress_callback:
                    progress = int((i / total_files) * 50)  # 0-50%
                    progress_callback(progress, f"第一阶段: {original_name}")
                
                if original_name != new_name:
                    original_path = os.path.join(folder_path, original_name)
                    temp_name = f"__temp__{success_count}__" + new_name
                    temp_path = os.path.join(folder_path, temp_name)
                    
                    try:
                        os.rename(original_path, temp_path)
                        temp_mappings[temp_name] = new_name
                        success_count += 1
                    except Exception as e:
                        errors.append(f"重命名 {original_name} 失败: {str(e)}")
            
            if progress_callback:
                progress_callback(50, "第一阶段完成，开始第二阶段...")
            
            # 第二阶段：重命名为最终文件名
            for i, (temp_name, final_name) in enumerate(temp_mappings.items()):
                if progress_callback:
                    progress = 50 + int((i / len(temp_mappings)) * 50)  # 50-100%
                    progress_callback(progress, f"第二阶段: {final_name}")
                
                temp_path = os.path.join(folder_path, temp_name)
                final_path = os.path.join(folder_path, final_name)
                
                try:
                    os.rename(temp_path, final_path)
                except Exception as e:
                    errors.append(f"最终重命名 {temp_name} 失败: {str(e)}")
                    # 尝试恢复原始名称
                    try:
                        original_name = None
                        for orig, new in file_mappings.items():
                            if new == final_name:
                                original_name = orig
                                break
                        if original_name:
                            os.rename(temp_path, os.path.join(folder_path, original_name))
                    except:
                        pass
        
        except Exception as e:
            errors.append(f"重命名过程出错: {str(e)}")
        
        if progress_callback:
            progress_callback(100, "重命名完成！")
        
        return success_count, errors 