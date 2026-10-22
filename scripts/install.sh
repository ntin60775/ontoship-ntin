#!/usr/bin/env bash
# OntoShip core — project-local install.
#
# usage: scripts/install.sh [--dry-run] [--copy | --check] <project>
#
# The target layout is <project>/.agents/skills/<name>/SKILL.md — the project-local
# skill root shared by zcode, DSH and Qoder. The default install links the seven skill
# bundles to this repository; --copy makes a detached copy; --check verifies either
# form and names every missing or drifted skill. --dry-run prints the planned links and
# runs the same preflight checks without writing; planning a --copy install is not
# implemented yet. Legacy harness roots (.dsh, .zcode, .qoder) are reported as warnings
# and never written or deleted. The install is idempotent and writes only under
# <project>/.agents/skills. It links the skills; it does not run the init skill.

set -euo pipefail

readonly SKILLS=(kb-search kb-curate init grilling to-tickets ship testing)
readonly LEGACY_ROOTS=(.dsh .zcode .qoder)
readonly EXCLUDES=(-x __pycache__ -x '*.pyc')

here=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
readonly REPO=$(CDPATH= cd -- "$here/.." && pwd -P)

usage() {
  cat <<'EOF'
usage: scripts/install.sh [--dry-run] [--copy | --check] <project>

Install the OntoShip core into <project>/.agents/skills, the project-local skill root
shared by zcode, DSH and Qoder.

  (default)  symlink the seven skill bundles to this repository:
             kb-search, kb-curate, init, grilling, to-tickets, ship, testing
  --dry-run  print the planned links and run the same preflight checks without
             writing; cannot be combined with --check or --copy (yet)
  --copy     copy the skill directories instead (detached install)
  --check    verify the install; warn about legacy .dsh/.zcode/.qoder entries;
             exit 1 and name each missing or drifted skill

Idempotent; writes only <project>/.agents/skills; never runs the init skill.
EOF
}

die() {
  printf 'install: %s\n' "$*" >&2
  exit 1
}

usage_error() {
  printf 'install: %s\n' "$*" >&2
  usage >&2
  exit 2
}

mode=link
dry_run=0
project=
while (($# > 0)); do
  arg=$1
  shift
  case $arg in
    --dry-run)
      dry_run=1
      ;;
    --copy | --check)
      if [[ $mode != "link" && $mode != "${arg#--}" ]]; then
        usage_error "--copy and --check are mutually exclusive"
      fi
      mode=${arg#--}
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    --)
      (($# == 1)) || usage_error "-- expects exactly one <project>"
      project=$1
      shift
      ;;
    -*)
      usage_error "unknown option: $arg"
      ;;
    *)
      [[ -z $project ]] || usage_error "unexpected argument: $arg"
      project=$arg
      ;;
  esac
done

[[ -n $project ]] || usage_error "missing <project>"
[[ -d $project ]] || usage_error "not a project directory: $project"
if ((dry_run)); then
  [[ $mode != "check" ]] || usage_error "--dry-run and --check are mutually exclusive"
  [[ $mode != "copy" ]] || usage_error "--dry-run with --copy is not implemented"
fi
project=$(CDPATH= cd -- "$project" && pwd -P)
readonly dest=$project/.agents/skills

for tool in cp diff find ln mkdir readlink rm; do
  command -v "$tool" >/dev/null 2>&1 || die "required tool not found: $tool"
done

for name in "${SKILLS[@]}"; do
  [[ -f $REPO/skills/$name/SKILL.md ]] ||
    die "source skill missing: $REPO/skills/$name/SKILL.md"
done

# A correct link resolves to the source directory; a correct copy has the same files.
is_link_to() {
  local path=$1 src=$2 want
  [[ -L $path ]] || return 1
  want=$(readlink -f -- "$src") || return 1
  [[ $(readlink -f -- "$path" 2>/dev/null) == "$want" ]]
}

is_copy_of() {
  local path=$1 src=$2
  [[ -d $path && ! -L $path ]] || return 1
  diff -rq "${EXCLUDES[@]}" -- "$src" "$path" >/dev/null 2>&1
}

describe_entry() {
  local path=$1
  if [[ -L $path ]]; then
    printf 'wrong symlink -> %s' "$(readlink -- "$path" 2>/dev/null || printf '?')"
  elif [[ -d $path ]]; then
    printf 'directory differs from the source'
  elif [[ -e $path ]]; then
    printf 'not a directory'
  else
    printf 'missing'
  fi
}

