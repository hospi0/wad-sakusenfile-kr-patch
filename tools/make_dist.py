# -*- coding: utf-8 -*-
r"""강철의 전풍·작전파일 배포 묶음(게임별) — dist/<이름>_<VER>/ : 트랙 1 xdelta + xdelta.exe + readme.txt(CP949) + 한글패치_적용.bat(CP949) + zip
  에어즈 어드벤처 tools/make_dist.py 를 옮김. 바뀌는 트랙: 트랙 1 만(트랙 2·cue 그대로).
  검증: 원본 트랙 1 → xdelta 적용 → md5 = 빌드 트랙 1 md5.  python tools/make_dist.py   (먼저 build.py·build_f.py --write)"""
import glob, hashlib, os, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
VER = 'v0.9'
XDELTA = r'C:\claude\utils\xdelta.exe'
B = os.path.join('C:' + os.sep, 'claude', 'roms', 'ss', 'World Advanced Daisenryaku')
GAMES = [
    dict(rom='World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)', out='work/disc', name='WAD_Koutetsu_KR_' + VER,
         title='월드 어드밴스드 대전략 강철의 전풍 (세가 새턴 일본판 Rev A) 한글 패치 ' + VER,
         change="""  - 시나리오 54개 브리핑·승리 조건 문장
  - 메뉴·메시지·턴 시작·이벤트·저장 화면·설정 화면 글자
  - 무기·지형 이름(작은 글자는 한글), 유닛·나라·거점·작전 이름(작은 글자는 영문)
  - 큰 유닛 이름, 맵 이름, 지구본 연표
  - 그림 글자: 타이틀 띠, 작전 버튼, 상황 표, 유닛 정보, 설정 버튼, 지도 지명 52장, 엔딩 19종, 자료 제공 화면""",
         note="""  - 표시 칸이 좁아 작은 글자의 고유 이름은 영문으로 넣었습니다.
  - 대전략 로고(큰 한자)와 동영상은 원본 그대로입니다.
  - 스태프 롤은 원본 그대로입니다."""),
    dict(rom='World Advanced Daisenryaku - Sakusen File (Japan) (2M)', out='work/disc_f', name='WAD_SakusenFile_KR_' + VER,
         title='월드 어드밴스드 대전략 작전 파일 (세가 새턴 일본판) 한글 패치 ' + VER,
         change="""  - 시나리오 41개 브리핑·승리 조건 문장, 캠페인 이야기
  - 메뉴·메시지·턴 시작·이벤트·저장 화면·설정 화면 글자, 턴 화면 나라·부대 이름
  - 무기·지형 이름(작은 글자는 한글), 유닛·나라·거점 이름(작은 글자는 영문)
  - 큰 유닛 이름, 시나리오 제목·설명, 지구본 연표, 엔딩 글
  - 그림 글자: 타이틀 띠, 작전 버튼, 병기 타입 메뉴, 상황 표, 유닛 정보, 설정 버튼, 지도 지명 15장, 자료 제공 화면""",
         note="""  - 표시 칸이 좁아 작은 글자의 고유 이름은 영문으로, 시나리오 설명 일부는 줄여서 넣었습니다.
  - 대전략 로고(큰 한자)와 동영상은 원본 그대로입니다."""),
]
README = """{title}
{line}

2개의 트랙으로 이루어진 {rom} 의
트랙 1번(데이터)에 패치하시면 됩니다.

원본md5 : {o}
패치md5 : {d}

입니다.


[ 적용 방법 ]

  1) 원본 트랙 1 파일을 이 폴더에 복사
       "{bin}"
  2) 한글패치_적용.bat 실행 → 이름 끝에 [KR] 이 붙은 파일이 만들어집니다
  3) 만든 파일 이름을 원본 트랙 1 이름으로 바꿔 넣고, 트랙 2(오디오)와 cue 는 원본 그대로 쓰세요

  직접 적용:
    xdelta.exe -d -s "원본 트랙 1" "{patch}" "결과 파일"
  (Delta Patcher 같은 xdelta3 GUI 도구로 적용해도 됩니다. 원본이 다르면 xdelta 가 적용을 거부합니다.)


[ 바뀌는 것 ]

{change}


[ 알려진 점 ]

  - 시험판입니다. 전체 플레이 검증을 마치지 않았습니다.
{note}
  - 패치 전 세이브와 세이브스테이트는 쓰지 마세요. 새 게임으로 시작해 주세요.
"""
BAT = r"""@echo off
chcp 949 >nul
set "XD=%~dp0xdelta.exe"
if not exist "%~dp0{bin}" (
  echo   [오류] 원본 트랙 1 파일을 이 폴더에 넣어 주세요 - readme 참고.
  pause & exit /b 1
)
"%XD%" -d -f -s "%~dp0{bin}" "%~dp0{patch}" "%~dp0{kbin}"
if errorlevel 1 (
  echo   [오류] 패치 실패 - 원본이 다를 수 있습니다 - readme 의 원본md5 확인.
  pause & exit /b 1
)
echo   완료: "{kbin}"
pause
"""


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''): h.update(b)
    return h.hexdigest().upper()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for g in GAMES:
        NAME = g['name']; ROM = g['rom']; d = os.path.join(ROOT, 'dist', NAME); os.makedirs(d, exist_ok=True)
        b = '%s (Track 1).bin' % ROM; src = os.path.join(B, ROM, b); out = os.path.join(ROOT, g['out'], b)
        patch = NAME + '_Track1.xdelta'; pp = os.path.join(d, patch)
        subprocess.run([XDELTA, '-e', '-9', '-B', '536870912', '-f', '-s', src, out, pp], check=True)
        chk = os.path.join(d, '_check.bin')
        subprocess.run([XDELTA, '-d', '-f', '-s', src, pp, chk], check=True)
        o, want, got = md5(src), md5(out), md5(chk)
        os.remove(chk)
        assert got == want, ('패치 적용 결과가 빌드와 다름', got, want)
        shutil.copy2(XDELTA, os.path.join(d, 'xdelta.exe'))
        kbin = '%s (Track 1) [KR].bin' % ROM
        readme = README.format(title=g['title'], line='=' * 60, rom=ROM, o=o, d=want, bin=b, patch=patch, change=g['change'], note=g['note'])
        open(os.path.join(d, 'readme.txt'), 'wb').write(readme.replace('\n', '\r\n').encode('cp949'))
        open(os.path.join(d, '한글패치_적용.bat'), 'wb').write(BAT.format(bin=b, patch=patch, kbin=kbin).replace('\n', '\r\n').encode('cp949'))
        z = os.path.join(ROOT, 'dist', NAME + '.zip')
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(os.listdir(d)): zf.write(os.path.join(d, f), NAME + '/' + f)
        print('✅', NAME, '원본md5', o, '패치md5', want)
        for f in sorted(os.listdir(d)): print('  %-58s %12d' % (f, os.path.getsize(os.path.join(d, f))))
        print('  zip %d B md5 %s' % (os.path.getsize(z), md5(z)))


if __name__ == '__main__':
    main()
