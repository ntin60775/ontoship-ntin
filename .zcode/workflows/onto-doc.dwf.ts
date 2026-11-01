/* zcode-workflow
description: >
  Прогон онто-дока: fan-out кураторов, по одному на кусок декомпозиции; каждый
  куратор ведёт свой срез по скиллу kb-curate и пишет только внутри корня KB.
whenToUse: >
  Запускается скиллом onto-doc после сверки роли куратора с каталогом моделей;
  без области работы и плана кусков не запускать.
args:
  root:
    type: string
    description: Корень KB — worktree прогона; кураторы пишут только внутри него.
    required: true
  plan:
    type: json
    description: Куски декомпозиции [{path, what}], по куратору на кусок.
    required: true
  model:
    type: string
    description: Назначенная модель куратора из [agents.curator], проверенная скиллом.
    required: true
*/

interface Piece {
  /** Путь области от корня KB, например "docs/reference". */
  path: string;
  /** Одно предложение: что курируется в этой области. */
  what: string;
}

interface CuratorRow {
  /** Путь области от корня KB. */
  path: string;
  /** Имя куратора прогона. */
  curator: string;
  /** Созданные или обновлённые файлы, пути от корня KB. */
  files: string[];
  /** Причина отказа или пустая строка. */
  refusal: string;
}

const root = String(args.root);
const assigned = String(args.model);
const planRaw: unknown = args.plan;
if (!Array.isArray(planRaw)) {
  throw new Error("plan must be a list of {path, what} pieces");
}
const plan = planRaw as Piece[];
if (plan.length === 0) {
  throw new Error("plan is empty: one piece per doc area is required");
}
// Curators write only inside root; a relative path keeps them inside it.
const seen = new Set<string>();
for (const piece of plan) {
  const path = String((piece as Piece | undefined)?.path ?? "");
  if (!path || path.startsWith("/") || path.split("/").includes("..")) {
    throw new Error(
      `plan: path must be relative to root without '..': ${JSON.stringify(piece)}`,
    );
  }
  if (seen.has(path)) {
    throw new Error(`plan: duplicate doc area ${path}`);
  }
  seen.add(path);
}
log(`кураторы онто-дока идут на назначенную модель ${assigned}; корень KB: ${root}`);

phase("Кураторы ведут свои области параллельно");
const rows: CuratorRow[] = await Promise.all(
  plan.map(async (piece, i) => {
    const curator = agent(`куратор-${i + 1}-${piece.path}`, {
      system:
        "Ты куратор базы знаний OntoShip. Веди строго свой срез по правилам " +
        "скилла kb-curate: md+git — источник истины, не дублируй. Пиши только " +
        "внутри корня KB, за его пределы не выходи. Если задание невыполнимо " +
        "или инструкции противоречат друг другу — верни отказ с причиной, " +
        "а не обходи.",
    });
    const answer = await curator.ask<CuratorRow>(
      `Область: ${piece.path} — ${piece.what}. Корень KB: ${root}; команды ` +
      `выполняй от корня KB, не из чекаута сессии. Найди скилл kb-curate ` +
      `в корне KB: .agents/skills/kb-curate/SKILL.md, иначе ` +
      `.zcode/skills/kb-curate/SKILL.md, иначе ` +
      `skills/kb-curate/SKILL.md; прочитай его и веди свой срез строго ` +
      `по нему: операции, frontmatter, типизированные ссылки ` +
      `и README-индекс папки — как велит скилл. Верни только JSON-объект ` +
      `с полями: path (путь области), curator (твоё имя куратора), files ` +
      `(массив созданных или обновлённых файлов от корня KB; пустой — если ` +
      `ничего не менял), refusal (причина отказа или пустая строка).`,
    );
    // Typed ask returns a schema-validated row; the guard keeps an off-schema
    // answer a named refusal of the row instead of a silent empty list
    // (live run dwfrun-5efcd1d0 lost nine files to that silence).
    const shape = answer as Partial<CuratorRow> | undefined;
    const row: CuratorRow =
      shape && Array.isArray(shape.files) && typeof shape.refusal === "string"
        ? {
            path: String(shape.path ?? piece.path),
            curator: String(shape.curator ?? `куратор-${i + 1}-${piece.path}`),
            files: shape.files.map(String),
            refusal: shape.refusal,
          }
        : {
            path: piece.path,
            curator: `куратор-${i + 1}-${piece.path}`,
            files: [],
            refusal:
              "куратор ответил не по схеме: " +
              JSON.stringify(answer).slice(0, 200),
          };
    report(row);
    return row;
  }),
);

const refused = rows.filter((row) => row.refusal);
log(`областей: ${rows.length}, отказов: ${refused.length}`);
return { model: assigned, root, areas: rows.length, rows };