# Legacy harness roots that still point into this repository are reported, never
# touched. DSH ranks .dsh/skills (100) above .agents/skills (200), so a stale entry
# shadows the universal install; the fix is the operator's, not the installer's.
legacy_warnings() {
  local root base name path
  for root in "${LEGACY_ROOTS[@]}"; do
    base=$project/$root/skills
    if is_link_to "$base" "$REPO/skills"; then
      if [[ $root == .dsh ]]; then
        printf 'warning: legacy .dsh/skills -> %s; DSH ranks .dsh/skills (100) above .agents/skills (200), so the old entry shadows the universal install — remove it manually\n' \
          "$(readlink -- "$base")" >&2
      else
        printf 'warning: legacy %s/skills -> %s — remove it manually\n' \
          "$root" "$(readlink -- "$base")" >&2
      fi
    fi
    [[ -d $base ]] || continue
    for name in "${SKILLS[@]}"; do
      path=$base/$name
      is_link_to "$path" "$REPO/skills/$name" || continue
      if [[ $root == .dsh ]]; then
        printf 'warning: legacy .dsh/skills/%s points into this repository; DSH ranks .dsh/skills (100) above .agents/skills (200), so the old entry shadows the universal install — remove it manually\n' \
          "$name" >&2
      else
        printf 'warning: legacy %s/skills/%s points into this repository — remove it manually\n' \
          "$root" "$name" >&2
      fi
    done
  done
}

check() {
  local drift=0 name path
  legacy_warnings
  for name in "${SKILLS[@]}"; do
    path=$dest/$name
    if is_link_to "$path" "$REPO/skills/$name"; then
      printf 'ok %s (link)\n' "$name"
    elif is_copy_of "$path" "$REPO/skills/$name"; then
      printf 'ok %s (copy)\n' "$name"
    else
      printf 'drift: %s: %s\n' "$name" "$(describe_entry "$path")" >&2
      drift=$((drift + 1))
    fi
  done
  if ((drift > 0)); then
    printf 'check: %d skill(s) drifted\n' "$drift" >&2
    return 1
  fi
  printf 'check: ok\n'
}

# Refuse the whole run rather than half-install or destroy a detached copy.
preflight_install() {
  local name path parent=$project/.agents
  # mkdir -p cannot repair a file or a dangling link on the way to the root.
  if [[ ( -e $parent || -L $parent ) && ! -d $parent ]]; then
    die "refusing to replace a non-directory: $parent"
  fi
  if [[ ( -e $dest || -L $dest ) && ! -d $dest ]]; then
    die "refusing to replace a non-directory: $dest"
  fi
  for name in "${SKILLS[@]}"; do
    path=$dest/$name
    if [[ $mode == copy ]]; then
      if [[ -L $path || ! -e $path ]]; then
        continue
      fi
      [[ -d $path ]] || die "refusing to replace a non-directory: $path"
      is_copy_of "$path" "$REPO/skills/$name" ||
        die "copy differs: $path (remove it to reinstall)"
    else
      if [[ -e $path && ! -L $path ]]; then
        die "refusing to replace a non-symlink: $path (remove it, or use --copy/--check)"
      fi
    fi
  done
}

install_links() {
  local name path src
  for name in "${SKILLS[@]}"; do
    path=$dest/$name
    src=$REPO/skills/$name
    if is_link_to "$path" "$src"; then
      printf 'unchanged %s\n' "$name"
      continue
    fi
    if [[ -L $path ]]; then
      rm -f -- "$path"
    fi
    ln -s -- "$src" "$path"
    printf 'linked %s -> %s\n' "$name" "$src"
  done
}

# Mirror install_links without touching the disk; the wording never claims a write.
plan_links() {
  local name path src
  [[ -d $dest ]] || printf 'would create %s\n' "$dest"
  for name in "${SKILLS[@]}"; do
    path=$dest/$name
    src=$REPO/skills/$name
    if is_link_to "$path" "$src"; then
      printf 'would leave %s unchanged\n' "$name"
    else
      printf 'would link %s -> %s\n' "$name" "$src"
    fi
  done
}

install_copies() {
  local name path src
  for name in "${SKILLS[@]}"; do
    path=$dest/$name
    src=$REPO/skills/$name
    if is_copy_of "$path" "$src"; then
      printf 'unchanged %s\n' "$name"
      continue
    fi
    if [[ -L $path ]]; then
      rm -f -- "$path"
    fi
    cp -a -- "$src" "$path"
    # A detached install carries sources, not this machine's bytecode.
    find "$path" -type d -name __pycache__ -prune -exec rm -rf -- {} +
    find "$path" -type f -name '*.pyc' -delete
    printf 'copied %s -> %s\n' "$name" "$path"
  done
}

case $mode in
  check)
    check
    ;;
  link)
    preflight_install
    if ((dry_run)); then
      plan_links
    else
      mkdir -p -- "$dest"
      install_links
    fi
    ;;
  copy)
    preflight_install
    mkdir -p -- "$dest"
    install_copies
    ;;
esac
