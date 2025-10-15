import re

def normalize_bj_keys_file(input_file, output_file):
    """
    将BJ_keys_madmom_15s_88.txt中的复杂文件名格式
    转换为简单的数字.mp3格式
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    normalized_lines = []
    
    for line in lines:
        line = line.strip()
        
        # 跳过标题行和空行
        if not line or 'Musical Key Detection Results' in line or '===' in line:
            normalized_lines.append(line)
            continue
            
        # 查找包含音调信息的行
        if ':' in line and ('major' in line or 'minor' in line):
            # 提取开头的数字
            number_match = re.match(r'^(\d+)', line)
            if number_match:
                number = number_match.group(1)
                # 提取音调信息（冒号后的部分）
                key_match = re.search(r': ([A-G][#b]? (?:major|minor))', line)
                if key_match:
                    key = key_match.group(1)
                    # 创建新格式：数字.mp3: 音调
                    new_line = f"{number}.mp3: {key}"
                    normalized_lines.append(new_line)
                    continue
        
        # 如果无法解析，保持原行
        normalized_lines.append(line)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in normalized_lines:
            f.write(line + '\n')
    
    print(f"文件已成功转换：{input_file} -> {output_file}")
    print(f"共处理了 {len([l for l in normalized_lines if '.mp3:' in l])} 个音频文件条目")

if __name__ == "__main__":
    input_file = "BJ_keys_madmom_15s_88.txt"
    output_file = "BJ_keys_madmom_15s_88_normalized.txt"
    
    normalize_bj_keys_file(input_file, output_file)
    
    # 显示转换前后的对比示例
    print("\n转换示例：")
    print("转换前: 049.遇皇后 在头上整整乌纱帽 - 孟广禄 蓝文云_15s.mp3: D# minor")
    print("转换后: 049.mp3: D# minor")