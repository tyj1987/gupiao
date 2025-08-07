#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自选股管理模块
支持自选股的添加、删除、分组管理和模拟交易
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, asdict
import uuid

@dataclass
class WatchStock:
    """自选股信息"""
    symbol: str
    name: str
    add_date: str
    add_price: float
    group_name: str = "默认分组"
    notes: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class StockGroup:
    """股票分组"""
    name: str
    description: str
    created_date: str
    stocks: List[str]  # 股票代码列表
    
    def to_dict(self):
        return asdict(self)

class WatchlistManager:
    """自选股管理器"""
    
    def __init__(self, data_dir: str = "data/watchlist"):
        """
        初始化自选股管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.watchlist_file = self.data_dir / "watchlist.json"
        self.groups_file = self.data_dir / "groups.json"
        
        # 初始化数据
        self.watchlist: Dict[str, WatchStock] = {}
        self.groups: Dict[str, StockGroup] = {}
        
        # 加载数据
        self.load_data()
        
        # 确保有默认分组
        if "默认分组" not in self.groups:
            self.create_group("默认分组", "系统默认分组")
    
    def load_data(self):
        """加载自选股数据"""
        try:
            # 加载自选股列表
            if self.watchlist_file.exists():
                with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.watchlist = {
                        symbol: WatchStock(**stock_data) 
                        for symbol, stock_data in data.items()
                    }
            
            # 加载分组信息
            if self.groups_file.exists():
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.groups = {
                        name: StockGroup(**group_data) 
                        for name, group_data in data.items()
                    }
            
            logger.info(f"已加载 {len(self.watchlist)} 只自选股，{len(self.groups)} 个分组")
            
        except Exception as e:
            logger.error(f"加载自选股数据失败: {e}")
    
    def save_data(self):
        """保存自选股数据"""
        try:
            # 保存自选股列表
            watchlist_data = {
                symbol: stock.to_dict() 
                for symbol, stock in self.watchlist.items()
            }
            with open(self.watchlist_file, 'w', encoding='utf-8') as f:
                json.dump(watchlist_data, f, ensure_ascii=False, indent=2)
            
            # 保存分组信息
            groups_data = {
                name: group.to_dict() 
                for name, group in self.groups.items()
            }
            with open(self.groups_file, 'w', encoding='utf-8') as f:
                json.dump(groups_data, f, ensure_ascii=False, indent=2)
            
            logger.info("自选股数据已保存")
            
        except Exception as e:
            logger.error(f"保存自选股数据失败: {e}")
    
    def add_stock(self, symbol: str, name: str, current_price: float, 
                  group_name: str = "默认分组", notes: str = "") -> bool:
        """
        添加股票到自选股
        
        Args:
            symbol: 股票代码
            name: 股票名称
            current_price: 当前价格
            group_name: 分组名称
            notes: 备注
            
        Returns:
            是否添加成功
        """
        try:
            if symbol in self.watchlist:
                logger.warning(f"股票 {symbol} 已在自选股中")
                return False
            
            # 确保分组存在
            if group_name not in self.groups:
                self.create_group(group_name, f"用户创建的分组 - {group_name}")
            
            # 创建自选股记录
            watch_stock = WatchStock(
                symbol=symbol,
                name=name,
                add_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                add_price=current_price,
                group_name=group_name,
                notes=notes
            )
            
            # 添加到自选股列表
            self.watchlist[symbol] = watch_stock
            
            # 添加到分组
            self.groups[group_name].stocks.append(symbol)
            
            # 保存数据
            self.save_data()
            
            logger.info(f"已添加股票到自选股: {symbol} - {name}")
            return True
            
        except Exception as e:
            logger.error(f"添加自选股失败: {e}")
            return False
    
    def remove_stock(self, symbol: str) -> bool:
        """
        从自选股中移除股票
        
        Args:
            symbol: 股票代码
            
        Returns:
            是否移除成功
        """
        try:
            if symbol not in self.watchlist:
                logger.warning(f"股票 {symbol} 不在自选股中")
                return False
            
            # 获取分组信息
            group_name = self.watchlist[symbol].group_name
            
            # 从自选股列表中移除
            del self.watchlist[symbol]
            
            # 从分组中移除
            if group_name in self.groups and symbol in self.groups[group_name].stocks:
                self.groups[group_name].stocks.remove(symbol)
            
            # 保存数据
            self.save_data()
            
            logger.info(f"已从自选股中移除: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"移除自选股失败: {e}")
            return False
    
    def create_group(self, name: str, description: str = "") -> bool:
        """
        创建股票分组
        
        Args:
            name: 分组名称
            description: 分组描述
            
        Returns:
            是否创建成功
        """
        try:
            if name in self.groups:
                logger.warning(f"分组 {name} 已存在")
                return False
            
            group = StockGroup(
                name=name,
                description=description,
                created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                stocks=[]
            )
            
            self.groups[name] = group
            self.save_data()
            
            logger.info(f"已创建分组: {name}")
            return True
            
        except Exception as e:
            logger.error(f"创建分组失败: {e}")
            return False
    
    def delete_group(self, name: str, move_to_default: bool = True) -> bool:
        """
        删除股票分组
        
        Args:
            name: 分组名称
            move_to_default: 是否将股票移至默认分组
            
        Returns:
            是否删除成功
        """
        try:
            if name not in self.groups:
                logger.warning(f"分组 {name} 不存在")
                return False
            
            if name == "默认分组":
                logger.warning("无法删除默认分组")
                return False
            
            # 处理分组中的股票
            if move_to_default:
                for symbol in self.groups[name].stocks:
                    if symbol in self.watchlist:
                        self.watchlist[symbol].group_name = "默认分组"
                        self.groups["默认分组"].stocks.append(symbol)
            else:
                # 删除分组中的所有股票
                for symbol in self.groups[name].stocks[:]:  # 创建副本避免修改时出错
                    self.remove_stock(symbol)
            
            # 删除分组
            del self.groups[name]
            self.save_data()
            
            logger.info(f"已删除分组: {name}")
            return True
            
        except Exception as e:
            logger.error(f"删除分组失败: {e}")
            return False
    
    def move_stock_to_group(self, symbol: str, target_group: str) -> bool:
        """
        将股票移动到指定分组
        
        Args:
            symbol: 股票代码
            target_group: 目标分组名称
            
        Returns:
            是否移动成功
        """
        try:
            if symbol not in self.watchlist:
                logger.warning(f"股票 {symbol} 不在自选股中")
                return False
            
            if target_group not in self.groups:
                logger.warning(f"目标分组 {target_group} 不存在")
                return False
            
            # 获取当前分组
            current_group = self.watchlist[symbol].group_name
            
            if current_group == target_group:
                logger.info(f"股票 {symbol} 已在目标分组 {target_group} 中")
                return True
            
            # 从当前分组中移除
            if current_group in self.groups and symbol in self.groups[current_group].stocks:
                self.groups[current_group].stocks.remove(symbol)
            
            # 添加到目标分组
            self.groups[target_group].stocks.append(symbol)
            
            # 更新股票的分组信息
            self.watchlist[symbol].group_name = target_group
            
            self.save_data()
            
            logger.info(f"已将股票 {symbol} 从 {current_group} 移动到 {target_group}")
            return True
            
        except Exception as e:
            logger.error(f"移动股票分组失败: {e}")
            return False
    
    def get_watchlist(self, group_name: Optional[str] = None) -> List[WatchStock]:
        """
        获取自选股列表
        
        Args:
            group_name: 分组名称，为None时返回所有股票
            
        Returns:
            自选股列表
        """
        if group_name is None:
            return list(self.watchlist.values())
        
        if group_name not in self.groups:
            return []
        
        return [
            self.watchlist[symbol] 
            for symbol in self.groups[group_name].stocks 
            if symbol in self.watchlist
        ]
    
    def get_groups(self) -> Dict[str, StockGroup]:
        """获取所有分组"""
        return self.groups.copy()
    
    def get_group_names(self) -> List[str]:
        """获取所有分组名称"""
        return list(self.groups.keys())
    
    def update_stock_notes(self, symbol: str, notes: str) -> bool:
        """
        更新股票备注
        
        Args:
            symbol: 股票代码
            notes: 新的备注内容
            
        Returns:
            是否更新成功
        """
        try:
            if symbol not in self.watchlist:
                logger.warning(f"股票 {symbol} 不在自选股中")
                return False
            
            self.watchlist[symbol].notes = notes
            self.save_data()
            
            logger.info(f"已更新股票 {symbol} 的备注")
            return True
            
        except Exception as e:
            logger.error(f"更新股票备注失败: {e}")
            return False
    
    def get_stock_count(self) -> int:
        """获取自选股总数"""
        return len(self.watchlist)
    
    def get_group_stock_count(self, group_name: str) -> int:
        """获取指定分组的股票数量"""
        if group_name not in self.groups:
            return 0
        return len(self.groups[group_name].stocks)
    
    def search_stocks(self, keyword: str) -> List[WatchStock]:
        """
        搜索自选股
        
        Args:
            keyword: 搜索关键词（股票名称或代码）
            
        Returns:
            匹配的自选股列表
        """
        keyword = keyword.lower()
        results = []
        
        for stock in self.watchlist.values():
            if (keyword in stock.symbol.lower() or 
                keyword in stock.name.lower() or
                keyword in stock.notes.lower()):
                results.append(stock)
        
        return results
