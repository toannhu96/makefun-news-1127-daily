// make.fun news-image-20261127 entry (Node 22, standard library only).
// Validates the committed entry.png (whole PNG, <= 1 MiB, <= 1024x1024), then writes it to
// /output/entry.png via a temporary file + rename so a failure never leaves partial output.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { readFileSync, writeFileSync, renameSync, rmSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const MAX_BYTES = 1024 * 1024;
const MAX_DIM = 1024;
const SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function fail(message: string): never {
  console.error(`entry check failed: ${message}`);
  process.exit(1);
}

// CRC-32 (PNG polynomial) so we can prove every chunk is intact.
const CRC_TABLE = new Uint32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (const b of buf) c = CRC_TABLE[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function validatePng(data: Buffer): { width: number; height: number } {
  if (data.length > MAX_BYTES) fail(`${data.length} bytes exceeds ${MAX_BYTES}`);
  if (data.length < 8 || !data.subarray(0, 8).equals(SIGNATURE)) fail('not a PNG (bad signature)');

  let pos = 8;
  let width = 0;
  let height = 0;
  let first = true;
  let sawIdat = false;
  let sawIend = false;
  while (pos < data.length) {
    if (sawIend) fail('data after IEND chunk');
    if (pos + 12 > data.length) fail('truncated chunk header');
    const len = data.readUInt32BE(pos);
    const type = data.toString('latin1', pos + 4, pos + 8);
    const end = pos + 12 + len;
    if (end > data.length) fail(`truncated ${type} chunk`);
    const crc = data.readUInt32BE(pos + 8 + len);
    if (crc32(data.subarray(pos + 4, pos + 8 + len)) !== crc) fail(`bad CRC in ${type} chunk`);
    if (first) {
      if (type !== 'IHDR' || len !== 13) fail('first chunk is not a valid IHDR');
      width = data.readUInt32BE(pos + 8);
      height = data.readUInt32BE(pos + 12);
      first = false;
    }
    if (type === 'IDAT') sawIdat = true;
    if (type === 'IEND') sawIend = true;
    pos = end;
  }
  if (!sawIdat) fail('no IDAT chunk');
  if (!sawIend) fail('missing IEND chunk (file is not whole)');
  if (width < 1 || height < 1) fail(`invalid dimensions ${width}x${height}`);
  if (width > MAX_DIM || height > MAX_DIM) fail(`${width}x${height} exceeds ${MAX_DIM}x${MAX_DIM}`);
  return { width, height };
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');
const temp = join(outDir, `.entry.png.${process.pid}.tmp`);

let data: Buffer;
try {
  data = readFileSync(new URL('./entry.png', import.meta.url));
} catch (e) {
  fail(`cannot read entry.png: ${(e as Error).message}`);
}

const { width, height } = validatePng(data);

try {
  mkdirSync(outDir, { recursive: true });
  writeFileSync(temp, data);
  renameSync(temp, target);
} catch (e) {
  rmSync(temp, { force: true });
  fail(`cannot write ${target}: ${(e as Error).message}`);
}
console.log(`wrote ${target} (${width}x${height}, ${data.length} bytes)`);
