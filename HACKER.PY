import csv
from dataclasses import dataclass
from typing import List
import json

@dataclass
class CursorVersion:
    version: str
    build_id: str
    
    def get_download_links(self) -> dict:
        base_url = f"https://downloader.cursor.sh/builds/{self.build_id}"
        return {
            "windows": {
                "x64": f"{base_url}/windows/nsis/x64",
                "arm64": f"{base_url}/windows/nsis/arm64"
            },
            "mac": {
                "universal": f"{base_url}/mac/installer/universal",
                "arm64": f"{base_url}/mac/installer/arm64",
                "x64": f"{base_url}/mac/installer/x64"
            },
            "linux": {
                "x64": f"{base_url}/linux/appImage/x64"
            }
        }

def parse_versions(data: str) -> List[CursorVersion]:
    versions = []
    for line in data.strip().split('\n'):
        if not line:
            continue
        version, build_id = line.strip().split(',')
        versions.append(CursorVersion(version, build_id))
    return versions

def generate_markdown(versions: List[CursorVersion]) -> str:
    md = """# 🖥️ Windows

## x64
<details>
<summary style="font-size:1.2em">📦 Windows x64 安装包</summary>

| 版本 | 下载链接 |
|------|----------|
"""
    
    # Windows x64
    for version in versions:
        links = version.get_download_links()
        md += f"| {version.version} | [下载]({links['windows']['x64']}) |\n"
    
    md += """
</details>

## ARM64 
<details>
<summary style="font-size:1.2em">📱 Windows ARM64 安装包</summary>

| 版本 | 下载链接 |
|------|----------|
"""
    
    # Windows ARM64
    for version in versions:
        links = version.get_download_links()
        md += f"| {version.version} | [下载]({links['windows']['arm64']}) |\n"
    
    md += """
</details>

# 🍎 macOS

## Universal
<details>
<summary style="font-size:1.2em">🎯 macOS Universal 安装包</summary>

| 版本 | 下载链接 |
|------|----------|
"""
    
    # macOS Universal
    for version in versions:
        links = version.get_download_links()
        md += f"| {version.version} | [下载]({links['mac']['universal']}) |\n"
    
    md += """
</details>

## ARM64
<details>
<summary style="font-size:1.2em">💪 macOS ARM64 安装包</summary>

| 版本 | 下载链接 |
|------|----------|
"""
    
    # macOS ARM64
    for version in versions:
        links = version.get_download_links()
        md += f"| {version.version} | [下载]({links['mac']['arm64']}) |\n"
    
    md += """
</details>

## Intel
<details>
<summary style="font-size:1.2em">💻 macOS Intel 安装包</summary>

| 版本 | 下载链接 |
|------|----------|
"""
    
    # macOS Intel
    for version in versions:
        links = version.get_download_links()
        md += f"| {version.version} | [下载]({links['mac']['x64']}) |\n"
    
    md += """
</details>

# 🐧 Linux

## x64
<details>
<summary style="font-size:1.2em">🎮 Linux x64 AppImage</summary>

| 版本 | 下载链接 |
|------|----------|
"""
    
    # Linux x64
    for version in versions:
        links = version.get_download_links()
        md += f"| {version.version} | [下载]({links['linux']['x64']}) |\n"
    
    md += """
</details>

<style>
details {
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f8f9fa;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

summary {
    cursor: pointer;
    font-weight: bold;
    margin: -0.5em -1em;
    padding: 0.5em 1em;
}

summary:hover {
    background: #f1f3f5;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1em;
}

th, td {
    padding: 0.5em;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

tr:hover {
    background: #f1f3f5;
}

a {
    color: #0366d6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}
</style>
"""
    return md

