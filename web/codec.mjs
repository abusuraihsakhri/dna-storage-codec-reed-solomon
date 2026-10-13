/** Portable DNA codec matching dna_storage_codec/codec.py.
 * Version DSR1, RS(255,253), two parity bytes, one-byte correction/block.
 * No network or backend is required. Not a fountain code.
 */
const PAIRS = ["AC", "CA", "GT", "TG"];
const REVERSE = new Map(PAIRS.map((p, i) => [p, i]));
const MAX_BYTES = 16 * 1024 * 1024;
const EXP = new Uint8Array(512);
const LOG = new Uint8Array(256);
let value = 1;
for (let i = 0; i < 255; i++) {
  EXP[i] = value; LOG[value] = i;
  value <<= 1;
  if (value & 256) value ^= 0x11d;
}
for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
const mul = (a, b) => a && b ? EXP[LOG[a] + LOG[b]] : 0;

function syndrome(data) {
  let s0 = 0, s1 = 0;
  for (const b of data) { s0 ^= b; s1 = mul(s1, 2) ^ b; }
  return [s0, s1];
}

function encodeBlock(data) {
  const work = new Uint8Array(data.length + 2);
  work.set(data);
  for (let i = 0; i < data.length; i++) {
    const v = work[i];
    if (v) { work[i + 1] ^= mul(v, 3); work[i + 2] ^= mul(v, 2); }
  }
  const result = new Uint8Array(data.length + 2);
  result.set(data); result.set(work.subarray(data.length), data.length);
  return result;
}

function decodeBlock(block) {
  if (block.length < 3 || block.length > 255) throw Error("Invalid Reed–Solomon block size");
  const data = new Uint8Array(block);
  let [s0, s1] = syndrome(data);
  if (!s0 && !s1) return [data.subarray(0, -2), false];
  if (!s0 || !s1) throw Error("Uncorrectable Reed–Solomon block");
  const exponent = (LOG[s1] - LOG[s0] + 255) % 255;
  const index = data.length - 1 - exponent;
  if (index < 0 || index >= data.length) throw Error("Uncorrectable Reed–Solomon block");
  data[index] ^= s0;
  if (syndrome(data).some(n => n !== 0)) throw Error("Uncorrectable Reed–Solomon block");
  return [data.subarray(0, -2), true];
}

function dnaToBytes(text) {
  if (typeof text !== "string") throw TypeError("DNA sequence must be text");
  const seq = text.replace(/\s/g, "").toUpperCase();
  if (seq.length % 8) throw Error("DNA length must be a multiple of eight");
  if (seq.length > (MAX_BYTES + 40 + 2 * Math.ceil((MAX_BYTES + 40) / 253)) * 8)
    throw Error("DNA sequence exceeds 16 MiB limit");
  const bytes = new Uint8Array(seq.length / 8);
  for (let i = 0; i < bytes.length; i++) {
    let byte = 0;
    for (let j = 0; j < 4; j++) {
      const symbol = REVERSE.get(seq.slice(i * 8 + j * 2, i * 8 + j * 2 + 2));
      if (symbol === undefined) throw Error("Invalid dinucleotide at position " + (i * 8 + j * 2 + 1));
      byte = (byte << 2) | symbol;
    }
    bytes[i] = byte;
  }
  return bytes;
}

function bytesToDna(data) {
  const dna = [];
  for (const b of data) for (const shift of [6, 4, 2, 0]) dna.push(PAIRS[(b >>> shift) & 3]);
  return dna.join("");
}

async function sha256(bytes) {
  if (!globalThis.crypto?.subtle) throw Error("SHA-256 requires a secure browser context (HTTPS or localhost)");
  return new Uint8Array(await globalThis.crypto.subtle.digest("SHA-256", bytes));
}

export async function encodeBytes(input) {
  if (!(input instanceof Uint8Array)) throw TypeError("Input must be Uint8Array");
  if (input.length > MAX_BYTES) throw Error("File exceeds 16 MiB limit");
  const digest = await sha256(input);
  const frame = new Uint8Array(40 + input.length);
  frame.set([68, 83, 82, 49]); // DSR1
  new DataView(frame.buffer).setUint32(4, input.length, false);
  frame.set(digest, 8); frame.set(input, 40);
  const blocks = [];
  for (let i = 0; i < frame.length; i += 253) blocks.push(encodeBlock(frame.subarray(i, i + 253)));
  return blocks.map(bytesToDna).join("");
}

export async function decodeBytes(sequence) {
  const protectedBytes = dnaToBytes(sequence);
  if (!protectedBytes.length) throw Error("DNA sequence cannot be empty");
  const blocks = [], count = Math.ceil(protectedBytes.length / 255);
  let corrected = 0, total = 0;
  for (let i = 0; i < protectedBytes.length; i += 255) {
    const [data, fixed] = decodeBlock(protectedBytes.subarray(i, i + 255));
    blocks.push(data); total += data.length; corrected += Number(fixed);
  }
  const frame = new Uint8Array(total);
  let offset = 0;
  for (const block of blocks) { frame.set(block, offset); offset += block.length; }
  if (frame.length < 40 || String.fromCharCode(...frame.subarray(0, 4)) !== "DSR1")
    throw Error("Invalid DNA storage frame");
  const length = new DataView(frame.buffer).getUint32(4, false);
  if (length > MAX_BYTES || length !== frame.length - 40) throw Error("Payload size mismatch");
  const payload = frame.slice(40);
  const actual = await sha256(payload);
  let mismatch = 0;
  for (let i = 0; i < 32; i++) mismatch |= actual[i] ^ frame[8 + i];
  if (mismatch) throw Error("SHA-256 integrity check failed");
  return {bytes: payload, correctedBytes: corrected, blocks: count};
}
