import {test} from "node:test";
import assert from "node:assert/strict";
import {encodeBytes, decodeBytes} from "./codec.mjs";

for (const length of [0, 1, 2, 39, 213, 253, 254, 500, 1024, 4096]) {
  test("binary/DNA round-trip " + length + " bytes", async () => {
    const bytes = Uint8Array.from({length}, (_, i) => i % 256);
    const dna = await encodeBytes(bytes);
    const {bytes: got, correctedBytes} = await decodeBytes(dna);
    assert.deepEqual(got, bytes);
    assert.equal(correctedBytes, 0);
    assert.match(dna, /^[ACGT]+$/);
    assert.equal(dna.length % 8, 0);
    assert.equal((dna.match(/[GC]/g) || []).length * 2, dna.length);
    assert.doesNotMatch(dna, /A{3}|C{3}|G{3}|T{3}/);
  });
}
test("one byte can be corrected", async () => {
  const original = Uint8Array.from({length: 600}, (_, i) => i % 256);
  const dna = await encodeBytes(original);
  // Corrupt one complete 8-nt codeword in each of the first two blocks.
  let corrupt = dna.split("");
  for (const position of [0, 280]) {
    const start = position * 8;
    const candidate = dna.slice(start, start + 8) === "ACACACAC" ? "TGTGTGTG" : "ACACACAC";
    corrupt.splice(start, 8, ...candidate.split(""));
  }
  const decoded = await decodeBytes(corrupt.join(""));
  assert.deepEqual(decoded.bytes, original);
  assert.equal(decoded.correctedBytes, 2);
});
test("rejects malformed or uncorrectable DNA", async () => {
  await assert.rejects(decodeBytes(""), /empty/i);
  await assert.rejects(decodeBytes("ACGT"), /multiple of eight/);
  await assert.rejects(decodeBytes("AAAAAAAA"), /dinucleotide/);
  const dna = await encodeBytes(new TextEncoder().encode("abcdefghijklmnop"));
  const bad = "TGTGTGTG" + "CACACACA" + dna.slice(16);
  await assert.rejects(decodeBytes(bad));
});
