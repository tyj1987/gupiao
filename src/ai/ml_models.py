import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from loguru import logger
import joblib
import os
# 机器学习模块
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
# import lightgbm as lgb  # 暂时注释，可选安装
# import xgboost as xgb  # 暂时注释，可选安装
from sklearn.neural_network import MLPRegressor

from config.config import config

class MLModels:
    """机器学习模型管理器"""
    
    def __init__(self):
        """
        初始化机器学习模型
        """
        logger.info("机器学习模型管理器初始化中...")
        self.models = {}
        self.scalers = {}
        self.disabled = False  # 启用机器学习功能
        
        # 模型配置
        self.model_configs = {
            'random_forest': {
                'model': RandomForestRegressor,
                'params': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': 42
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingRegressor,
                'params': {
                    'n_estimators': 100,
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'random_state': 42
                }
            },
            # 'lightgbm': {
            #     'model': lgb.LGBMRegressor,
            #     'params': {
            #         'n_estimators': 100,
            #         'learning_rate': 0.1,
            #         'max_depth': 6,
            #         'random_state': 42,
            #         'verbose': -1
            #     }
            # },
            # 'xgboost': {
            #     'model': xgb.XGBRegressor,
            #     'params': {
            #         'n_estimators': 100,
            #         'learning_rate': 0.1,
            #         'max_depth': 6,
            #         'random_state': 42
            #     }
            # },
            'neural_network': {
                'model': MLPRegressor,
                'params': {
                    'hidden_layer_sizes': (100, 50),
                    'activation': 'relu',
                    'solver': 'adam',
                    'alpha': 0.001,
                    'learning_rate': 'constant',
                    'max_iter': 500,
                    'random_state': 42
                }
            },
            'linear_regression': {
                'model': LinearRegression,
                'params': {}
            },
            'ridge': {
                'model': Ridge,
                'params': {
                    'alpha': 1.0,
                    'random_state': 42
                }
            },
            'svr': {
                'model': SVR,
                'params': {
                    'kernel': 'rbf',
                    'C': 1.0,
                    'gamma': 'scale'
                }
            }
        }
        
        # 模型保存路径
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # 加载已训练的模型
        self._load_models()
        
        logger.info("机器学习模型管理器初始化完成")
    
    def train_models(self, 
                    features: Union[pd.DataFrame, np.ndarray], 
                    targets: Union[pd.Series, np.ndarray],
                    model_names: List[str] = None,
                    test_size: float = 0.2,
                    cv_folds: int = 5) -> Dict[str, Dict]:
        """
        训练机器学习模型
        
        Args:
            features: 特征数据，支持DataFrame或numpy数组
            targets: 目标变量，支持Series或numpy数组
            model_names: 要训练的模型名称列表
            test_size: 测试集比例
            cv_folds: 交叉验证折数
            
        Returns:
            训练结果
        """
        try:
            if hasattr(self, 'disabled') and self.disabled:
                logger.warning("机器学习模块被禁用")
                return {}
            
            # 转换为DataFrame/Series格式
            if isinstance(features, np.ndarray):
                feature_names = [f'feature_{i}' for i in range(features.shape[1])]
                features = pd.DataFrame(features, columns=feature_names)
            
            if isinstance(targets, np.ndarray):
                targets = pd.Series(targets)
                
            if features.empty or targets.empty:
                logger.warning("训练数据为空")
                return {}
            
            if model_names is None:
                model_names = list(self.model_configs.keys())
                
            logger.debug(f"将训练模型: {model_names}")
            
            # 数据预处理
            features_clean = self._preprocess_features(features)
            targets_clean = targets.dropna()
            
            # 确保特征和目标对齐
            common_index = features_clean.index.intersection(targets_clean.index)
            features_clean = features_clean.loc[common_index]
            targets_clean = targets_clean.loc[common_index]
            
            if len(features_clean) < 50:
                logger.warning("训练数据不足50条，跳过模型训练")
                return {}
            
            # 分割训练测试集
            X_train, X_test, y_train, y_test = train_test_split(
                features_clean, targets_clean, 
                test_size=test_size, 
                random_state=42,
                shuffle=False  # 时间序列数据不打乱
            )
            
            results = {}
            
            for model_name in model_names:
                try:
                    logger.info(f"开始训练{model_name}模型")
                    
                    # 获取模型配置
                    model_config = self.model_configs[model_name]
                    model_class = model_config['model']
                    params = model_config['params'].copy()
                    
                    # 数据标准化
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)
                    
                    # 创建并训练模型
                    model = model_class(**params)
                    model.fit(X_train_scaled, y_train)
                    
                    # 预测
                    y_train_pred = model.predict(X_train_scaled)
                    y_test_pred = model.predict(X_test_scaled)
                    
                    # 评估模型
                    train_metrics = self._calculate_metrics(y_train, y_train_pred)
                    test_metrics = self._calculate_metrics(y_test, y_test_pred)
                    
                    # 交叉验证
                    cv_scores = cross_val_score(
                        model, X_train_scaled, y_train, 
                        cv=cv_folds, scoring='neg_mean_squared_error'
                    )
                    
                    # 保存模型和标准化器
                    self.models[model_name] = model
                    self.scalers[model_name] = scaler
                    self._save_model(model_name, model, scaler)
                    
                    results[model_name] = {
                        'train_metrics': train_metrics,
                        'test_metrics': test_metrics,
                        'cv_score_mean': -cv_scores.mean(),
                        'cv_score_std': cv_scores.std(),
                        'feature_importance': self._get_feature_importance(model, features_clean.columns),
                        'model_params': params
                    }
                    
                    logger.info(f"{model_name}模型训练完成，测试R²: {test_metrics['r2']:.4f}")
                    
                except Exception as e:
                    logger.error(f"训练{model_name}模型失败: {e}")
                    results[model_name] = {'error': str(e)}
            
            return results
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            return {}
    
    def predict(self, features: pd.DataFrame, model_name: str = None) -> Dict[str, Any]:
        """
        使用模型进行预测
        
        Args:
            features: 特征数据
            model_name: 模型名称，如果为None则使用集成预测
            
        Returns:
            预测结果
        """
        try:
            if features.empty:
                return {'prediction': 0, 'confidence': 0, 'model': 'none'}
            
            # 数据预处理
            features_clean = self._preprocess_features(features)
            
            if features_clean.empty:
                return {'prediction': 0, 'confidence': 0, 'model': 'none'}
            
            # 使用指定模型预测
            if model_name and model_name in self.models:
                return self._single_model_predict(features_clean, model_name)
            
            # 集成预测
            return self._ensemble_predict(features_clean)
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return {'prediction': 0, 'confidence': 0, 'model': 'error'}
    
    def _single_model_predict(self, features: pd.DataFrame, model_name: str) -> Dict[str, Any]:
        """
        单模型预测
        
        Args:
            features: 特征数据
            model_name: 模型名称
            
        Returns:
            预测结果
        """
        try:
            # 检查模型是否存在且已训练
            if model_name not in self.models or self.models[model_name] is None:
                logger.warning(f"模型{model_name}未训练，返回默认预测")
                return {'prediction': 0, 'confidence': 50, 'model': model_name}
            
            model = self.models[model_name]
            scaler = self.scalers[model_name]
            
            # 检查特征名称是否匹配
            if hasattr(model, 'feature_names_in_'):
                expected_features = model.feature_names_in_
                current_features = features.columns.tolist()
                
                if not np.array_equal(expected_features, current_features):
                    logger.warning(f"模型{model_name}特征不匹配，需要重新训练")
                    return {'prediction': 0, 'confidence': 30, 'model': model_name}
            
            # 标准化特征
            features_scaled = scaler.transform(features)
            
            # 预测
            prediction = model.predict(features_scaled)
            
            # 计算置信度（基于模型的预测方差或其他指标）
            confidence = self._calculate_confidence(model, features_scaled, prediction)
            
            return {
                'prediction': float(prediction[0]) if len(prediction) == 1 else prediction.tolist(),
                'confidence': confidence,
                'model': model_name
            }
            
        except Exception as e:
            logger.error(f"单模型预测失败: {e}")
            return {'prediction': 0, 'confidence': 0, 'model': model_name}
    
    def _ensemble_predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        集成预测
        
        Args:
            features: 特征数据
            
        Returns:
            集成预测结果
        """
        try:
            if not self.models:
                return {'prediction': 0, 'confidence': 0, 'model': 'no_models'}
            
            predictions = []
            confidences = []
            model_names = []
            
            for model_name in self.models:
                try:
                    result = self._single_model_predict(features, model_name)
                    predictions.append(result['prediction'])
                    confidences.append(result['confidence'])
                    model_names.append(model_name)
                except Exception as e:
                    logger.warning(f"模型{model_name}预测失败: {e}")
            
            if not predictions:
                return {'prediction': 0, 'confidence': 0, 'model': 'all_failed'}
            
            # 加权平均预测（基于置信度）
            weights = np.array(confidences)
            if weights.sum() > 0:
                weights = weights / weights.sum()
                ensemble_prediction = np.average(predictions, weights=weights)
            else:
                ensemble_prediction = np.mean(predictions)
            
            # 集成置信度
            ensemble_confidence = np.mean(confidences)
            
            return {
                'prediction': float(ensemble_prediction),
                'confidence': ensemble_confidence,
                'model': 'ensemble',
                'individual_predictions': {
                    name: pred for name, pred in zip(model_names, predictions)
                },
                'individual_confidences': {
                    name: conf for name, conf in zip(model_names, confidences)
                }
            }
            
        except Exception as e:
            logger.error(f"集成预测失败: {e}")
            return {'prediction': 0, 'confidence': 0, 'model': 'ensemble_error'}
    
    def _preprocess_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        预处理特征数据
        
        Args:
            features: 原始特征数据
            
        Returns:
            预处理后的特征数据
        """
        try:
            # 复制数据
            features_clean = features.copy()
            
            # 处理无穷大值
            features_clean = features_clean.replace([np.inf, -np.inf], np.nan)
            
            # 处理缺失值
            features_clean = features_clean.fillna(features_clean.mean())
            
            # 移除常数列
            constant_cols = features_clean.columns[features_clean.nunique() <= 1]
            if len(constant_cols) > 0:
                features_clean = features_clean.drop(columns=constant_cols)
                logger.debug(f"移除常数列: {list(constant_cols)}")
            
            # 移除高相关性列
            if len(features_clean.columns) > 1:
                corr_matrix = features_clean.corr().abs()
                upper_tri = corr_matrix.where(
                    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                )
                high_corr_cols = [column for column in upper_tri.columns if any(upper_tri[column] > 0.95)]
                if high_corr_cols:
                    features_clean = features_clean.drop(columns=high_corr_cols)
                    logger.debug(f"移除高相关性列: {high_corr_cols}")
            
            return features_clean
            
        except Exception as e:
            logger.error(f"特征预处理失败: {e}")
            return pd.DataFrame()
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        计算模型评估指标
        
        Args:
            y_true: 真实值
            y_pred: 预测值
            
        Returns:
            评估指标
        """
        try:
            return {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred),
                'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100 if np.all(y_true != 0) else np.inf
            }
        except Exception as e:
            logger.error(f"计算评估指标失败: {e}")
            return {'mse': np.inf, 'rmse': np.inf, 'mae': np.inf, 'r2': -np.inf, 'mape': np.inf}
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """
        获取特征重要性
        
        Args:
            model: 训练好的模型
            feature_names: 特征名称列表
            
        Returns:
            特征重要性字典
        """
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importances = np.abs(model.coef_)
            else:
                return {}
            
            # 确保长度匹配
            if len(importances) != len(feature_names):
                return {}
            
            # 归一化重要性
            if importances.sum() > 0:
                importances = importances / importances.sum()
            
            return dict(zip(feature_names, importances))
            
        except Exception as e:
            logger.error(f"获取特征重要性失败: {e}")
            return {}
    
    def _calculate_confidence(self, model, features: np.ndarray, prediction: np.ndarray) -> float:
        """
        计算预测置信度
        
        Args:
            model: 模型
            features: 特征数据
            prediction: 预测结果
            
        Returns:
            置信度
        """
        try:
            # 基于模型类型计算置信度
            if hasattr(model, 'predict_proba'):
                # 分类模型
                proba = model.predict_proba(features)
                return float(np.max(proba))
            elif hasattr(model, 'estimators_'):
                # 集成模型
                predictions = np.array([est.predict(features) for est in model.estimators_])
                std = np.std(predictions, axis=0)
                # 标准差越小，置信度越高
                confidence = 1 / (1 + std[0]) if len(std) > 0 else 0.5
                return float(confidence)
            else:
                # 其他模型，返回固定置信度
                return 0.7
                
        except Exception as e:
            logger.warning(f"计算置信度失败: {e}")
            return 0.5
    
    def _save_model(self, model_name: str, model, scaler):
        """
        保存模型和标准化器
        
        Args:
            model_name: 模型名称
            model: 模型对象
            scaler: 标准化器
        """
        try:
            model_path = os.path.join(self.model_dir, f'{model_name}_model.pkl')
            scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.pkl')
            
            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)
            
            logger.debug(f"模型{model_name}保存成功")
            
        except Exception as e:
            logger.error(f"保存模型{model_name}失败: {e}")
    
    def _load_models(self):
        """
        加载已保存的模型
        """
        try:
            if not os.path.exists(self.model_dir):
                return
            
            for model_name in self.model_configs.keys():
                model_path = os.path.join(self.model_dir, f'{model_name}_model.pkl')
                scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.pkl')
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    try:
                        model = joblib.load(model_path)
                        scaler = joblib.load(scaler_path)
                        
                        self.models[model_name] = model
                        self.scalers[model_name] = scaler
                        
                        logger.debug(f"模型{model_name}加载成功")
                        
                    except Exception as e:
                        logger.warning(f"加载模型{model_name}失败: {e}")
            
            if self.models:
                logger.info(f"成功加载{len(self.models)}个模型")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
    
    def optimize_hyperparameters(self, 
                                features: pd.DataFrame, 
                                targets: pd.Series,
                                model_name: str,
                                param_grid: Dict = None) -> Dict[str, Any]:
        """
        超参数优化
        
        Args:
            features: 特征数据
            targets: 目标变量
            model_name: 模型名称
            param_grid: 参数网格
            
        Returns:
            优化结果
        """
        try:
            if model_name not in self.model_configs:
                logger.error(f"未知模型: {model_name}")
                return {}
            
            # 数据预处理
            features_clean = self._preprocess_features(features)
            targets_clean = targets.dropna()
            
            # 确保特征和目标对齐
            common_index = features_clean.index.intersection(targets_clean.index)
            features_clean = features_clean.loc[common_index]
            targets_clean = targets_clean.loc[common_index]
            
            if len(features_clean) < 50:
                logger.warning("数据不足，跳过超参数优化")
                return {}
            
            # 数据标准化
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features_clean)
            
            # 获取模型和默认参数网格
            model_config = self.model_configs[model_name]
            model_class = model_config['model']
            
            if param_grid is None:
                param_grid = self._get_default_param_grid(model_name)
            
            # 网格搜索
            grid_search = GridSearchCV(
                model_class(),
                param_grid,
                cv=5,
                scoring='neg_mean_squared_error',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(features_scaled, targets_clean)
            
            # 更新模型配置
            self.model_configs[model_name]['params'] = grid_search.best_params_
            
            # 训练最优模型
            best_model = grid_search.best_estimator_
            self.models[model_name] = best_model
            self.scalers[model_name] = scaler
            
            # 保存优化后的模型
            self._save_model(model_name, best_model, scaler)
            
            return {
                'best_params': grid_search.best_params_,
                'best_score': -grid_search.best_score_,
                'cv_results': grid_search.cv_results_
            }
            
        except Exception as e:
            logger.error(f"超参数优化失败: {e}")
            return {}
    
    def _get_default_param_grid(self, model_name: str) -> Dict:
        """
        获取默认参数网格
        
        Args:
            model_name: 模型名称
            
        Returns:
            参数网格
        """
        param_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.05, 0.1, 0.2],
                'max_depth': [3, 6, 9]
            },
            'lightgbm': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.05, 0.1, 0.2],
                'max_depth': [3, 6, 9]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.05, 0.1, 0.2],
                'max_depth': [3, 6, 9]
            },
            'neural_network': {
                'hidden_layer_sizes': [(50,), (100,), (100, 50)],
                'alpha': [0.0001, 0.001, 0.01],
                'learning_rate_init': [0.001, 0.01, 0.1]
            },
            'ridge': {
                'alpha': [0.1, 1.0, 10.0, 100.0]
            },
            'svr': {
                'C': [0.1, 1.0, 10.0],
                'gamma': ['scale', 'auto', 0.001, 0.01]
            }
        }
        
        return param_grids.get(model_name, {})
    
    def get_model_performance(self) -> Dict[str, Dict]:
        """
        获取所有模型的性能信息
        
        Returns:
            模型性能字典
        """
        try:
            performance = {}
            
            for model_name in self.models:
                model = self.models[model_name]
                performance[model_name] = {
                    'model_type': type(model).__name__,
                    'parameters': getattr(model, 'get_params', lambda: {})(),
                    'feature_count': getattr(model, 'n_features_in_', 'unknown'),
                    'is_fitted': hasattr(model, 'feature_importances_') or hasattr(model, 'coef_')
                }
            
            return performance
            
        except Exception as e:
            logger.error(f"获取模型性能失败: {e}")
            return {}
    
    def clear_models(self):
        """
        清除所有模型
        """
        self.models.clear()
        self.scalers.clear()
        logger.info("所有模型已清除")