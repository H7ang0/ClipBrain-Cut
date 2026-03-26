import json
import argparse
import sys

# 本地素材库索引文件的路径
DATABASE_PATH = "ClipBrain_Library.json"

def search_clipbrain(query, limit=5):
    """
    接收 Claude Code 传来的检索词，在本地 JSON 库中进行匹配，
    并返回结构化的 JSON 数据供 Claude Code 进一步处理或回复用户。
    """
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            library = json.load(f)
    except FileNotFoundError:
        # 如果找不到数据库，返回友好的错误信息给 Claude Code
        error_msg = {"error": f"未找到 {DATABASE_PATH}，请确保已运行 clipbrain_indexer.py 完成本地素材建库。"}
        return json.dumps(error_msg, ensure_ascii=False)

    results = []
    # 简单的分词逻辑：如果输入有空格则按空格分词，否则按单字切分
    keywords = query.split() if " " in query else list(query)
    
    for filename, data in library.items():
        if "scenes" not in data: 
            continue
        
        for scene in data["scenes"]:
            score = 0
            # 将所有描述性字段拼接在一起进行匹配
            scene_text = f"{scene.get('shot_type','')} {scene.get('action_desc','')} {scene.get('audio_desc','')} {scene.get('emotion_tag','')}"
            
            for kw in keywords:
                if kw in scene_text:
                    score += 1
                    
            if score > 0:
                results.append({
                    "filename": filename,
                    "start_time": scene.get("start_time"),
                    "end_time": scene.get("end_time"),
                    "description": scene_text,
                    "relevance_score": score
                })

    # 根据相关性得分从高到低排序，并截取前 limit 个结果
    results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:limit]
    
    #  JSON 格式输出 Claude Code 的 MCP 协议需要解析标准输出
    output_data = {
        "query": query, 
        "matched_clips": results
    }
    return json.dumps(output_data, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClipBrain Cut MCP Search Tool")
    parser.add_argument("query", type=str, help="从 Claude Code 传入的检索提示词 (如: 大笑 特写)")
    parser.add_argument("--limit", type=int, default=5, help="返回结果数量上限")
    
    args = parser.parse_args()
    
    # 将结果打印到标准输出 (stdout)，Claude Code 会捕获这个输出
    print(search_clipbrain(args.query, args.limit))
    sys.exit(0)
