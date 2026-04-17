import os
import pandas as pd
import numpy as np
import glob
import re

def load_stock_trading_data(data_dir):
    """
    从指定目录加载所有股票交易数据
    
    Parameters:
    data_dir (str): 数据目录路径
    
    Returns:
    dict: 股票数据字典，键为股票代码，值为对应的DataFrame
    """
    stock_data_dict = {}
    
    # 查找所有CSV文件
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    for csv_file in csv_files:
        try:
            # 从文件名获取股票代码
            stock_code = os.path.basename(csv_file).replace('.csv', '')
            
            # 尝试不同的编码格式读取CSV文件，跳过第一行无效的头部信息
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            df = None
            for encoding in encodings:
                try:
                    # 跳过第一行无效的头部信息
                    df = pd.read_csv(csv_file, encoding=encoding, skiprows=1)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print(f"无法读取股票数据文件 {csv_file}")
                continue
            
            # 清理列名，去除特殊字符
            cleaned_columns = []
            for col in df.columns:
                # 去除特殊字符和空格，转换为小写
                clean_col = re.sub(r'[^\w\s]', '', col).strip().lower()
                # 处理中文字符
                clean_col = re.sub(r'\s+', '_', clean_col)  # 将空格替换为下划线
                cleaned_columns.append(clean_col)
            df.columns = cleaned_columns
            
            # 标准化列名，确保包含必要的列（支持中英文列名）
            column_mapping = {
                'code': ['code', '股票代码', '股_票_代_码'],
                'name': ['name', '股票名称', '股_票_名_称'],
                'date': ['date', 'time', '时间', '日期', '交易日期', '交_易_日_期'],
                'open': ['open',  '开盘价', '开_盘_价'],
                'high': ['high',  '最高价', '最_高_价'],
                'low': ['low', '最低价', '最_低_价'],
                'close': ['close', '收盘价', '收_盘_价'],
                'volume': ['volume', '成交量', '成_交_量'],
                'amount': ['amount', '成交额', '成_交_额']
            }
            
            # 应用列名映射
            new_columns = {}
            for col in df.columns:
                # 查找最佳匹配
                matched = False
                for standard_name, possible_names in column_mapping.items():
                    for possible_name in possible_names:
                        if possible_name == col:
                            new_columns[col] = standard_name
                            matched = True
                            break
                    if matched:
                        break
                # 如果没有匹配到，保持原列名
                if not matched:
                    new_columns[col] = col
            df.rename(columns=new_columns, inplace=True)
            
            # 确保必要的列都存在
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"警告: 数据中缺少列 {missing_columns}，跳过股票 {stock_code}")
                continue  # 跳过数据有问题的股票
            
            # 转换日期列
            date_columns = [col for col in df.columns if col in ['date', 'time']]
            if date_columns:
                df['date'] = pd.to_datetime(df[date_columns[0]], errors='coerce')
                df = df.sort_values('date').reset_index(drop=True)
            
            # 添加涨停和跌停标识
            required_price_cols = ['open', 'close', 'high', 'low']
            if all(col in df.columns for col in required_price_cols):
                # 确保数据类型正确
                for col in required_price_cols + ['volume']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
                # 计算涨跌幅
                df['prev_close'] = df['close'].shift(1)
                df['change_ratio'] = (df['close'] - df['prev_close']) / df['prev_close']
                
                # 一字涨停：开盘价等于收盘价等于最高价等于最低价，且涨幅接近10%
                df['limit_up'] = ((df['open'] == df['close']) & 
                                 (df['close'] == df['high']) & 
                                 (df['high'] == df['low']) & 
                                 (df['change_ratio'] > 0.09))
                
                # 一字跌停：开盘价等于收盘价等于最高价等于最低价，且跌幅接近10%
                df['limit_down'] = ((df['open'] == df['close']) & 
                                   (df['close'] == df['high']) & 
                                   (df['high'] == df['low']) & 
                                   (df['change_ratio'] < -0.09))
            
            # 检查数据是否有效（非空且有足够数据点）
            if len(df) < 10:  # 至少需要10天的数据
                print(f"警告: 股票 {stock_code} 数据量不足，跳过")
                continue
            
            # 检查价格和成交量是否有效
            price_cols = ['open', 'high', 'low', 'close']
            if df[price_cols].isnull().any().any() or (df['volume'].isnull().any() if 'volume' in df.columns else False):
                print(f"警告: 股票 {stock_code} 存在缺失值，跳过")
                continue
                
            if (df[price_cols] <= 0).any().any() or (('volume' in df.columns and (df['volume'] < 0).any()) if 'volume' in df.columns else False):
                print(f"警告: 股票 {stock_code} 存在无效价格或成交量数据，跳过")
                continue
            
            stock_data_dict[stock_code] = df
            
        except Exception as e:
            print(f"加载股票数据 {csv_file} 时出错: {e}")

    return stock_data_dict

