#!/usr/bin/env bash
# OntoShip core — project-local install.
#
# usage: scripts/install.sh [--dry-run] [--copy | --check] <project>
#        scripts/install.sh [--dry-run] [--copy] --pack <source> <project>
#
# The target layout is <project>/.agents/skills/<name>/SKILL.md — the project-local
# skill root shared by zcode, DSH and Qoder. The default install links the skill
# bundles to this repository; --copy makes a detached copy; --check verifies either
# form, names every missing or drifted skill and validates installed standards
# packs. --dry-run prints the planned links or copies and runs the same preflight
# checks without writing. --pack <source> installs a standards pack into
# <project>/.agents/packs/<name> after the pack contract validator passes; the
# pack name comes from the manifest. Legacy harness roots
# (.dsh, .zcode, .qoder) and retired bundles (chain) are reported as warnings
# and never written or deleted. The install is idempotent and writes only under
# <project>/.agents (skills and packs). It links the skills; it does not run the
# init skill.

set -euo pipefail

readonly SKILLS=(kb-search kb-curate init grilling to-tickets ship testing critic onto-doc pack deliver)
readonly LEGACY_ROOTS=(.dsh .zcode .qoder)
# Bundles the core no longer ships. An old install may still carry one; like
# legacy roots, a retired entry is reported by --check and never touched.
readonly RETIRED_SKILLS=(chain)
# A copy is content, not this machine's bytecode and not VCS internals:
# neither is compared, nor does either stay in a fresh copy (issue #4).
readonly EXCLUDES=(-x __pycache__ -x '*.pyc' -x .git)

here=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
readonly REPO=$(CDPATH= cd -- "$here/.." && pwd -P)

