import os
import json
import uuid
import time
import argparse

# 剪映 Mac 版的默认草稿路径 (Windows 用户需修改为对应的 AppData 路径)
# 例如 Mac: /Users/你的用户名/Movies/CapCut/User Data/Projects/com.lveditor.draft/
# 请根据你的实际情况修改此处
CAPCUT_DRAFT_DIR = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft/")

def generate_uuid():
    return str(uuid.uuid4())

def parse_time_to_microseconds(time_str):
    """将 00:05 格式的时间转换为剪映所需的微秒"""
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return (minutes * 60 + seconds) * 1000000
    except Exception:
        return 0

def create_capcut_draft(project_name, clips):
    """
    根据传入的片段列表，生成剪映草稿文件。
    clips 格式示例: [{"filename": "vlog_01.mp4", "start_time": "00:00", "end_time": "00:05"}]
    """
    project_path = os.path.join(CAPCUT_DRAFT_DIR, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    # 剪映草稿骨架
    draft_content = {
        "materials": {
            "videos": [],
            "audios": [],
            "transitions": []
        },
        "tracks": [
            {
                "id": generate_uuid(),
                "type": "video",
                "segments": []
            }
        ],
        "version": 360000 # 适配较新版本的剪映
    }

    current_timeline_position = 0 # 当前轨道的时间轴位置 (微秒)
    
    # 获取原始素材的绝对路径
    material_base_dir = os.path.abspath("./raw_materials")

    for clip in clips:
        material_id = generate_uuid()
        segment_id = generate_uuid()
        
        file_path = os.path.join(material_base_dir, clip['filename'])
        start_us = parse_time_to_microseconds(clip['start_time'])
        end_us = parse_time_to_microseconds(clip['end_time'])
        duration_us = end_us - start_us
        
        if duration_us <= 0:
            duration_us = 3000000 # 默认给 3 秒

        # 1. 注册素材 (Material)
        draft_content["materials"]["videos"].append({
            "id": material_id,
            "path": file_path,
            "type": "video",
            "duration": duration_us # 这里简化为截取长度
        })

        # 2. 将素材放入轨道 (Segment)
        draft_content["tracks"][0]["segments"].append({
            "id": segment_id,
            "material_id": material_id,
            "source_timerange": {
                "start": start_us,
                "duration": duration_us
            },
            "target_timerange": {
                "start": current_timeline_position,
                "duration": duration_us
            }
        })
        
        # 推进时间轴
        current_timeline_position += duration_us

    # 写入 draft_content.json
    content_file = os.path.join(project_path, "draft_content.json")
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(draft_content, f, ensure_ascii=False)

    # 写入 draft_meta_info.json (剪映识别工程所必须的元数据)
    meta_info = {
        "id": generate_uuid(),
        "draft_name": project_name,
        "draft_root_path": project_path,
        "tm_draft_create": int(time.time() * 1000),
        "tm_draft_modified": int(time.time() * 1000)
    }
    meta_file = os.path.join(project_path, "draft_meta_info.json")
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(meta_info, f, ensure_ascii=False)

    return project_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClipBrain Cut 剪映草稿生成器")
    parser.add_argument("project_name", type=str, help="剪映工程名称")
    parser.add_argument("clips_json", type=str, help="包含片段信息的 JSON 字符串")
    
    args = parser.parse_args()
    
    try:
        clips_data = json.loads(args.clips_json)
        # 兼容两种可能的 JSON 结构
        if "matched_clips" in clips_data:
            clips = clips_data["matched_clips"]
        else:
            clips = clips_data
            
        draft_path = create_capcut_draft(args.project_name, clips)
        print(json.dumps({"status": "success", "message": f"成功生成剪映工程: {args.project_name}", "path": draft_path}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
