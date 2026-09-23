#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比生成文档与模板的版式差异"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def compare_pages():
    """对比前三页"""
    pages = [
        ('/tmp/verify/ref-01.png', '/tmp/verify/my-1.png', '第1页（封面）'),
        ('/tmp/verify/ref-02.png', '/tmp/verify/my-2.png', '第2页（摘要）'),
        ('/tmp/verify/ref-03.png', '/tmp/verify/my-3.png', '第3页（目录）'),
    ]

    for ref_path, my_path, label in pages:
        print(f'\n=== {label} ===')

        try:
            ref_img = Image.open(ref_path)
            my_img = Image.open(my_path)

            # 检查尺寸
            if ref_img.size != my_img.size:
                print(f'⚠️  尺寸不同：模板 {ref_img.size} vs 生成 {my_img.size}')
                # 统一尺寸用于比较
                min_w = min(ref_img.width, my_img.width)
                min_h = min(ref_img.height, my_img.height)
                ref_img = ref_img.crop((0, 0, min_w, min_h))
                my_img = my_img.crop((0, 0, min_w, min_h))
            else:
                print(f'✅ 尺寸一致：{ref_img.size}')

            # 转为灰度数组
            ref_arr = np.array(ref_img.convert('L'))
            my_arr = np.array(my_img.convert('L'))

            # 计算差异
            diff = np.abs(ref_arr.astype(int) - my_arr.astype(int))
            diff_ratio = (diff > 10).sum() / diff.size

            print(f'像素差异率：{diff_ratio*100:.2f}%')

            if diff_ratio < 0.05:
                print('✅ 版式基本一致（差异 <5%）')
            elif diff_ratio < 0.15:
                print('⚠️  有一定差异（5%~15%），可能是字体渲染')
            else:
                print('❌ 差异较大（>15%），需要检查排版')

                # 生成差异热图
                diff_img = Image.fromarray((diff > 10).astype(np.uint8) * 255)
                diff_path = my_path.replace('.png', '_diff.png')
                diff_img.save(diff_path)
                print(f'   差异热图已保存：{diff_path}')

        except Exception as e:
            print(f'❌ 对比失败：{e}')

if __name__ == '__main__':
    compare_pages()
