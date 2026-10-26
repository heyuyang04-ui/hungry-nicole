#!/usr/bin/env python3
"""Build small animated README WebPs from the verified, released Seedance animations.

Generated media belongs in Release assets, not Git. This never modifies the
runtime animations. Each preview retains the original frame durations and
full clip, including the final frame; only its display size and encoding change.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = '#f5f2f7'
DESCRIPTIONS = {
    'idle': '安静站立、轻轻呼吸，日常陪伴时的默认待机。',
    'idle2': '转头看向主人，作为另一段待机表情。',
    '01': '抬手招呼，向主人问好。',
    '04': '想到好主意时，举起手指表达灵感。',
    '05': '双手叉腰，露出得意的小表情。',
    '08': '靠近主人，温柔地撒个娇。',
    '09': '害羞地转头，又偷偷看回来。',
    '13': '鼓起脸颊，表达一点点小脾气。',
    '14': '打个哈欠，困了也继续陪着你。',
    '18': '开心庆祝，也用于 Codex 任务完成反馈。',
    '22': '展示小小猫爪印记，送给主人。',
    '25': '轻轻吹出星光，来一点小魔法。',
    '20': '在胸前比心，表达喜欢。',
    '21': '拿出约定卡片，和主人作个约定。',
    '24': '打开小盒子，展示珍藏的小宝藏。',
    '26': '温柔点头，表示自己一直陪在身边。',
    'work01': '收到新任务，点头示意准备开始。',
    'work02': '抱着小电脑忙碌，对应执行任务。',
    'work03': '整理纸张和文件夹，对应整理、编辑或回复。',
    'work04': '打开书本翻阅，对应思考、搜索和阅读。',
    'work05': '拿起放大镜检查，对应验证、测试和排查。',
    'drag': '被拖起时悬空摆动，努力保持平衡。',
    'landing': '松开拖拽后轻轻落地，重新站稳。',
    'quota': '拿出小卡片查看，用于额度回应。',
    '17': '实际喂食专用：右键 → 食物 → 面包，成功扣除库存后播放，饱腹度 +30。',
    'hungry': '揉揉肚子、期待投喂；吃饭提醒期间与分身一起循环播放，直到主人确认。',
    'feed': '备用吃面包反馈素材，仅展示；当前喂食功能固定使用「17 · 偷吃面包」。',
}
GROUPS = [
    ('日常陪伴', ['idle', 'idle2', '01', '04', '05', '08', '09', '13', '14']),
    ('互动与小魔法', ['18', '22', '25', '20', '21', '24', '26']),
    ('陪你工作', ['work01', 'work02', 'work03', 'work04', 'work05']),
    ('桌面操作', ['drag', 'landing', 'quota']),
    ('饥饿与喂食', ['17', 'hungry', 'feed']),
]


def collect(value):
    result = {}
    if isinstance(value, dict):
        if 'id' in value and 'file' in value:
            result[value['id']] = value
        for child in value.values():
            result.update(collect(child))
    elif isinstance(value, list):
        for child in value:
            result.update(collect(child))
    return result


def build(source, output, size, release_url):
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((source / '素材清单.json').read_text())
    checksums = json.loads((ROOT / 'app/nicole_assets.json').read_text())['files']
    items = collect(manifest)
    assert set(items) == set(DESCRIPTIONS), 'Action list changed; update gallery descriptions first.'
    rows, samples = [], {}
    for key in DESCRIPTIONS:
        item = items[key]
        path = source / item.get('playbackFile', item['file'])
        expected = checksums['妮可桌宠素材/' + path.relative_to(source).as_posix()]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'Unverified source: {key}'
        frames, durations, elapsed = [], [], 0
        with Image.open(path) as animation:
            for index in range(animation.n_frames):
                animation.seek(index)
                frame = animation.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
                matte = Image.new('RGBA', frame.size, BACKGROUND)
                matte.alpha_composite(frame)
                frames.append(matte.convert('RGB'))
                elapsed += animation.info['duration']
                durations.append(animation.info['duration'])
        target = output / f'preview-nicole-{key}.webp'
        frames[0].save(target, save_all=True, append_images=frames[1:], duration=durations,
                       loop=0, quality=82, method=4, minimize_size=True)
        with Image.open(target) as check:
            total = 0
            for i in range(check.n_frames):
                check.seek(i);check.load();total += check.info['duration']
            assert check.is_animated and check.size == (size, size)
            assert total == elapsed, (key, total, elapsed)
        samples[key] = [frames[round(f * (len(frames) - 1))] for f in (.25, .5, .75)]
        row = dict(id=key, name=item['name'], file=target.name, frames=len(frames),
                   durationMs=elapsed, previewDurationMs=total, bytes=target.stat().st_size,
                   sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    markdown = ['## 动态动作图鉴', '',
        '以下展示当前 Seedance 素材包的全部 **27 段动画**。预览按原速播放，缩小为 200×200 的无声动态 WebP，并铺浅色背景；桌宠实际使用 720×720 透明 WebP。', '',
        '普通互动可从右键 → 手动动作菜单体验；工作动作随 Codex 状态联动。自动动作静音，主动互动在开启声音且 1 倍速时可播放素材音轨。预览为方便查看会重复播放，不代表桌宠会不断重复该动作。', '']
    for group_index, (title, keys) in enumerate(GROUPS):
        markdown += [f'### {title}', '', '| | | |', '| :---: | :---: | :---: |']
        for start in range(0, len(keys), 3):
            cards = []
            for key in keys[start:start + 3]:
                name = items[key]['name']
                cards.append(f'**{name}** · `{key}`<br><img src="{release_url}/preview-nicole-{key}.webp" width="200" height="200" alt="妮可：{name}动态预览"><br>{DESCRIPTIONS[key]}')
            markdown.append('| ' + ' | '.join(cards + [''] * (3 - len(cards))) + ' |')
        markdown.append('')
        sheet = Image.new('RGB', (size * 3, (size + 22) * len(keys)), BACKGROUND)
        draw = ImageDraw.Draw(sheet)
        for row, key in enumerate(keys):
            draw.text((8, row * (size + 22) + 4), key, fill='#393343')
            for col, frame in enumerate(samples[key]):
                sheet.paste(frame, (col * size, row * (size + 22) + 22))
        sheet.save(output / f'contact-{group_index + 1}.jpg')
    (output / 'gallery.md').write_text('\n'.join(markdown), encoding='utf-8')
    (output / 'gallery-report.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'outputs/妮可桌宠素材')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/readme-gallery')
    parser.add_argument('--release-url', default='https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance')
    args = parser.parse_args()
    build(args.source, args.output, 200, args.release_url.rstrip('/'))
