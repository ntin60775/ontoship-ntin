/**
 * Build the browser artifact: concatenate the factory shell, the runtime
 * locale dictionaries (locale/*.json without the plugin-manager meta), the
 * pure model, and the UI into client.js. No dependencies; node only.
 */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const read = name => readFile(join(root, name), 'utf8');

const [prefix, model, ui, suffix, en, ru] = await Promise.all([
  read('src/prefix.js'),
  read('src/model.js'),
  read('src/ui.js'),
  read('src/suffix.js'),
  read('locale/en.json').then(JSON.parse),
  read('locale/ru.json').then(JSON.parse),
]);

const runtimeDict = full => {
  const { meta, ...rest } = full;
  // The Client locale service looks up flat dot-keys ('tab.title'), while
  // the plugin-manager JSON nests its sections: flatten for runtime.
  const flatten = (obj, prefix = '') => Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix === '' ? key : `${prefix}.${key}`;
    return typeof value === 'object' && value !== null ? flatten(value, fullKey) : [[fullKey, value]];
  });
  return Object.fromEntries(flatten(rest));
};
const localeBlock = `    const LOCALE_EN = ${JSON.stringify(runtimeDict(en), null, 2).replace(/\n/g, '\n    ')};\n`
  + `    const LOCALE_RU = ${JSON.stringify(runtimeDict(ru), null, 2).replace(/\n/g, '\n    ')};\n`;

const artifact = [prefix, localeBlock, model, ui, suffix].join('\n');
await writeFile(join(root, 'client.js'), artifact, 'utf8');
console.log(`client.js written: ${artifact.length} bytes`);