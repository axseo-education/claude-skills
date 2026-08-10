#!/bin/bash
# CCFM 교육용 스킬 설치
#
#   bash install.sh
#
# 설치 후 Claude Code 를 다시 켜고 / 를 누르면 목록에 나타납니다.

set -e
DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "")"

# curl | bash 로 실행되면 스크립트 옆에 education 이 없다. 그때는 ZIP 을 받아 쓴다 (git 불필요).
if [ -z "$DIR" ] || [ ! -d "$DIR/education" ]; then
  TMP="$(mktemp -d)"
  echo "스킬을 내려받는 중..."
  curl -fsSL https://github.com/axseo-education/claude-skills/archive/refs/heads/master.zip -o "$TMP/repo.zip"
  ( cd "$TMP" && unzip -q repo.zip )
  DIR="$TMP/claude-skills-master"
  trap 'rm -rf "$TMP"' EXIT
fi

# 안전장치 — 이 스킬들의 원본을 만드는 기기에서는 실행하지 않는다.
# 교육판이 원본을 덮어쓰면 되돌릴 수 없다.
if [ -f "$HOME/scripts/export-skills.sh" ] || [ -d "$DIR/overrides" ]; then
  if [ "${I_KNOW_WHAT_IM_DOING:-}" != "1" ]; then
    echo "여기는 스킬 원본을 관리하는 기기로 보입니다."
    echo "설치하면 ~/.claude/skills/ 의 원본이 교육판으로 덮어써집니다."
    echo
    echo "정말 설치하려면:  I_KNOW_WHAT_IM_DOING=1 bash install.sh"
    exit 1
  fi
fi

mkdir -p ~/.claude/skills ~/.claude/commands
BACKUP="$HOME/.claude/skills-backup-$(date +%Y%m%d-%H%M%S)"

echo "CCFM 스킬을 설치합니다."
echo

n=0
for d in "$DIR"/education/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  if [ -d "$HOME/.claude/skills/$name" ]; then
    mkdir -p "$BACKUP"
    mv "$HOME/.claude/skills/$name" "$BACKUP/$name"
  fi
  cp -R "$d" "$HOME/.claude/skills/$name"
  echo "  /$name"
  n=$((n+1))
done

for f in "$DIR"/education/*.md; do
  [ -e "$f" ] || continue
  name="$(basename "$f" .md)"
  if [ -f "$HOME/.claude/commands/$name.md" ]; then
    mkdir -p "$BACKUP"
    mv "$HOME/.claude/commands/$name.md" "$BACKUP/$name.md"
  fi
  cp "$f" "$HOME/.claude/commands/$name.md"
  echo "  /$name"
  n=$((n+1))
done

echo
echo "설치 완료 — ${n}개."
[ -d "$BACKUP" ] && echo "기존 파일은 $BACKUP 에 옮겨 뒀습니다."
echo "Claude Code 를 다시 켜고 / 를 눌러 확인하세요."
