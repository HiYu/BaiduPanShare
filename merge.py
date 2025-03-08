import os
import csv

# 定义目录路径和目标文件路径
input_dir = './'  # 替换为你的输入目录路径
output_file = './book_list.csv'  # 替换为你的目标文件路径
def merge_csv(input_dir, output_file):
    # 打开目标文件以写入符合条件的数据
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["书名","格式","大小","分享链接","提取码","过期时间"])  # 写入标题行
        # 遍历目录下的所有文件
        for filename in os.listdir(input_dir):
            print(filename)
            if filename.endswith('.csv'):  # 只处理 CSV 文件
                file_path = os.path.join(input_dir, filename)
                if file_path == output_file:  # 跳过目标文件
                    continue
                # 打开当前 CSV 文件
                with open(file_path, 'r', newline='', encoding='utf-8') as infile:
                    for line in infile:
                        line = line.strip() # 使用 strip() 去除行尾的换行符
                        items = line.split(',') # 使用 split() 将行拆分为列表
                        new_items = []
                        if len(items) > 6:  # 跳过空行
                            joined = '&'.join(items[0:-5]) # 使用 join() 将列表连接为字符串
                            new_items.append(joined)
                            new_items.extend(items[-5:])
                        else:
                            new_items = items
                        t = new_items[0].split(".")[-1]
                        new_items[1] = t
                        writer.writerow(new_items)  # 写入目标文件
    print(f"处理完成，结果已写入 {output_file}")