def load_single_stock_data(stock_code=None):
    """
    从CSV文件加载单只股票数据
    
    Parameters:
    stock_code (str): 股票代码，如果为None则随机选择一个
    
    Returns:
    tuple: (股票代码, DataFrame)
    """
    # 获取data目录路径
    data_dir = os.path.join(os.path.dirname(__file__), 'stock-trading-data-2024-09-28N')
    
    # 查找CSV文件
    if not os.path.exists(data_dir):
        print(f"目录 {data_dir} 不存在")
        return None, None
    
    # 获取所有CSV文件
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print("未找到CSV文件")
        return None, None
    
    # 如果没有指定股票代码，则随机选择一个
    if stock_code is None:
        csv_file = np.random.choice(csv_files)
        stock_code = os.path.basename(csv_file).replace('.csv', '')
    else:
        # 查找指定股票代码的文件
        csv_file = os.path.join(data_dir, f"{stock_code}.csv")
        if not os.path.exists(csv_file):
            print(f"未找到股票 {stock_code} 的数据文件")
            return None, None
    
    try:
        # 尝试不同的编码格式读取CSV文件，跳过第一行无效的头部信息
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
        df = None
        for encoding in encodings:
            try:
                # 跳过第一行无效的头部信息
                df = pd.read_csv(csv_file, encoding=encoding, skiprows=1)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"无法读取股票数据文件 {csv_file}")
            return None, None
        
        # 清理列名，去除特殊字符
        cleaned_columns = []
        for col in df.columns:
            # 去除特殊字符和空格，转换为小写
            clean_col = re.sub(r'[^\w\s]', '', col).strip().lower()
            # 处理中文字符
            clean_col = re.sub(r'\s+', '_', clean_col)  # 将空格替换为下划线
            cleaned_columns.append(clean_col)
        df.columns = cleaned_columns
        
        # 标准化列名，确保包含必要的列（支持中英文列名）
        column_mapping = {
            'code': ['code', '股票代码', '股_票_代_码'],
            'name': ['name', '股票名称', '股_票_名_称'],
            'date': ['date', 'time', '时间', '日期', '交易日期', '交_易_日_期'],
            'open': ['open', '开盘', '开盘价', '开_盘_价'],
            'high': ['high', '最高', '最高价', '最_高_价'],
            'low': ['low', '最低', '最低价', '最_低_价'],
            'close': ['close', '收盘', '收盘价', '收_盘_价'],
            'volume': ['volume', '成交量', '成_交_量'],
            'amount': ['amount', '成交额', '成_交_额']
        }
        
        # 应用列名映射
        new_columns = {}
        for col in df.columns:
            # 查找最佳匹配
            matched = False
            for standard_name, possible_names in column_mapping.items():
                for possible_name in possible_names:
                    if possible_name == col:
                        new_columns[col] = standard_name
                        matched = True
                        break
                if matched:
                    break
            # 如果没有匹配到，保持原列名
            if not matched:
                new_columns[col] = col
        df.rename(columns=new_columns, inplace=True)
        
        # 确保必要的列都存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"警告: 数据中缺少列 {missing_columns}，可能影响策略执行")
            # 为缺失的volume列创建默认值
            if 'volume' in missing_columns:
                df['volume'] = np.random.randint(100000, 1000000, len(df))
                missing_columns.remove('volume')
                print("创建默认的交易量列...")
        
        # 转换日期列
        date_columns = [col for col in df.columns if col in ['date', 'time']]
        if date_columns:
            df['date'] = pd.to_datetime(df[date_columns[0]], errors='coerce')
            df = df.sort_values('date').reset_index(drop=True)
        
        # 添加涨停和跌停标识
        required_price_cols = ['open', 'close', 'high', 'low']
        if all(col in df.columns for col in required_price_cols):
            # 确保数据类型正确
            for col in required_price_cols + ['volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 计算涨跌幅
            df['prev_close'] = df['close'].shift(1)
            df['change_ratio'] = (df['close'] - df['prev_close']) / df['prev_close']
            
            # 一字涨停：开盘价等于收盘价等于最高价等于最低价，且涨幅接近10%
            df['limit_up'] = ((df['open'] == df['close']) & 
                             (df['close'] == df['high']) & 
                             (df['high'] == df['low']) & 
                             (df['change_ratio'] > 0.099))
            
            # 一字跌停：开盘价等于收盘价等于最高价等于最低价，且跌幅接近10%
            df['limit_down'] = ((df['open'] == df['close']) & 
                               (df['close'] == df['high']) & 
                               (df['high'] == df['low']) & 
                               (df['change_ratio'] < -0.099))
        
        return stock_code, df
        
    except Exception as e:
        print(f"加载股票数据 {stock_code} 时出错: {e}")
        return None, None

def save_data(data, filename):
    """
    保存数据到文件
    
    Parameters:
    data (DataFrame): 要保存的数据
    filename (str): 文件名
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    data.to_csv(filepath, index=False)

def load_data(filename):
    """
    从文件加载数据
    
    Parameters:
    filename (str): 文件名
    
    Returns:
    DataFrame: 加载的数据
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    # 尝试不同的编码格式，跳过第一行无效的头部信息
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding, skiprows=1)
            # 清理列名，去除特殊字符
            cleaned_columns = []
            for col in df.columns:
                # 去除特殊字符和空格，转换为小写
                clean_col = re.sub(r'[^\w\s]', '', col).strip().lower()
                # 处理中文字符
                clean_col = re.sub(r'\s+', '_', clean_col)  # 将空格替换为下划线
                cleaned_columns.append(clean_col)
            df.columns = cleaned_columns
            return df
        except UnicodeDecodeError:
            continue
    # 如果所有编码都失败，则使用默认编码并忽略错误
    df = pd.read_csv(filepath, encoding='utf-8', errors='ignore', skiprows=1)
    # 清理列名，去除特殊字符
    cleaned_columns = []
    for col in df.columns:
        # 去除特殊字符和空格，转换为小写
        clean_col = re.sub(r'[^\w\s]', '', col).strip().lower()
        # 处理中文字符
        clean_col = re.sub(r'\s+', '_', clean_col)  # 将空格替换为下划线
        cleaned_columns.append(clean_col)
    df.columns = cleaned_columns
    return df

