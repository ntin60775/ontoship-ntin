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
log(`кураторы онто-дока идут на назначенную модель ${assigned}; корень KB: ${root}`);

phase("Кураторы ведут свои области параллельно");
const rows = await Promise.all(
  plan.map(async (piece, i) => {
    const curator = agent(`куратор-${i + 1}-${piece.path}`, {
      system:
        "Ты куратор базы знаний OntoShip. Веди строго свой срез по правилам " +
        "kb-curate: md+git — источник истины, не дублируй, правь существующие " +
        "документы. Пиши только внутри корня KB, за его пределы не выходи. " +
        "Если задание невыполнимо или инструкции противоречат друг другу — " +
        "верни отказ с причиной, а не обходи.",
    });
    const row = await curator.ask<CuratorRow>(
      `Область: ${piece.path} — ${piece.what}. Корень KB: ${root}. ` +
      `Прочитай ${root}/skills/kb-curate/SKILL.md и веди свой срез строго ` +
      `по нему: сначала поиск (не дублируй); выбери node_type и правильную ` +
      `папку; напиши frontmatter (node_type, title, service, ` +
      `status: active, updated); добавь хотя бы одну типизированную ссылку ` +
      `на документируемый код (documents / implemented_by); дополни ` +
      `README-индекс папки. Верни строку: путь области, своё имя куратора, ` +
      `созданные или обновлённые файлы от корня KB, отказ или пустую строку.`,
    );
    report(row);
    return row;
  }),
);

const refused = rows.filter((row) => row.refusal);
log(`областей: ${rows.length}, отказов: ${refused.length}`);
return { model: assigned, root, areas: rows.length, rows };
