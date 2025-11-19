#!/usr/bin/env python3
"""
音乐生成提示生成模块
根据音乐属性生成提示
"""

import json
import argparse
from pathlib import Path

class PromptGenerator:
    """音乐生成提示生成器"""
    
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self):
        """加载提示模板"""
        return {
            'style_based': "Generate a {style} music piece in {key} {mode}",
            'emotion_based': "Create a {emotion} melody with {valence:.1f} valence and {arousal:.1f} arousal",
            'tempo_based': "Compose music at {bpm} BPM in {time_signature} time signature",
            'comprehensive': "Generate a {style} {emotion} music piece in {key} {mode} at {bpm} BPM"
        }
    
    def generate_style_prompt(self, properties):
        """生成基于风格的提示"""
        template = self.templates['style_based']
        return template.format(
            style=properties.get('style', 'classical'),
            key=properties.get('key', 'C'),
            mode=properties.get('mode', 'major')
        )
    
    def generate_emotion_prompt(self, properties):
        """生成基于情感的提示"""
        template = self.templates['emotion_based']
        return template.format(
            emotion=properties.get('emotion', 'happy'),
            valence=properties.get('valence', 0.5),
            arousal=properties.get('arousal', 0.5)
        )
    
    def generate_tempo_prompt(self, properties):
        """生成基于节拍的提示"""
        template = self.templates['tempo_based']
        return template.format(
            bpm=properties.get('bpm', 120),
            time_signature=properties.get('time_signature', '4/4')
        )
    
    def generate_comprehensive_prompt(self, properties):
        """生成综合提示"""
        template = self.templates['comprehensive']
        return template.format(
            style=properties.get('style', 'classical'),
            emotion=properties.get('emotion', 'happy'),
            key=properties.get('key', 'C'),
            mode=properties.get('mode', 'major'),
            bpm=properties.get('bpm', 120)
        )
    
    def generate_all_prompts(self, properties):
        """生成所有类型的提示"""
        prompts = {
            'style_based': self.generate_style_prompt(properties),
            'emotion_based': self.generate_emotion_prompt(properties),
            'tempo_based': self.generate_tempo_prompt(properties),
            'comprehensive': self.generate_comprehensive_prompt(properties)
        }
        return prompts

def main():
    parser = argparse.ArgumentParser(description="音乐生成提示生成")
    parser.add_argument("--properties", required=True, help="输入属性文件路径")
    parser.add_argument("--output", required=True, help="输出提示文件路径")
    parser.add_argument("--type", default="comprehensive", 
                       choices=['style_based', 'emotion_based', 'tempo_based', 'comprehensive', 'all'],
                       help="提示类型")
    
    args = parser.parse_args()
    
    # 加载属性
    with open(args.properties, 'r') as f:
        properties = json.load(f)
    
    # 生成提示
    generator = PromptGenerator()
    
    if args.type == 'all':
        prompts = generator.generate_all_prompts(properties)
    else:
        method = getattr(generator, f'generate_{args.type}_prompt')
        prompts = {args.type: method(properties)}
    
    # 保存结果
    with open(args.output, 'w') as f:
        json.dump(prompts, f, indent=2)
    
    print(f"提示已保存到: {args.output}")
    for prompt_type, prompt_text in prompts.items():
        print(f"{prompt_type}: {prompt_text}")

if __name__ == "__main__":
    main()