usage() {
  cat <<'EOF'
usage: scripts/install.sh [--dry-run] [--copy | --check] <project>
       scripts/install.sh [--dry-run] [--copy] --pack <source> <project>

Install the OntoShip core into <project>/.agents/skills, the project-local skill root
shared by zcode, DSH and Qoder.

  (default)  symlink the skill bundles to this repository:
             kb-search, kb-curate, init, grilling, to-tickets, ship, testing,
             critic, onto-doc, pack, deliver
  --dry-run  print the planned links (or copies with --copy) and run the same
             preflight checks without writing; cannot be combined with --check
  --copy     copy the skill directories instead (detached install)
  --check    verify the install and validate installed packs; warn about legacy
             .dsh/.zcode/.qoder entries and retired bundles (chain); exit 1 and
             name each missing or drifted skill and each invalid pack
  --pack <source>
             install a standards pack into <project>/.agents/packs/<name>; the
             source must pass the pack contract validator, the name comes from
             the manifest; link/copy follows the mode; cannot be combined with
             --check

Idempotent; writes only under <project>/.agents (skills and packs); never runs
the init skill.
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
pack_source=
pack_requested=0
while (($# > 0)); do
  arg=$1
  shift
  case $arg in
    --dry-run)
      dry_run=1
      ;;
    --pack)
      (($# >= 1)) || usage_error "--pack expects a <source> directory"
      ((pack_requested == 0)) || usage_error "--pack given twice"
      [[ -n $1 ]] || usage_error "--pack expects a non-empty <source>"
      pack_source=$1
      pack_requested=1
      shift
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
fi
if [[ -n $pack_source && $mode == "check" ]]; then
  usage_error "--pack and --check are mutually exclusive"
fi
project=$(CDPATH= cd -- "$project" && pwd -P)
readonly dest=$project/.agents/skills
readonly packs_dest=$project/.agents/packs
readonly pack_validator=$REPO/skills/pack/validate_pack.py

# The pack channel validates the source before any write: a refused pack
# installs nothing. The name comes from the validated manifest; the
# contract requires it to equal the source directory name.
pack_name=
if ((pack_requested)); then
  command -v python3 >/dev/null 2>&1 || die "required tool not found: python3"
  [[ -f $pack_validator ]] || die "pack validator missing: $pack_validator"
  [[ -d $pack_source ]] || usage_error "not a pack directory: $pack_source"
  pack_source=$(CDPATH= cd -- "$pack_source" && pwd -P)
  if ! python3 "$pack_validator" "$pack_source" >/dev/null; then
    die "pack refused by contract: $pack_source"
  fi
  pack_name=$(python3 -c \
    'import json, sys; print(json.loads(open(sys.argv[1], encoding="utf-8").read())["name"])' \
    "$pack_source/manifest.json")
fi

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

# Retired bundles: the core stopped shipping them, but an old install may
# still carry one (a link now dangling, or a detached copy with local edits).
# The finding follows legacy_warnings: report, never delete — removal is the
# operator's decision.
retired_warnings() {
  local name path root
  for name in "${RETIRED_SKILLS[@]}"; do
    path=$dest/$name
    if [[ -e $path || -L $path ]]; then
      printf 'warning: %s выведен — удали вручную: %s\n' "$name" "$path" >&2
    fi
    # The legacy roots carried the retired bundle too; keep naming it there.
    for root in "${LEGACY_ROOTS[@]}"; do
      path=$project/$root/skills/$name
      [[ -e $path || -L $path ]] || continue
      printf 'warning: %s выведен — удали вручную: %s\n' "$name" "$path" >&2
    done
  done
}

check() {
  local drift=0 pack_drift=0 name path entry reason
  legacy_warnings
  retired_warnings
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
  # Installed packs are validated by the contract, not compared to a source:
  # a detached pack outlives its source repository. No packs dir — no packs.
  # A non-directory at the packs root is named, not silently skipped.
  if [[ -e $packs_dest || -L $packs_dest ]]; then
    if [[ ! -d $packs_dest ]]; then
      printf 'drift: packs: not a directory\n' >&2
      pack_drift=$((pack_drift + 1))
    else
      command -v python3 >/dev/null 2>&1 || die "required tool not found: python3"
      [[ -f $pack_validator ]] || die "pack validator missing: $pack_validator"
      for entry in "$packs_dest"/*; do
        [[ -e $entry || -L $entry ]] || continue
        name=$(basename -- "$entry")
        # Имя с ФС недоверено: управляющие символы заменяются маркером,
        # чтобы отчёт оставался построчным (идиома валидатора).
        safe_name=${name//[[:cntrl:]]/·}
        if [[ ! -d $entry ]]; then
          printf 'drift: pack %s: not a directory\n' "$safe_name" >&2
          pack_drift=$((pack_drift + 1))
          continue
        fi
        if reason=$(python3 "$pack_validator" "$entry" 2>&1 >/dev/null); then
          printf 'ok pack %s\n' "$safe_name"
        else
          printf 'drift: pack %s: %s\n' "$safe_name" "${reason#pack: }" >&2
          pack_drift=$((pack_drift + 1))
        fi
      done
    fi
  fi
  if ((drift > 0)); then
    printf 'check: %d skill(s) drifted\n' "$drift" >&2
  fi
  if ((pack_drift > 0)); then
    printf 'check: %d pack(s) drifted\n' "$pack_drift" >&2
  fi
  if ((drift > 0 || pack_drift > 0)); then
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

# Mirror install_copies without touching the disk; the wording never claims a write.
plan_copies() {
  local name path
  [[ -d $dest ]] || printf 'would create %s\n' "$dest"
  for name in "${SKILLS[@]}"; do
    path=$dest/$name
    if is_copy_of "$path" "$REPO/skills/$name"; then
      printf 'would leave %s unchanged\n' "$name"
    else
      printf 'would copy %s -> %s\n' "$name" "$path"
    fi
  done
}

# Pack channel: one validated pack per run, link or copy by mode. The
# preflight refuses the whole run rather than half-install or destroy a
# detached copy — the same contour as the core channel.
preflight_pack() {
  local parent=$project/.agents target=$packs_dest/$pack_name
  if [[ ( -e $parent || -L $parent ) && ! -d $parent ]]; then
    die "refusing to replace a non-directory: $parent"
  fi
  if [[ ( -e $packs_dest || -L $packs_dest ) && ! -d $packs_dest ]]; then
    die "refusing to replace a non-directory: $packs_dest"
  fi
  if [[ $mode == copy ]]; then
    if [[ -L $target || ! -e $target ]]; then
      return 0
    fi
    [[ -d $target ]] || die "refusing to replace a non-directory: $target"
    is_copy_of "$target" "$pack_source" ||
      die "copy differs: $target (remove it to reinstall)"
  else
    if [[ -e $target && ! -L $target ]]; then
      die "refusing to replace a non-symlink: $target (remove it, or use --copy/--check)"
    fi
  fi
}

install_pack_link() {
  local target=$packs_dest/$pack_name
  if is_link_to "$target" "$pack_source"; then
    printf 'unchanged pack %s\n' "$pack_name"
    return 0
  fi
  if [[ -L $target ]]; then
    rm -f -- "$target"
  fi
  ln -s -- "$pack_source" "$target"
  printf 'linked pack %s -> %s\n' "$pack_name" "$pack_source"
}

install_pack_copy() {
  local target=$packs_dest/$pack_name
  if is_copy_of "$target" "$pack_source"; then
    printf 'unchanged pack %s\n' "$pack_name"
    return 0
  fi
  if [[ -L $target ]]; then
    rm -f -- "$target"
  fi
  cp -a -- "$pack_source" "$target"
  # The source's VCS internals never travel: a fresh copy is content only.
  find "$target" -name .git -prune -exec rm -rf -- {} +
  find "$target" -type d -name __pycache__ -prune -exec rm -rf -- {} +
  find "$target" -type f -name '*.pyc' -delete
  printf 'copied pack %s -> %s\n' "$pack_name" "$target"
}

# Mirror the pack install without touching the disk; the wording never
# claims a write.
plan_pack() {
  local target=$packs_dest/$pack_name
  [[ -d $packs_dest ]] || printf 'would create %s\n' "$packs_dest"
  if [[ $mode == copy ]]; then
    if is_copy_of "$target" "$pack_source"; then
      printf 'would leave pack %s unchanged\n' "$pack_name"
    else
      printf 'would copy pack %s -> %s\n' "$pack_name" "$target"
    fi
  else
    if is_link_to "$target" "$pack_source"; then
      printf 'would leave pack %s unchanged\n' "$pack_name"
    else
      printf 'would link pack %s -> %s\n' "$pack_name" "$pack_source"
    fi
  fi
}

case $mode in
  check)
    check
    ;;
  link | copy)
    if ((pack_requested)); then
      preflight_pack
      if ((dry_run)); then
        plan_pack
      else
        mkdir -p -- "$packs_dest"
        if [[ $mode == copy ]]; then
          install_pack_copy
        else
          install_pack_link
        fi
      fi
    else
      preflight_install
      if ((dry_run)); then
        if [[ $mode == copy ]]; then
          plan_copies
        else
          plan_links
        fi
      else
        mkdir -p -- "$dest"
        if [[ $mode == copy ]]; then
          install_copies
        else
          install_links
        fi
      fi
    fi
    ;;
esac
