import re

def extract_filename_number(line):
    """
    从文件行中提取文件名的数字部分
    例如：'028.wav: D major' -> '028'
         '028.mp3: D major' -> '028'
    """
    # 匹配数字开头的文件名
    match = re.match(r'^(\d+)\.(wav|mp3):', line)
    if match:
        return match.group(1)
    
    # 匹配特殊文件名（包含中文或英文的完整文件名）
    if ':' in line and not line.startswith('===') and 'Musical Key Detection Results' not in line:
        filename = line.split(':')[0].strip()
        return filename
    
    return None

def match_bj_keys_files(reference_file, target_file, output_file):
    """
    根据参考文件匹配目标文件，删除目标文件中多余的条目
    
    Args:
        reference_file: 参考文件 (BJ_keys_2nd_madmon.txt)
        target_file: 目标文件 (BJ_keys_madmom_15s_88_normalized.txt)
        output_file: 输出文件
    """
    
    # 读取参考文件，提取所有文件名
    reference_filenames = set()
    with open(reference_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            filename = extract_filename_number(line)
            if filename:
                reference_filenames.add(filename)
    
    print(f"参考文件中找到 {len(reference_filenames)} 个文件名")
    print(f"参考文件名示例: {list(reference_filenames)[:10]}")
    
    # 读取目标文件并过滤
    matched_lines = []
    removed_count = 0
    
    with open(target_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # 保留标题行和空行
            if not line or 'Musical Key Detection Results' in line or '===' in line:
                matched_lines.append(line)
                continue
            
            filename = extract_filename_number(line)
            if filename:
                if filename in reference_filenames:
                    # 文件名在参考文件中存在，保留
                    matched_lines.append(line)
                else:
                    # 文件名不在参考文件中，删除
                    removed_count += 1
                    print(f"删除: {line}")
            else:
                # 无法解析的行，保留
                matched_lines.append(line)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in matched_lines:
            f.write(line + '\n')
    
    print(f"\n匹配完成！")
    print(f"删除了 {removed_count} 个多余的条目")
    print(f"保留了 {len([l for l in matched_lines if '.mp3:' in l])} 个匹配的条目")
    print(f"结果已保存到: {output_file}")

if __name__ == "__main__":
    reference_file = "BJ_keys_2nd_madmon.txt"
    target_file = "BJ_keys_madmom_15s_88_normalized.txt"
    output_file = "BJ_keys_madmom_15s_88_matched.txt"
    
    match_bj_keys_files(reference_file, target_file, output_file)