def main():
    # 示例数据
    data = """
0.45.11,250207y6nbaw5qc
0.45.10,250205buadkzpea
0.45.9,250202tgstl42dt
0.45.8,250201b44xw1x2k
0.45.7,250130nr6eorv84
0.45.6,25013021lv9say3
0.45.5,250128loaeyulq8
0.45.4,250126vgr3vztvj
0.45.3,250124b0rcj0qql
0.45.2,250123mhituoa6o
0.45.1,2501213ljml5byg
0.45.0,250120dh9ezx9pg
0.44.11,250103fqxdt5u9z
0.44.10,250102ys80vtnud
0.44.9,2412268nc6pfzgo
0.44.8,241222ooktny8mh
0.44.7,2412219nhracv01
0.44.6,2412214pmryneua
0.44.5,241220s3ux0e1tv
0.44.4,241219117fcvexy
0.44.3,241218sybfbogmq
0.44.2,241218ntls52u8v
0.44.0,2412187f9v0nffu
0.43.6,241206z7j6me2e2
0.43.5,241127pdg4cnbu2
0.43.4,241126w13goyvrs
0.43.3,2411246yqzx1jmm
0.43.1,241124gsiwb66nc
0.42.5,24111460bf2loz1
0.42.4,2410291z3bdg1dy
0.42.3,241016kxu9umuir
0.42.2,2410127mj66lvaq
0.42.1,241011i66p9fuvm
0.42.0,241009fij7nohn5
0.41.3,240925fkhcqg263
0.41.2,240921llnho65ov
0.41.1,2409189xe3envg5
0.40.4,2409052yfcjagw2
0.40.3,240829epqamqp7h
0.40.2,240828c021k3aib
0.40.1,2408245thnycuzj
0.40.0,24082202sreugb2
0.39.6,240819ih4ta2fye
0.39.5,240814y9rhzmu7h
0.39.4,240810elmeg3seq
0.39.3,2408092hoyaxt9m
0.39.2,240808phaxh4b5r
0.39.1,240807g919tr4ly
0.39.0,240802cdixtv9a6
0.38.1,240725f0ti25os7
0.38.0,240723790oxe4a2
0.37.1,240714yrr3gmv3k
0.36.2,2407077n6pzboby
0.36.1,240706uekt2eaft
0.36.0,240703xqkjv5aqa
0.35.1,240621pc2f7rl8a
0.35.0,240608cv11mfsjl
0.34.6,240606kgzq24cfb
0.34.6,240605r495newcf
0.34.5,240602rq6xovt3a
0.34.4,2406014h0rgjghe
0.34.3,240529baisuyd2e
0.34.2,240528whh1qyo9h
0.34.1,24052838ygfselt
0.34.0,240527xus72jmkj
0.33.4,240511kb8wt1tms
0.33.3,2405103lx8342ta
0.33.2,240510dwmw395qe
0.33.1,2405039a9h2fqc9
0.33.0,240503hyjsnhazo
0.32.8,240428d499o6zja
0.32.7,240427w5guozr0l
0.32.2,240417ab4wag7sx
0.32.1,2404152czor73fk
0.32.0,240412ugli06ue0
0.31.3,240402rq154jw46
0.31.1,240402pkwfm2ps6
0.31.0,2404018j7z0xv2g
0.30.5,240327tmd2ozdc7
0.30.4,240325dezy8ziab
0.30.3,2403229gtuhto9g
0.30.2,240322gzqjm3p0d
0.30.1,2403212w1ejubt8
0.30.0,240320tpx86e7hk
0.29.1,2403027twmz0d1t
0.29.0,240301kpqvacw2h
0.28.1,240226tstim4evd
0.28.0,240224g2d7jazcq
0.27.4,240219qdbagglqz
0.27.3,240218dxhc6y8os
0.27.2,240216kkzl9nhxi
0.27.1,240215l4ooehnyl
0.27.0,240215at6ewkd59
0.26.2,240212o6r9qxtcg
0.26.1,2402107t904hing
0.26.0,240210k8is5xr6v
0.25.3,240207aacboj1k8
0.25.2,240206p3708uc9z
0.25.1,2402033t030rprh
0.25.0,240203kh86t91q8
0.24.4,240129iecm3e33w
0.24.3,2401289dx79qsc0
0.24.1,240127cad17436d
0.24.0,240126wp9irhmza
0.23.9,240124dsmraeml3
0.23.8,240123fnn1hj1fg
0.23.7,240123xsfe7ywcv
0.23.6,240121m1740elox
0.23.5,2401215utj6tx6q
0.23.4,240121f4qy6ba2y
0.23.3,2401201und3ytom
0.23.2,240120an2k2hf1i
0.23.1,240119fgzxwudn9
0.22.2,24011721vsch1l1
0.22.1,2401083eyk8kmzc
0.22.0,240107qk62kvva3
0.21.1,231230h0vi6srww
0.21.0,231229ezidnxiu3
0.20.2,231219aksf83aad
0.20.1,231218ywfaxax09
0.20.0,231216nsyfew5j1
0.19.1,2312156z2ric57n
0.19.0,231214per9qal2p
0.18.8,2312098ffjr3ign
0.18.7,23120880aolip2i
0.18.6,231207ueqazwde8
0.18.5,231206jzy2n2sbi
0.18.4,2312033zjv5fqai
0.18.3,231203k2vnkxq2m
0.18.1,23120176kaer07t
0.17.0,231127p7iyxn8rg
0.16.0,231116rek2xuq6a
0.15.5,231115a5mv63u9f
0.15.4,23111469e1i3xyi
0.15.3,231113b0yv3uqem
0.15.2,231113ah0kuf3pf
0.15.1,231111yanyyovap
0.15.0,231110mdkomczmw
0.14.1,231109xitrgihlk
0.14.0,231102m6tuamwbx
0.13.4,231029rso7pso8l
0.13.3,231025uihnjkh9v
0.13.2,231024w4iv7xlm6
0.13.1,231022f3j0ubckv
0.13.0,231022ptw6i4j42
0.12.3,231008c5ursm0oj"""
    
    versions = parse_versions(data)
    
    # 生成 Markdown 文件
    markdown_content = generate_markdown(versions)
    with open('Cursor历史.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # 创建结果数据结构
    result = {
        "versions": []
    }
    
    # 处理每个版本
    for version in versions:
        version_info = {
            "version": version.version,
            "build_id": version.build_id,
            "downloads": version.get_download_links()
        }
        result["versions"].append(version_info)
    
    # 保存为JSON文件
    with open('cursor_downloads.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # 同时生成CSV格式的下载链接
    with open('cursor_downloads.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Version', 'Platform', 'Architecture', 'Download URL'])
        
        for version in versions:
            links = version.get_download_links()
            for platform, archs in links.items():
                for arch, url in archs.items():
                    writer.writerow([version.version, platform, arch, url])

if __name__ == "__main__":
    main() 