def get_stock_data(stock_code, start_date=None, end_date=None):
    """
    获取指定股票的数据
    
    Parameters:
    stock_code (str): 股票代码
    start_date (str): 开始日期，格式为'YYYY-MM-DD'
    end_date (str): 结束日期，格式为'YYYY-MM-DD'
    
    Returns:
    DataFrame: 股票数据
    """
    stock_code, data = load_single_stock_data(stock_code)
    
    if data is not None and start_date is not None and end_date is not None:
        data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
        
    return stock_code, data

def load_csv_data(filepath):
    """
    从CSV文件加载数据
    
    Parameters:
    filepath (str): CSV文件路径
    
    Returns:
    DataFrame: 加载的数据
    """
    # 尝试不同的编码格式，跳过第一行无效的头部信息
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding, skiprows=1)
            # 清理列名，去除特殊字符
            cleaned_columns = []
            for col in df.columns:
                # 去除特殊字符和空格，转换为小写
                clean_col = re.sub(r'[^\w\s]', '', col).strip().lower()
                # 处理中文字符
                clean_col = re.sub(r'\s+', '_', clean_col)  # 将空格替换为下划线
                cleaned_columns.append(clean_col)
            df.columns = cleaned_columns
            return df
        except UnicodeDecodeError:
            continue
    # 如果所有编码都失败，则使用默认编码并忽略错误
    df = pd.read_csv(filepath, encoding='utf-8', errors='ignore', skiprows=1)
    # 清理列名，去除特殊字符
    cleaned_columns = []
    for col in df.columns:
        # 去除特殊字符和空格，转换为小写
        clean_col = re.sub(r'[^\w\s]', '', col).strip().lower()
        # 处理中文字符
        clean_col = re.sub(r'\s+', '_', clean_col)  # 将空格替换为下划线
        cleaned_columns.append(clean_col)
    df.columns = cleaned_columns
    return df